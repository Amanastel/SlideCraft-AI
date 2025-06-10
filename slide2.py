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
from slide_edit_api import edit_slide_function
from baml_client.sync_client import b
from functools import lru_cache
import time
from threading import Thread
import requests
from urllib.parse import urlparse
import mimetypes
import tempfile


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

model2 = genai.GenerativeModel(
    model_name="gemini-2.0-flash-preview-image-generation")

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
    prompt = f"""
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
    cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(),
                     flags=re.MULTILINE).strip()

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
    s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key,
                         Body=image_data, ContentType='image/png')
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
                        image_url = upload_image_to_s3(
                            image_bytes, image_filename)
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
            cursor.execute(
                "SELECT mindmap_json FROM slide_requests WHERE id = %s", (request_id,))
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
            b64 = getattr(part.inline_data, "data", "")
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
        target_slide = next(
            (s for s in slides if s.get("slide_id") == slide_id), None)
        if not target_slide:
            return jsonify({"error": "Slide not found"}), 404

        # Find the target content
        content_items = target_slide.get("content", [])
        target_content = next(
            (c for c in content_items if c.get("id") == content_id), None)
        if not target_content:
            return jsonify({"error": "Content not found"}), 404

        return jsonify({"data": target_content}), 200

    except Exception as e:
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


@app.route("/api/v1/slides/content/edit-text", methods=["POST"])
def edit_slide_content2():
    """
    Update text content in slides.
    If `content_id` is provided, updates only that content block.
    If `content_id` is missing, updates all text-based content blocks in the slide.
    """
    try:
        data = request.get_json()
        request_id = data.get("request_id")
        slide_id = data.get("slide_id")
        content_id = data.get("content_id")
        new_prompt = data.get("prompt")

        if not (request_id and slide_id and new_prompt):
            return jsonify({"error": "Missing required fields"}), 400

        # Fetch from DB
        record = fetch_request_record(request_id)
        if not record:
            return jsonify({"error": "No record found for this request ID"}), 404

        mindmap_json, slide_json_str, updated_at = record
        slide_json = json.loads(slide_json_str)
        slides = slide_json.get("slides", [])
        target_slide = next(
            (s for s in slides if s.get("slide_id") == slide_id), None)

        if not target_slide:
            return jsonify({"error": "Slide not found"}), 404

        content_items = target_slide.get("content", [])
        content_type = target_slide.get("type")

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # ========== CASE 1: Targeted content update ==========
        if content_id:

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
            target_slide = next(
                (s for s in slides if s.get("slide_id") == slide_id), None)
            if not target_slide:
                return jsonify({"error": "Slide not found"}), 404

            # Find the target content
            content_items = target_slide.get("content", [])
            target_content = next(
                (c for c in content_items if c.get("id") == content_id), None)
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

            old_content = target_content.get("html", "")

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

            logger.info(
                f"Updated content for {content_id} from: '{old_content}' to: '{new_text}'")

            # Update the content with new text
            target_content["html"] = new_text

            # Update the slide JSON in the database
            updated_slide_json = json.dumps(slide_json)
            update_slide_record(request_id, updated_slide_json)

            return jsonify({
                "message": "Content updated successfully",
                "data": target_content
            }), 200

        else:
            target_slide = next(
                (s for s in slides if s.get("slide_id") == slide_id), None)
            if not target_slide:
                return jsonify({"error": "Slide not found"}), 404

            # Edit the slide using the edit_slide_function
            response = edit_slide_function(target_slide, new_prompt)
            new_updated_slide = response.get("editedSlide", {})
            print(f"New updated slide: {new_updated_slide}")

            # Find and update the slide in the slides array
            for i, slide in enumerate(slides):
                if slide.get("slide_id") == slide_id:
                    slides[i] = new_updated_slide
                    break

            # Update the slide JSON in the database
            updated_slide_json = json.dumps(slide_json)
            update_slide_record(request_id, updated_slide_json)

            logger.info(f"Updated entire slide {slide_id} with new content based on prompt: {new_prompt}")

            return jsonify({
                "message": "Slide updated successfully",
                "data": response
            }), 200
    except ValueError as ve:
        logger.error(f"Value error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error updating slide content: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error updating slide content: {str(e)}")
        return jsonify({"error": str(e)}), 500


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
                content.append(
                    {k: v for k, v in element_dict.items() if v is not None})

            slide_dict = {
                "slide_id": slide.slide_id,
                "background": slide.background
            }
            if content:
                slide_dict["content"] = content
            slides_json.append(slide_dict)

        response_data = {"slides": slides_json}

        # Store in DB asynchronously
        store_slide_json(request_id, response_data)
        
        # Generate images for the presentation
        # image_response = generate_all_images_for_presentation(request_id)
            # Fire-and-forget async processing
        thread = Thread(target=generate_all_images_for_presentation,
                        args=(request_id,))
        thread.start()
        # Get the updated record from DB after storing
        # updated_record = fetch_request_record(request_id)
        # if updated_record:
        #     input_data, updated_slides, updated_at = updated_record
        #     if updated_slides:
        #         data = json.loads(updated_slides)
        #         return Response(
        #             json.dumps({
        #                 "cached": False,
        #                 "last_updated": updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else None,
        #                 "data": data
        #             }, indent=2),
        #             mimetype="application/json"
        #         )

        # Fallback response if DB update failed
        return Response(
            json.dumps({
                "cached": False,
                "last_updated": None,
                "data": response_data,
                # "images": image_response
            }, indent=2),
            mimetype="application/json"
        )

    except Exception as e:
        logger.error(f"Error in generate_presentation: {str(e)}")
        return jsonify({'error': str(e)}), 500
    




@app.route("/api/v1/slides/generate-all-images", methods=["POST"])
def generate_all_images():
    data = request.get_json() or {}
    request_id = data.get("request_id")
    if not request_id:
        return jsonify({"error": "Missing request ID"}), 400

    # Fire-and-forget async processing
    thread = Thread(target=generate_all_images_for_presentation,
                    args=(request_id,))
    thread.start()
    
    

    return jsonify({"success": True, "message": "Image generation started","data": generate_all_images_for_presentation(request_id)}), 202


@app.route("/api/v1/slides/slide-data", methods=["POST"])
def getSlideData():
    data = request.get_json() or {}
    request_id = data.get("request_id")
    if not request_id:
        return jsonify({"error": "Missing request ID"}), 400
    # Fetch record from DB
    
    input_data = data.get("input_data", {})
    print(f"Input data received: {input_data}")
    if not input_data:
        return jsonify({"error": "Missing input data"}), 400


    # Parse and prepare input data
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    # Structure for BAML - handling the new data format
    try:
        presentation_input = {
            "id": int(input_data.get('id', 0)),
            "title": input_data.get('title', ''),
            "outline": []
        }
        
        # Handle slides array if present
        if 'slides' in input_data:
            for slide in input_data.get('slides', []):
                slide_outline = {
                    "id": int(slide.get('id', 0)),
                    "title": slide.get('title', ''),
                    "points": slide.get('key_content_elements', [])
                }
                presentation_input["outline"].append(slide_outline)
        
        # Fallback: handle legacy outline format if no slides but outline exists
        elif 'outline' in input_data:
            for section in input_data.get('outline', []):
                section_outline = {
                    "id": int(section.get('id', 0)),
                    "title": section.get('title', ''),
                    "points": section.get('points', [])
                }
                presentation_input["outline"].append(section_outline)
        
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data format - could not convert IDs to integers: {str(e)}"}), 400

    # Generate presentation
    slides = b.GeneratePresentation(presentation_input)

    # Convert to JSON format efficiently (same logic as in generate_presentation route)
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
            content.append(
                {k: v for k, v in element_dict.items() if v is not None})

        slide_dict = {
            "slide_id": slide.slide_id,
            "background": slide.background
        }
        if content:
            slide_dict["content"] = content
        slides_json.append(slide_dict)
        
        
        response_data = {"slides": slides_json}

        # Store in DB asynchronously
        store_slide_json(request_id, response_data)
        
        
        thread = Thread(target=generate_all_images_for_presentation,
                        args=(request_id,))
        thread.start()

    return jsonify({"data": {"slides": slides_json}}), 200





@app.route("/api/v1/files/upload", methods=["POST"])
def upload_file():
    """
    Upload any file to S3 and return the URL
    
    Expected request:
    - multipart/form-data with 'file' field
    OR
    - JSON with base64 encoded file data
    
    Returns:
    {
        "success": true,
        "url": "https://s3.amazonaws.com/bucket/path/to/file.ext",
        "filename": "generated_filename.ext",
        "file_type": "pdf|docx|png|etc",
        "content_type": "application/pdf"
    }
    """
    try:
        file_data = None
        filename = None
        content_type = None
        
        # Check if it's a file upload (multipart/form-data)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Get file extension
            file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            # Allow all file types - no restrictions
            # Common file types with their content types
            content_type_map = {
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'xls': 'application/vnd.ms-excel',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'ppt': 'application/vnd.ms-powerpoint',
                'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'txt': 'text/plain',
                'md': 'text/markdown',
                'html': 'text/html',
                'csv': 'text/csv',
                'json': 'application/json',
                'xml': 'application/xml',
                'zip': 'application/zip',
                'rar': 'application/x-rar-compressed',
                '7z': 'application/x-7z-compressed',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'webp': 'image/webp',
                'svg': 'image/svg+xml',
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'flac': 'audio/flac'
            }
            
            content_type = content_type_map.get(file_extension, 'application/octet-stream')
            
            # Read file data
            file_data = file.read()
            filename = f"{uuid.uuid4().hex[:8]}.{file_extension}" if file_extension else f"{uuid.uuid4().hex[:8]}"
            
        # Check if it's JSON with base64 data
        elif request.is_json:
            data = request.get_json()
            base64_data = data.get("file_base64")
            custom_filename = data.get("filename")
            file_type = data.get("file_type", "")
            
            if not base64_data:
                return jsonify({"error": "Missing 'file_base64' field in JSON"}), 400
            
            try:
                # Handle data URL format (data:application/pdf;base64,...)
                if base64_data.startswith('data:'):
                    content_type = base64_data.split(';')[0].split(':')[1]
                    base64_data = base64_data.split(',')[1]
                
                # Decode base64 data
                file_data = base64.b64decode(base64_data)
                
                # Use custom filename if provided, otherwise generate one
                if custom_filename:
                    filename = custom_filename
                else:
                    # Try to determine extension from file_type or content_type
                    extension = ""
                    if file_type:
                        extension = f".{file_type}"
                    elif content_type:
                        type_to_ext = {
                            'application/pdf': '.pdf',
                            'application/msword': '.doc',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                            'text/plain': '.txt',
                            'image/png': '.png',
                            'image/jpeg': '.jpg'
                        }
                        extension = type_to_ext.get(content_type, '')
                    
                    filename = f"{uuid.uuid4().hex[:8]}{extension}"
                
                # Set content type if not already set
                if not content_type:
                    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    content_type_map = {
                        'pdf': 'application/pdf',
                        'doc': 'application/msword',
                        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'txt': 'text/plain',
                        'png': 'image/png',
                        'jpg': 'image/jpeg',
                        'jpeg': 'image/jpeg'
                    }
                    content_type = content_type_map.get(file_extension, 'application/octet-stream')
                    
            except Exception as e:
                return jsonify({"error": f"Invalid base64 data: {str(e)}"}), 400
        else:
            return jsonify({"error": "No file data provided. Use multipart/form-data with 'file' field or JSON with 'file_base64' field"}), 400
        
        # Validate file data size (max 60MB for general files)
        max_size = 200 * 1024 * 1024  # 60MB
        if len(file_data) > max_size:
            return jsonify({"error": f"File too large. Maximum size: {max_size / 1024 / 1024}MB"}), 400
        
        # Upload to S3
        try:
            s3_key = f"uploads/{filename}"
            
            # Use the existing S3 client (s3) defined earlier in the file
            s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                # Remove ACL to avoid access denied errors
            )
            
            # Construct the public URL
            file_url = f"https://s3.{AWS_REGION}.amazonaws.com/{S3_BUCKET_NAME}/{s3_key}"
            
            # Get file type from filename
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            logger.info(f"File uploaded successfully: {file_url}")
            
            return jsonify({
                "success": True,
                "url": file_url,
                "filename": filename,
                "file_type": file_type,
                "content_type": content_type,
                "size_bytes": len(file_data)
            })
            
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return jsonify({"error": f"Failed to upload to S3: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500




@app.route("/api/v1/files/summarize", methods=["POST"])
def summarize_file():
    """
    Summarize a file from a given URL
    
    Expected request body:
    {
        "file_url": "https://example.com/document.pdf",
        "summary_type": "brief|detailed|key_points", // optional, defaults to "brief"
        "max_length": 500 // optional, max words in summary
    }
    
    Returns:
    {
        "success": true,
        "summary": "Generated summary text...",
        "file_info": {
            "url": "original_url",
            "file_type": "pdf|docx|txt|etc",
            "file_size": 12345,
            "title": "extracted_title"
        },
        "summary_type": "brief"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        file_url = data.get("file_url")
        summary_type = data.get("summary_type", "brief")
        max_length = data.get("max_length", 500)
        
        if not file_url:
            return jsonify({"error": "Missing 'file_url' field"}), 400
        
        # Validate summary type
        # valid_summary_types = ["brief", "detailed", "key_points"]
        # if summary_type not in valid_summary_types:
        #     return jsonify({"error": f"Invalid summary_type. Must be one of: {', '.join(valid_summary_types)}"}), 400
        
        # Validate max_length
        if not isinstance(max_length, int) or max_length < 50 or max_length > 2000:
            return jsonify({"error": "max_length must be an integer between 50 and 2000"}), 400
        
        # Download and extract file content
        try:
            file_content, file_info = download_and_extract_content(file_url)
            print(f"File info: {file_info}")  # Log file info for debugging
            print(f"Extracted file content: {file_content[:100]}...")  # Log first 100 chars for debugging
        except Exception as e:
            return jsonify({"error": f"Failed to download or extract file content: {str(e)}"}), 400
        
        # Generate summary using AI
        try:
            summary = generate_file_summary(file_content, summary_type, max_length, file_info)
        except Exception as e:
            return jsonify({"error": f"Failed to generate summary: {str(e)}"}), 500
        
        return jsonify({
            "success": True,
            "summary": summary,
            "file_info": file_info,
            "summary_type": summary_type,
            "content_length": len(file_content),
            "summary_length": len(summary.split())
        })
        
    except Exception as e:
        logger.error(f"File summarization error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/api/v1/files/extract", methods=["POST"])
def extract_file_content():
    """
    Extract raw content from a file at the given URL without AI summarization
    
    Expected request body:
    {
        "file_url": "https://example.com/document.pdf",
        "include_metadata": true, // optional, defaults to true
        "max_content_length": 50000 // optional, max characters to return, defaults to 50000
    }
    
    Returns:
    {
        "success": true,
        "content": "Raw extracted text content...",
        "file_info": {
            "url": "original_url",
            "file_name": "document.pdf",
            "file_type": "pdf",
            "file_size": 12345,
            "content_type": "application/pdf",
            "title": "extracted_title"
        },
        "content_stats": {
            "total_characters": 15000,
            "total_words": 2500,
            "total_lines": 150,
            "truncated": false
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        file_url = data.get("file_url")
        include_metadata = data.get("include_metadata", True)
        max_content_length = data.get("max_content_length", 50000)
        
        if not file_url:
            return jsonify({"error": "Missing 'file_url' field"}), 400
        
        # Validate max_content_length
        if not isinstance(max_content_length, int) or max_content_length < 100 or max_content_length > 100000:
            return jsonify({"error": "max_content_length must be an integer between 100 and 100000"}), 400
        
        # Download and extract file content
        try:
            file_content, file_info = download_and_extract_content(file_url)
            logger.info(f"File content extracted: {len(file_content)} characters")
        except Exception as e:
            return jsonify({"error": f"Failed to download or extract file content: {str(e)}"}), 400
        
        # Calculate content statistics
        total_characters = len(file_content)
        total_words = len(file_content.split())
        total_lines = len(file_content.split('\n'))
        
        # Truncate content if necessary
        truncated = False
        if total_characters > max_content_length:
            file_content = file_content[:max_content_length] + "... [Content truncated]"
            truncated = True
        
        # Prepare response
        response_data = {
            "success": True,
            "content": file_content,
            "content_stats": {
                "total_characters": total_characters,
                "total_words": total_words,
                "total_lines": total_lines,
                "truncated": truncated,
                "returned_characters": len(file_content)
            }
        }
        
        # Include file metadata if requested
        if include_metadata:
            response_data["file_info"] = file_info
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"File content extraction error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ...existing code...

def download_and_extract_content(file_url):
    """
    Download file from URL and extract text content
    
    Returns:
        tuple: (content_text, file_info_dict)
    """
    import requests
    from urllib.parse import urlparse
    import mimetypes
    import PyPDF2
    from docx import Document
    import tempfile
    import os
    
    try:
        # Parse URL and get basic info
        parsed_url = urlparse(file_url)
        file_name = os.path.basename(parsed_url.path) or "unknown_file"
        
        # Download file
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        
        # Get file info
        content_type = response.headers.get('content-type', '')
        file_size = len(response.content)
        
        # Determine file type
        file_extension = os.path.splitext(file_name)[1].lower()
        if not file_extension:
            # Try to guess from content type
            extension_map = {
                'application/pdf': '.pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                'text/plain': '.txt',
                'text/html': '.html',
                'application/json': '.json'
            }
            file_extension = extension_map.get(content_type, '.txt')
        
        file_info = {
            "url": file_url,
            "file_name": file_name,
            "file_type": file_extension.lstrip('.'),
            "file_size": file_size,
            "content_type": content_type,
            "title": ""
        }
        
        # Extract content based on file type
        if file_extension == '.pdf':
            content = extract_pdf_content(response.content)
        elif file_extension == '.docx':
            content = extract_docx_content(response.content)
        elif file_extension in ['.txt', '.md']:
            content = response.text
        elif file_extension == '.html':
            content = extract_html_content(response.text)
        elif file_extension == '.json':
            content = extract_json_content(response.text)
        else:
            # Try to decode as text
            try:
                content = response.text
            except:
                raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Extract title from content
        title = extract_title_from_content(content, file_extension)
        file_info["title"] = title
        
        # Validate content length
        if len(content.strip()) < 10:
            raise ValueError("File appears to be empty or content could not be extracted")
        
        return content, file_info
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download file: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to process file: {str(e)}")


def extract_pdf_content(pdf_data):
    """Extract text from PDF data"""
    try:
        try:
            import PyPDF2
        except ImportError:
            raise Exception("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2==3.0.1")
        
        from io import BytesIO
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
        content = ""
        
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        
        return content.strip()
    except Exception as e:
        raise Exception(f"Failed to extract PDF content: {str(e)}")


def extract_docx_content(docx_data):
    """Extract text from DOCX data"""
    try:
        try:
            from docx import Document
        except ImportError:
            raise Exception("python-docx is required for DOCX processing. Install with: pip install python-docx==1.1.0")
        
        from io import BytesIO
        
        doc = Document(BytesIO(docx_data))
        content = ""
        
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        
        return content.strip()
    except Exception as e:
        raise Exception(f"Failed to extract DOCX content: {str(e)}")


def extract_html_content(html_text):
    """Extract text from HTML"""
    try:
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # Fallback: simple HTML tag removal
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html_text).strip()
        
        soup = BeautifulSoup(html_text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        return soup.get_text(separator='\n').strip()
    except Exception as e:
        # Fallback: simple HTML tag removal
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_text).strip()


def extract_json_content(json_text):
    """Extract readable content from JSON"""
    try:
        import json
        data = json.loads(json_text)
        
        # Convert JSON to readable text
        def json_to_text(obj, level=0):
            indent = "  " * level
            text = ""
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    text += f"{indent}{key}: "
                    if isinstance(value, (dict, list)):
                        text += f"\n{json_to_text(value, level + 1)}"
                    else:
                        text += f"{value}\n"
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    text += f"{indent}[{i}]: "
                    if isinstance(item, (dict, list)):
                        text += f"\n{json_to_text(item, level + 1)}"
                    else:
                        text += f"{item}\n"
            else:
                text += f"{indent}{obj}\n"
            
            return text
        
        return json_to_text(data)
    except:
        return json_text


def extract_title_from_content(content, file_type):
    """Extract title from content"""
    lines = content.split('\n')
    
    # Get first non-empty line as potential title
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line) > 3:
            # Clean up the title
            title = line[:100]  # Limit to 100 chars
            return title
    
    return "Untitled Document"


def generate_file_summary(content, summary_type, max_length, file_info):
    """Generate AI summary of the file content"""
    
    # Prepare the prompt based on summary type
    if summary_type == "brief":
        summary_instruction = f"Provide a brief, concise summary in {max_length} words or less that captures the main purpose and key information."
    elif summary_type == "detailed":
        summary_instruction = f"Provide a detailed summary in {max_length} words or less that covers the main topics, key findings, and important details."
    elif summary_type == "key_points":
        summary_instruction = f"Extract and list the key points, main findings, or important information in bullet format, using {max_length} words or less."
    
    else:
        summary_instruction = summary_type + f" this is user prompt, base on this prompt, generate a summary "
    prompt = f"""
        You are a professional document summarization AI. Analyze the following document and provide a summary based on the instructions.

        Document Information:
        - File Type: {file_info.get('file_type', 'unknown')}
        - Title: {file_info.get('title', 'Unknown')}
        - Size: {file_info.get('file_size', 0)} bytes

        Summary Instructions: {summary_instruction}

        Document Content:
        {content[:8000]}  # Limit content to avoid token limits

        Please provide a clear, well-structured summary that helps the reader understand the document's content and purpose.
        """

    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        summary = response.text.strip()
        
        # Ensure summary doesn't exceed max_length
        words = summary.split()
        if len(words) > max_length:
            summary = ' '.join(words[:max_length]) + "..."
        
        return summary
        
    except Exception as e:
        raise Exception(f"AI summarization failed: {str(e)}")


if __name__ == '__main__':
    # Run the Flask app
    app.run(port=8086, debug=True, threaded=True)