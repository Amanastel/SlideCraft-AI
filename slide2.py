from flask import Flask, request, Response, jsonify
from langchain.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
import logging
import re
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS
import configparser
from flask import Flask, request, jsonify, Response
import uuid
import json
import pymysql
import configparser
import pymysql
import json
import logging
import google.generativeai as genai
import base64
import boto3
from google.generativeai import GenerativeModel
from google.genai import types
from PIL import Image
from io import BytesIO
from slide_service import generate_image_for_content, generate_all_images_for_presentation
from baml_client.sync_client import b
from functools import lru_cache
import time
from threading import Thread


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

# AWS S3 Setup from environment variables
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_MEETINGS")
BASE_URL = os.getenv("AWS_S3_BASE_URL")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# S3 Configuration from environment variables
S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
S3_REGION = os.getenv("AWS_REGION")

# Initialize S3 client with environment variables
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Headers for SSE
# Enable CORS for all routes
CORS(app)  # 🔥 This allows all origins by default
def stream_headers():
    return {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked",
    }

# Configure Gemini API using environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini models
model = GenerativeModel("gemini-1.5-flash")

model2 = genai.GenerativeModel(model_name="gemini-2.0-flash-preview-image-generation")

# Clean the streamed chunk
def clean_chunk(content):
    # Remove any ```json or ``` wrappers
    cleaned = re.sub(r"^```json\s*|```$", "", content.strip())
    return cleaned.strip()


# Store POSTed mind map and return request ID
@app.route("/api/v1/slides/initiate", methods=["POST"])
def initiate_slide_stream():
    data = request.json.get("input")
    if not data:
        return jsonify({"error": "Missing input data"}), 400

    request_id = str(uuid.uuid4())

    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO slide_requests (id, user_id, mindmap_json) VALUES (%s, %s, %s)",
                (request_id, None, json.dumps(data))
            )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"request_id": request_id}), 200

