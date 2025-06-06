from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv
import boto3
import uuid
from io import BytesIO
import requests
import pymysql
import json




# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Database configuration from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

# S3 Configuration from environment variables
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
S3_REGION = os.getenv("AWS_REGION")

# AWS S3 Setup from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# ✅ Use resource for high-level access (.Bucket())
s3_resource = boto3.resource(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# ✅ Keep client if needed elsewhere (e.g. presigned URLs)
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

client = genai.Client()



# --- helpers ---

def fetch_request_record(request_id):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT mindmap_json, slide_json, updated_at FROM slide_requests WHERE id = %s",
                (request_id,)
            )
            row = cursor.fetchone()
    finally:
        conn.close()
    return row  # (mindmap_json, slide_json, updated_at)


def update_slide_record(request_id, updated_slide_json):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE slide_requests
                   SET slide_json = %s
                     , updated_at = NOW()
                 WHERE id = %s
                """,
                (updated_slide_json, request_id)
            )
        conn.commit()
    finally:
        conn.close()




@app.route('/generate-image', methods=['POST'])
def generate_image_route():
    if not client:
        return jsonify({"error": "OpenAI client not initialized. Check API key and server logs."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400

    prompt = data['prompt']
    
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
          response_modalities=['TEXT', 'IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
      if part.text is not None:
        print(part.text)
      elif part.inline_data is not None:
        image = Image.open(BytesIO((part.inline_data.data)))
        image.save('gemini-native-image.png')
        image.show()
        # Save the image to S3
        image_name = f"{uuid.uuid4()}.png"
        image_path = f"images/{image_name}"
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        s3_client.upload_fileobj(image_bytes, S3_BUCKET_NAME, image_path)
        image_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{image_path}"
        return jsonify({"image_url": image_url}), 200
    return jsonify({"error": "No image generated"}), 500



# --- new endpoint ---

@app.route("/api/v1/slides/content/image", methods=["POST"])
def generate_image_for_slide_content():
    # 1. parse & validate
    data = request.get_json() or {}
    rid = data.get("request_id")
    sid = data.get("slide_id")
    cid = data.get("content_id")
    if not (rid and sid and cid):
        return jsonify({"error": "Missing one or more of: request_id, slide_id, content_id"}), 400

    # 2. fetch existing slide_json
    record = fetch_request_record(rid)
    if not record:
        return jsonify({"error": f"No record for request_id {rid}"}), 404

    _, slide_json_str, _ = record
    slide_doc = json.loads(slide_json_str)
    slides = slide_doc.get("slides", [])

    # 3. locate slide & content
    slide = next((s for s in slides if s.get("slide_id") == sid), None)
    if not slide:
        return jsonify({"error": f"Slide '{sid}' not found"}), 404

    content = next((c for c in slide.get("content", []) if c.get("id") == cid), None)
    if not content:
        return jsonify({"error": f"Content '{cid}' not found in slide '{sid}'"}), 404

    prompt = content.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt on that content block"}), 400

    # 4. generate image via Gemini
    resp = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
    )        # 5. extract & upload first image we find
    for part in resp.candidates[0].content.parts:
        if part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            key = f"images/{uuid.uuid4()}.png"
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            s3_client.upload_fileobj(buf, S3_BUCKET_NAME, key)
            new_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}"

            # 6. update the JSON in memory and persist it
            content["src"] = new_url
            content["is_image_created"] = True
            updated_json_str = json.dumps(slide_doc)
            update_slide_record(rid, updated_json_str)

            # 7. return just that updated block
            return jsonify({"data": content}), 200

    return jsonify({"error": "Gemini returned no image"}), 500



@app.route("/api/v1/slides/generate", methods=["GET"])
def generate_slides():
    try:
        request_id = request.args.get("id")
        record = fetch_request_record(request_id)
        if not record:
            return jsonify({"error": "No record found"}), 404

        mindmap_json, cached_slides, updated_at = record

        if cached_slides:
            return Response(
                json.dumps({
                    "cached": True,
                    "last_updated": updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else None,
                    "data": json.loads(cached_slides)
                }, indent=2),
                mimetype="application/json"
            )

        # Generate new slides from mind map
        # response_json = generate_prompt_templateSlide(mindmap_json)

        # Store in DB
        # store_slide_json(request_id, response_json)

        

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def generate_image_for_content(request_id, slide_id, content_id):
    """
    Generates an image for the given slide content based on its prompt,
    uploads the image to S3, updates the slide_json in DB, and returns the updated content block.
    """
    # 1. fetch existing record
    record = fetch_request_record(request_id)
    if not record:
        raise ValueError(f"No record for request_id {request_id}")

    mindmap_json, slide_json_str, _ = record
    slide_doc = json.loads(slide_json_str)

    # 2. locate slide
    slides = slide_doc.get("slides", [])
    slide = next((s for s in slides if s.get("slide_id") == slide_id), None)
    if not slide:
        raise ValueError(f"Slide '{slide_id}' not found")

    # 3. locate content
    content = next((c for c in slide.get("content", []) if c.get("id") == content_id), None)
    if not content:
        raise ValueError(f"Content '{content_id}' not found in slide '{slide_id}'")

    prompt = content.get("prompt")
    if not prompt:
        raise ValueError("No prompt found for content block")

    # 4. generate image via Gemini
    resp = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
    )

    # 5. upload first image found
    for part in resp.candidates[0].content.parts:
        if part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            key = f"images/{uuid.uuid4()}.png"
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            s3_client.upload_fileobj(buf, S3_BUCKET_NAME, key)
            new_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{key}"

            # 6. update JSON and persist
            content["src"] = new_url
            content["is_image_created"] = True
            updated_json = json.dumps(slide_doc)
            update_slide_record(request_id, updated_json)

            return content

    raise RuntimeError("Gemini did not return any image data")



def generate_all_images_for_presentation(request_id):
    """
    Generate images for all image content blocks in a presentation.
    This function runs in a background thread and logs all results to console.
    
    Args:
        request_id (str): The ID of the slide request to process
        
    Returns:
        dict: A dictionary containing the results of the image generation process
    """
    if not request_id:
        print("[ERROR] Missing request_id")
        return {"success": False, "error": "Missing request_id", "generated": 0, "skipped": 0, "errors": []}

    print(f"[INFO] Fetching record for request_id: {request_id}")
    record = fetch_request_record(request_id)
    if not record:
        print(f"[ERROR] No record found for request_id {request_id}")
        return {"success": False, "error": f"No record found for request_id {request_id}", "generated": 0, "skipped": 0, "errors": []}

    _, slide_json_str, _ = record
    slide_doc = json.loads(slide_json_str)
    slides = slide_doc.get("slides", [])

    generated_count = 0
    skipped_count = 0
    errors = []

    print(f"[INFO] Starting image generation for {len(slides)} slides...")

    for slide in slides:
        slide_id = slide.get("slide_id", "unknown")
        print(f"[INFO] Processing slide: {slide_id}")
        content_blocks = slide.get("content", [])

        for content in content_blocks:
            content_id = content.get("id", "unknown")
            content_type = content.get("type")

            if content_type == "image":
                prompt = content.get("prompt")
                is_image_created = content.get("is_image_created", False)

                if not prompt:
                    print(f"[INFO] Skipping {slide_id}/{content_id}: No prompt")
                    skipped_count += 1
                    continue

                if is_image_created:
                    print(f"[INFO] Skipping {slide_id}/{content_id}: Already created")
                    skipped_count += 1
                    continue

                try:
                    print(f"[INFO] Generating image for {slide_id}/{content_id} using Gemini...")
                    resp = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=prompt,
                        config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
                    )

                    image_uploaded = False

                    for part in resp.candidates[0].content.parts:
                        if part.inline_data:
                            print(f"[INFO] Image data received for {slide_id}/{content_id}. Preparing upload...")
                            img = Image.open(BytesIO(part.inline_data.data))
                            key = f"images/{uuid.uuid4()}.png"
                            buf = BytesIO()
                            img.save(buf, format="PNG")
                            buf.seek(0)

                            # Upload image to S3 (no ACLs)
                            s3_resource.Bucket(S3_BUCKET_NAME).upload_fileobj(
                                Fileobj=buf,
                                Key=key,
                                ExtraArgs={'ContentType': 'image/png'}
                            )

                            # Construct S3 public URL
                            image_url = f"https://s3.ap-south-1.amazonaws.com/{S3_BUCKET_NAME}/{key}"

                            print(f"[INFO] Image uploaded to S3: {image_url}")

                            # Update content block
                            content["src"] = image_url
                            content["is_image_created"] = True
                            # Update the global slide_doc dictionary and mark image as created
                            generated_count += 1
                            image_uploaded = True
                            break

                    if not image_uploaded:
                        err = f"No image data returned for {slide_id}/{content_id}"
                        print(f"[ERROR] {err}")
                        errors.append(err)

                except Exception as e:
                    err = f"Error generating image for {slide_id}/{content_id}: {str(e)}"
                    print(f"[ERROR] {err}")
                    errors.append(err)

    print("[INFO] Image generation process completed.")
    print(f"[INFO] Generated: {generated_count}, Skipped: {skipped_count}, Errors: {len(errors)}")

    # Save updated JSON if any new images were added
    if generated_count > 0:
        try:
            slide_doc = slide_doc  # Update global reference
            # Mark the entire presentation as having all images created
            slide_doc["is_image_created"] = True
            updated_json_str = json.dumps(slide_doc)
            print(f"[INFO] Updating database with new slide JSON...")
            update_slide_record(request_id, updated_json_str)
            print(f"[SUCCESS] Database updated successfully!")
        except Exception as e:
            err = f"Failed to update database: {str(e)}"
            print(f"[ERROR] {err}")
            return {
                "success": False, 
                "error": err, 
                "generated": generated_count, 
                "skipped": skipped_count, 
                "errors": errors
            }

    # Log final results
    print(f"[FINAL] Image generation completed!")
    print(f"[FINAL] Generated: {generated_count}, Skipped: {skipped_count}, Total Processed: {generated_count + skipped_count + len(errors)}")
    if errors:
        print(f"[FINAL] Errors encountered: {errors}")
    else:
        print(f"[FINAL] No errors encountered!")
    
    # Return success response with details
    return {
        "success": True,
        "message": "Image generation completed successfully",
        "generated": generated_count,
        "skipped": skipped_count,
        "total_processed": generated_count + skipped_count + len(errors),
        "errors": errors,
        "has_errors": len(errors) > 0
    }
    
    
if __name__ == '__main__':
    app.run(debug=True)