def generate_prompt_templateSlide(data):
    prompt =  f"""
You are a professional **Slide Generation AI Assistant** built for modern sales teams. Your role is to help salespeople generate **polished, client-facing PowerPoint slides** from structured sales data — including deal summaries, mind maps, client notes, and strategy outlines.

---

## 🎯 PURPOSE:

This tool helps **sales professionals** save time and effort by instantly turning structured sales input (like mind maps or outlines) into **comprehensive, ready-to-present slides**. These slides are typically used to:

- Pitch products or solutions to clients
- Summarize key deal conversations
- Share strategies or action plans
- Present progress and updates to stakeholders

The final slide deck should be professional, visually engaging, content-rich, and tailored for **external presentation to clients or decision-makers**.

---

## 📥 DATA SOURCE:

The structured input you'll receive is derived from:
- AI-generated **Deal Summaries**
- Sales meeting transcripts
- Salesperson-entered mind maps and outlines
- CRM-extracted insights and notes

This information has already been pre‑processed into a structured mind map format that you will use to build the slides.

---

## 🧠 YOUR ROLE:

As the assistant, your job is to:
1. Analyze the structure and content of the mind map to deeply understand the sales narrative and key messages.
2. Break it into a comprehensive set of logically sequenced slides that tell a compelling story.
3. **Significantly elaborate on the provided mind map content.** Expand each point into detailed explanations, relevant examples, supporting statistics, value propositions, or context that creates rich, informative slides. Add 3-5x more content than appears in the mind map outline.
4. Use **modern design best practices** and the detailed **DESIGN & STYLE GUIDELINES** (see below) to organize content effectively and ensure a visually stunning, professional look.
5. Output a structured **JSON array** representing the slide deck.
6. Dynamically **adapt slide styling** (backgrounds, text colors, accent colors) based on the provided "theme" value from mindMapJson.theme.
7. Ensure proper spacing and no element overlapping by precisely calculating positioning values.

---

## 🎨 Theme Behavior:

- If mindMapJson.theme is "light":
  - Use **varied light backgrounds** (e.g., white, off-white, subtle light gradients, very light blues or grays as specified in Design Guidelines).
  - Use **dark text colors** with adequate contrast (e.g., deep blues, charcoal, rich browns, dark navy) for headings and paragraphs.
  - Use accent colors like soft blues (#4285F4), subtle greens (#34A853), light teals (#00ACC1), or gentle oranges (#FB8C00).
- If mindMapJson.theme is "dark":
  - Use **varied dark backgrounds** (e.g., deep blue-blacks, rich charcoals, subtle dark gradients as specified in Design Guidelines).
  - Use **light text colors** with excellent contrast (e.g., off-whites, soft creams, light grays) for headings and paragraphs.
  - Use accent colors like vibrant teals (#00BCD4), glowing purples (#AB47BC), bright cyans (#00E5FF), or warm ambers (#FFD740).

The design should always be visually coherent, modern, and extremely easy to read, following the **DESIGN & STYLE GUIDELINES**.

---

## 🌟 DESIGN & STYLE GUIDELINES:

Your generated slides must be visually stunning, contemporary, and executive-level professional. Adhere to these principles:

### 1. Typography:
- **Font Families (Suggest these, actual rendering depends on your PPT engine):**
  - Headings: Use a clean, bold sans-serif font (e.g., "Montserrat", "Raleway", "Poppins", "Arial").
  - Body Text: Use a highly legible sans-serif font (e.g., "Open Sans", "Roboto", "Lato", "Nunito").
- **Font Sizes (px):**
  - Main Slide Titles (Headings): 42px - 52px, fontWeight: "bold" or 700.
  - Subheadings / Section Titles: 28px - 36px, fontWeight: "600" or "semibold".
  - Paragraphs / Body Text: 18px - 24px, fontWeight: "normal" or 400.
  - Bullet Points / List Items: 18px - 22px.
  - Captions / Ancillary Text: 14px - 16px.
- **Color:** Ensure high contrast between text and background based on the theme. Use accent colors sparingly for emphasis.
- **Line Spacing:** Use generous line spacing for readability (e.g., "lineHeight": "1.6" to "1.8" for paragraphs and list items).
- **Text Alignment:** Use "textAlign": "left" for most body content for better readability. Center headings or important callouts when appropriate.


### 3. Backgrounds and Colors:
- **Light Theme Backgrounds:**
  - Solid: #ffffff, #f8f9fa, #e9ecef, #f5f7fa, #f0f4f8
  - Gradients: Subtle gradients like:
    - "linear-gradient(135deg, #ffffff, #f0f4f8)"
    - "linear-gradient(to right, #f9f9f9, #eef2f7)"
    - "linear-gradient(to bottom, #ffffff, #f2f6fc)"
  - Accent Backgrounds (use sparingly):
    - Very light blue: #e8f0fe
    - Soft cream: #fffaf0
    - Light mint: #f0fff4
- **Dark Theme Backgrounds:**
  - Solid: #121212, #1e1e1e, #2c3e50, #1a2639, #2d3436
  - Gradients: Rich dark gradients like:
    - "linear-gradient(135deg, #232526, #414345)"
    - "linear-gradient(to right, #2c3e50, #4b6cb7)"
    - "linear-gradient(to bottom, #1a2639, #3a506b)"
  - Accent Backgrounds (use sparingly):
    - Deep navy: #1a237e
    - Rich purple: #311b92
    - Dark teal: #004d40

### 4. Content Element Styling:
- **Headings:** 
  - Position at "top": "5%" to "8%" 
  - Add "marginBottom": "30px" or proper spacing calculation
  - Consider adding subtle text shadow or border-bottom for emphasis
  - **Images/Placeholders:** Use " (https://placehold.co/600x400)" with contextual captions.

  
- **Paragraphs:** 
  - Maximum 5-7 lines per paragraph
  - "lineHeight": "1.8"
  - "maxWidth": "85%" for readability
  - For content-rich slides, place at "top": "25%" or below headings with 40px+ spacing
  
- **Lists:** 
  - Styled bullets (not just plain circles) for bullet lists
  - Add "marginBottom": "15px" to each list item
  - Indent sublists by "30px"
  - Limit to 5-7 bullet points per slide, create additional slides if more are needed
  
  
- **Images/Placeholders (`type: "image"`):**
  - **Include a detailed `"prompt"` field (string) suitable for an AI image generator, describing the desired visual based on the slide content.**
  - Continue to include the `"src"` field with a `(https://placehold.co/600x400)` URL, specifying appropriate dimensions.
  - Position images with precise `left`, `top`, `width`, `height` coordinates that **guarantee no overlap with text or other critical elements**.
  - Examples for positioning:
    - Right-side image: `left: "55%", width: "40%"` with text at `left: "5%"` and shared/aligned `top`.
    - Left-side image: `left: "5%", width: "40%"` with text at `left: "50%"` and shared/aligned `top`.
    - Centered image below text: `left: "25%", width: "50%"` with `top` calculated using vertical stacking below the preceding text block.
  - Always include a descriptive `"caption"` (string).
  - Use placeholder URLs with appropriate colors matching the theme (e.g., `/ffffff/222` for light, `/222/eee` for dark).
  - Include `marginBottom` for spacing after the image/caption block.
  
- **Tables:** 
  - Use alternating row colors for better readability
  - Light theme tables: Header row #4285F4 with white text, alternating rows #ffffff and #f5f5f5
  - Dark theme tables: Header row #5E35B1 with white text, alternating rows #2d2d2d and #373737
  - Add proper cell padding: 12px
  - Align numerical data right, text data left
  - Include table captions or titles
  
- **Charts/Infographics:**
  - Use clear labels and legends
  - Employ theme-appropriate colors
  - Position with generous surrounding whitespace
  - Include insightful titles or captions
  
- **Quotes:** 
  - Use large, italic font style
  - Include decorative quotation marks
  - Add attribution in smaller font below
  - Consider background shading or borders
  
- **Icons & Visual Elements:**
  - Suggest relevant icons (e.g., 📈, 🎯, 💡, 🔄)
  - Use consistent styling across all slides
  - Position with careful alignment to text
  
- **Callout Boxes:**
  - Use subtle background colors (#f8f9fa for light theme, #2a2a2a for dark theme)
  - Add light border or shadow
  - Position with generous margin from other elements

### 5. Element Types:
- **type**: **One of**:
  - "heading", "subheading", "paragraph", "bullet_list", "numbered_list"  
  - "image", "infographic", "table", "chart", "quote", "icon", "callout_box", "sidebar", "timeline", "comparison", "statistic", "process_flow"
  

## 🖼️ Example Output:
{{
[
  {{
    "slide_id": "slide_001",
    "background": {{
      "type": "gradient",
      "value": "linear-gradient(135deg, #ffffff, #f0f4f8)" // Example for light theme
    }},
    "content": [
      {{
        "id": "content_001",
        "type": "heading",
        "text": "Comprehensive Client Objectives Overview",
        "style": {{
          "fontSize": "46px",
          "fontWeight": "bold",
          "color": "#2c3e50",
          "textAlign": "center",
          "left": "7%",
          "top": "8%",
          "width": "86%",
          "height": "auto",
          "position": "absolute"
        }}
      }},
      {{
        "id": "content_002",
        "type": "paragraph",
        "text": "Our analysis identified these key business drivers that are guiding the client's technology investment strategy for the upcoming fiscal year. Each objective has been carefully aligned with industry benchmarks and projected market conditions to ensure maximum ROI.",
        "style": {{
          "fontSize": "22px",
          "fontWeight": "normal",
          "color": "#333333",
          "textAlign": "center",
          "left": "10%",
          "top": "20%", // Note the spacing after the heading
          "width": "80%",
          "lineHeight": "1.6",
          "position": "absolute"
        }}
      }},
        {{
          "id": "content_003",
          "type": "image",
          "prompt": "Conceptual diagram showing data flowing from disparate systems into a central analytical platform, with insights radiating outwards. Modern, clean vector art style. Use light theme appropriate colors like soft blues and greens.", // Detailed image prompt
          "src": "https://placehold.co/600x400?text=SynergyFlow+Dashboard+Mockup",
          "caption": "Modern hospital with AI-related overlay",
          "style": {{
           "left": "20%", // Centering example
            "top": "calc(content_002.top + content_002.height + 40px)", // Calculated top
            "width": "60%",
            "height": "400px", // Explicit height for placeholder
            "position": "absolute",
            "marginBottom": "20px" // Space after image
          
        }}
    }},
  }}
  ...
]
}}



## 🧾 OUTPUT RULES:

- Output only the JSON array, wrapped in `{{` and `}}`, with no surrounding markdown or explanations.
- Do not include any additional keys, comments, or text outside the JSON structure.
- Group related points from the mind map into slides that feel complete and thematically coherent.
- Enrich sparse points with supportive paragraphs, examples, or bullet details to avoid empty-looking slides.
- Maintain consistent typography, spacing, and alignment as per the design guidelines.
- Use placeholder image URLs (https://placehold.co/600x400) when visuals are implied.
- Ensure every style object includes `position": "absolute"` and valid layout properties (`left`, `top`, `width`, and optionally `height`).
- Adapt background and text colors based on the `theme` property from `data`.
- Strive for layout variety: mix title, list, two-column, and image-focused slides where appropriate.




## 🧩 Mind Map Input:

Use the structured mind map or outline provided below to generate the slide deck.
This input includes the "theme" property. Adjust your styles accordingly.

{data}

""".strip()

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)

    raw = response.text.strip()
    print(f"Raw response: {raw}")
    cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    
    print(f"Cleaned response: {cleaned}")

    try:
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini output not valid JSON: {e}\nRaw:\n{cleaned}")


# Initialize S3 client using environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=AWS_REGION,
)

# Setup AWS S3 client
def upload_image_to_s3(image_data: bytes, filename: str) -> str:
    s3_key = f"slides/{filename}.png"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=image_data, ContentType='image/png')
    return f"{BASE_URL}{s3_key}"

  
def generate_image_from_prompt(prompt: str) -> bytes:
    response = model.generate_content(f"Generate a high-quality PNG image based on the following prompt: {prompt}",
                                      stream=False)
    image_data = None
    for part in response.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            image_data = base64.b64decode(part.inline_data.data)
            break
    return image_data



def update_slide_json_with_generated_images(slide_json: dict) -> dict:
    for slide in slide_json.get("data", {}).get("slides", []):
        for content in slide.get("content", []):
            if content.get("type") == "image":
                prompt = content.get("prompt")
                if prompt:
                    print(f"Generating image for prompt: {prompt}")
                    image_bytes = generate_image_from_prompt(prompt)
                    if image_bytes:
                        image_filename = f"{content['id']}_{uuid.uuid4().hex[:8]}"
                        image_url = upload_image_to_s3(image_bytes, image_filename)
                        content["src"] = image_url
                        print(f"Image uploaded to S3: {image_url}")
                    else:
                        print(f"Failed to generate image for prompt: {prompt}")
    return slide_json



# --- DB fetch logic ---
def fetch_mindmap_by_request_id(request_id, db_config):
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT mindmap_json FROM slide_requests WHERE id = %s", (request_id,))
            result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        raise e
    
# Helper to fetch mindmap + slide_json
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
  
def fetch_slide_json(request_id):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT slide_json FROM slide_requests WHERE id = %s",
                (request_id,)
            )
            row = cursor.fetchone()
            return json.loads(row["slide_json"]) if row and row.get("slide_json") else None
    finally:
        conn.close()
        
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
        
# Helper to update slide_json and updated_at
def store_slide_json(request_id, slide_json):
    conn = pymysql.connect(**db_config)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE slide_requests SET slide_json = %s WHERE id = %s",
                (json.dumps(slide_json), request_id)
            )
        conn.commit()
    finally:
        conn.close()

@app.route("/api/v1/slides/generate-2", methods=["GET"])
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
        response_json = generate_prompt_templateSlide(mindmap_json)
        print(f"Generated slide JSON: {response_json}")
        # Store in DB
        store_slide_json(request_id, response_json)

        return Response(
            json.dumps({
                "data": response_json,
                "cached": False
            }, indent=2),
            mimetype='application/json'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-slide-images', methods=['POST'])
def generate_slide_images():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        updated_json = update_slide_json_with_generated_images(data)
        return jsonify(updated_json), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
      
@app.route("/api/v1/images/generate", methods=["POST"])
def generate_image():
    data = request.get_json() or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Ask the model for the image
        response = model.generate_content(prompt, stream=False)

        # Extract image data
        image_data = None
        mime_type = "image/png"  # Default fallback
        for part in response.parts:
            mime = getattr(part.inline_data, "mime_type", "")
            b64   = getattr(part.inline_data, "data", "")
            if b64 and mime.startswith("image/"):
                image_data = base64.b64decode(b64)
                mime_type = mime
                break

        if image_data is None:
            return jsonify({"error": "Model did not return any image data"}), 502

        # Encode the image as base64 string
        image_b64 = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_b64}"

        return jsonify({"image_base64": data_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
      
      
@app.route("/api/v1/slides/content", methods=["POST"])
def get_slide_content():
    try:
        data = request.get_json()
        request_id = data.get("request_id")
        slide_id = data.get("slide_id")
        content_id = data.get("content_id")

        if not (request_id and slide_id and content_id):
            return jsonify({"error": "Missing one or more required fields"}), 400

        # Fetch record from DB
        record = fetch_request_record(request_id)
        if not record:
            return jsonify({"error": "No record found for this request ID"}), 404

        mindmap_json, slide_json_str, updated_at = record

        # Parse slide JSON
        slide_json = json.loads(slide_json_str)
        slides = slide_json.get("slides", [])

        # Find the target slide
        target_slide = next((s for s in slides if s.get("slide_id") == slide_id), None)
        if not target_slide:
            return jsonify({"error": "Slide not found"}), 404

        # Find the target content
        content_items = target_slide.get("content", [])
        target_content = next((c for c in content_items if c.get("id") == content_id), None)
        if not target_content:
            return jsonify({"error": "Content not found"}), 404

        return jsonify({"data": target_content}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
      
  
@app.route("/api/v1/slides/content/edit-text", methods=["POST"])
def edit_slide_content():
    """
    API endpoint to update text content in slides.
    
    This endpoint is for updating text-based content only (headings, paragraphs, lists, etc.).
    For updating image content, use the /api/v1/slides/content/image endpoint.
    
    Requires:
    - request_id: The ID of the slide request
    - slide_id: The ID of the slide to update
    - content_id: The ID of the content element to update
    - prompt: The new prompt to generate updated content
    
    Returns:
    - The updated content element
    """
    try:
        data = request.get_json()
        request_id = data.get("request_id")
        slide_id = data.get("slide_id")
        content_id = data.get("content_id")
        new_prompt = data.get("prompt")

        if not (request_id and slide_id and content_id and new_prompt):
            return jsonify({"error": "Missing one or more required fields"}), 400

        # Fetch record from DB
        record = fetch_request_record(request_id)
        if not record:
            return jsonify({"error": "No record found for this request ID"}), 404

        mindmap_json, slide_json_str, updated_at = record

        # Parse slide JSON
        slide_json = json.loads(slide_json_str)
        slides = slide_json.get("slides", [])

        # Find the target slide
        target_slide = next((s for s in slides if s.get("slide_id") == slide_id), None)
        if not target_slide:
            return jsonify({"error": "Slide not found"}), 404

        # Find the target content
        content_items = target_slide.get("content", [])
        target_content = next((c for c in content_items if c.get("id") == content_id), None)
        if not target_content:
            return jsonify({"error": "Content not found"}), 404

        print(target_content)
        # Determine content type and update based on prompt
        content_type = target_content.get("type")
        
        # This API is only for non-image content
        if content_type == "image":
            return jsonify({
                "error": "This API cannot be used to update image content. Please use the /api/v1/slides/content/image endpoint instead."
            }), 400
        
        # For text content (heading, paragraph, bullet_list, etc.)
        # Get the old content to provide context for updating
        
        old_content = target_content.get("text", "")
        

        # Generate new text based on the prompt with context
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        generate_prompt = f"""
        You are a professional slide content writer. You need to update the following slide content.
        
        Content type: {content_type}
        Current content: "{old_content}"
        
        Generate new content based on this prompt:
        {new_prompt}
        
        Keep the style consistent with presentation slides - be professional, concise, and impactful.
        Maintain the appropriate length and format for this type of slide element.
        Only return the generated text, with no additional explanation or formatting.
        """
        
        response = model.generate_content(generate_prompt)
        new_text = response.text.strip()
        
        logger.info(f"Updated content for {content_id} from: '{old_content}' to: '{new_text}'")
        
        # Update the content with new text
        target_content["text"] = new_text

        # Update the slide JSON in the database
        updated_slide_json = json.dumps(slide_json)
        update_slide_record(request_id, updated_slide_json)

        return jsonify({
            "message": "Content updated successfully",
            "data": target_content
        }), 200

    except Exception as e:
        logger.error(f"Error updating slide content: {str(e)}")
        return jsonify({"error": str(e)}), 500
      

@app.route("/api/v1/slides/content/image", methods=["POST"])
def image_endpoint():
    data = request.get_json() or {}
    try:
        updated_block = generate_image_for_content(
            data["request_id"],
            data["slide_id"],
            data["content_id"]
        )
        return jsonify({"data": updated_block}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except RuntimeError as re:
        return jsonify({"error": str(re)}), 500
    except Exception as e:
        return jsonify({"error": "Internal error"}), 500
  
@app.route("/", methods=["GET"])
def hello():
    return "Hello, this is the LangChain Google Gemini 1.5 Flash API for generating slides!"











def fetch_request_record_cached(request_id):
    return fetch_request_record(request_id)

@app.route('/api/v1/slides/generate', methods=['GET'])
def generate_presentation():
    try:
        request_id = request.args.get("id")
        if not request_id:
            return jsonify({"error": "Missing request ID"}), 400

        # Get from DB with caching
        record = fetch_request_record(request_id)
        if not record:
            return jsonify({"error": "No record found"}), 404

        input_data, cached_slides, updated_at = record

        # Return cached slides if available
        if cached_slides:
            data = json.loads(cached_slides)
            return Response(
                json.dumps({
                    "cached": True,
                    "last_updated": updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else None,
                    "data": data
                }, indent=2),
                mimetype="application/json"
            )

        # Parse and prepare input data
        if isinstance(input_data, str):
            input_data = json.loads(input_data)
            
        # Structure for BAML - ensure proper type conversion
        try:
            presentation_input = {
                "id": int(input_data.get('id', 0)),
                "title": input_data.get('title', ''),
                "outline": [{
                    "id": int(section.get('id', 0)),
                    "title": section.get('title', ''),
                    "points": section.get('points', [])
                } for section in input_data.get('outline', [])]
            }
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Invalid data format - could not convert IDs to integers: {str(e)}"}), 400

        # Generate presentation
        slides = b.GeneratePresentation(presentation_input)

        # Convert to JSON format efficiently
        slides_json = []
        for slide in slides:
            content = []
            for element in slide.content:
                element_dict = {
                    "id": getattr(element, 'id', None),
                    "type": None,
                    "x": getattr(element, 'x', 0),
                    "y": getattr(element, 'y', 0),
                    "width": getattr(element, 'width', 0),
                    "height": getattr(element, 'height', 0)
                }

                if hasattr(element, 'html'):
                    element_dict.update({"type": "html", "html": element.html})
                elif hasattr(element, 'content'):
                    style = {}
                    if hasattr(element, 'style'):
                        style = {k: v for k, v in {
                            "font_family": getattr(element.style, 'font_family', None),
                            "font_size": getattr(element.style, 'font_size', None),
                            "color": getattr(element.style, 'color', None),
                            "line_height": getattr(element.style, 'line_height', None),
                            "alignment": getattr(element.style, 'alignment', None)
                        }.items() if v is not None}
                    element_dict.update({
                        "type": "text",
                        "content": element.content,
                        **({"style": style} if style else {})
                    })
                elif hasattr(element, 'src'):
                    style = {}
                    if hasattr(element, 'style'):
                        style = {k: v for k, v in {
                            "border_radius": getattr(element.style, 'border_radius', None),
                            "object_fit": getattr(element.style, 'object_fit', None),
                            "border": getattr(element.style, 'border', None),
                            "shadow": getattr(element.style, 'shadow', None)
                        }.items() if v is not None}
                    element_dict.update({
                        "type": "image",
                        "src": element.src,
                        "alt_text": getattr(element, 'alt_text', ''),
                        "caption": getattr(element, 'caption', ''),
                        "prompt": getattr(element, 'prompt', ''),
                        **({"style": style} if style else {})
                    })

                # Only add non-None values
                content.append({k: v for k, v in element_dict.items() if v is not None})

            slide_dict = {
                "slide_id": slide.slide_id,
                "background": slide.background
            }
            if content:
                slide_dict["content"] = content
            slides_json.append(slide_dict)

        response_data = {"slides": slides_json}
        
        # Cache the result
        # presentation_cache[cache_key] = (time.time(), response_data)
        
        # Store in DB asynchronously
        store_slide_json(request_id, response_data)

        return Response(
            json.dumps({
                "data": response_data,
                "cached": False
            }, indent=2),
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error in generate_presentation: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    
# @app.route("/api/v1/slides/generate-all-images", methods=["POST"])
# def generate_all_images():
#     """
#     Endpoint to generate images for all slides in a presentation.
#     Expects a JSON payload with 'request_id' and 'slide_id'.
#     """
#     data = request.get_json() or {}
#     request_id = data.get("request_id")
#     print(f"Request ID: {request_id}")
#     if not request_id:
#         return jsonify({"error": "Missing request ID"}), 400
#     return generate_all_images_for_presentation(request_id)
    
@app.route("/api/v1/slides/generate-all-images", methods=["POST"])
def generate_all_images():
    data = request.get_json() or {}
    request_id = data.get("request_id")
    if not request_id:
        return jsonify({"error": "Missing request ID"}), 400

    # Fire-and-forget async processing
    thread = Thread(target=generate_all_images_for_presentation, args=(request_id,))
    thread.start()

    return jsonify({"success": True, "message": "Image generation started"}), 202

if __name__ == "__main__":
    app.run(port=8086, debug=True, threaded=True)