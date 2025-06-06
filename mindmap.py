import os
import configparser
import pymysql
import json
import time
import logging
import traceback
import re
import google.generativeai as genai
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
# Load environment variables
load_dotenv()

# Initialize Gemini API Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load configuration
api_key = api_key=os.getenv("GEMINI_API_KEY")
# Database configuration from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}
# Configure logging
def setup_logging():
    handler = RotatingFileHandler('moses_prompter.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

setup_logging()

class MeetingAnalysis:
    def __init__(self):
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.role = """
            You are an elite AI sales assistant trained by top-performing AEs, SEs, and sales strategists.
            Your role is to analyze sales meetings and extract key insights, attendees, and action items.
            Focus on identifying sales opportunities, customer pain points, buying signals, and next steps.
            Think like a seasoned sales professional who needs to capture the essence of the meeting for follow-up.
        """

    def get_completion_from_messages(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            raw = response.text.strip()
            cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            return json.loads(cleaned)
        except Exception as e:
            app.logger.error(f"Error in get_completion_from_messages: {str(e)}")
            raise

def fetch_transcripts(db_config, meeting_unique_id):  
    connection = None
    try:  
        connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        transcript_query = """SELECT eventID, speaker, start, end, transcript, created_at FROM meeting_transcript WHERE eventID = %s"""
        cursor.execute(transcript_query, (meeting_unique_id,))
        transcript_rows = cursor.fetchall()
        return [{
            'eventID': tr['eventID'],
            'speaker': tr['speaker'],
            'start': tr['start'],
            'end': tr['end'],
            'transcript': tr['transcript'],
            'created_at': tr['created_at']
        } for tr in transcript_rows]
    finally:
        if connection:
            connection.close()

def get_meeting_participants(db_config, meeting_id):  
    connection = None
    try:  
        connection = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        transcript_query = """
                    SELECT attendee
                        FROM meeting_participant_metadata
                        WHERE meeting_unique_id = %s 
                    """
        cursor.execute(transcript_query, (meeting_id,))
        transcript_rows = cursor.fetchall()
        attendees = [tr['attendee'] for tr in transcript_rows]
        attendees_str = ", ".join(attendees)
        return attendees_str
    finally:
        if connection:
            connection.close()



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
        import re
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



def get_mind_map_prompt(content, audience=None, pages=None, scenario=None, tone=None, meetingDealSummarys=None, file_url=None):
    print(f"Gemini content: {content}")
    print(f"Audience: {audience}, Pages: {pages}, Scenario: {scenario}, Tone: {tone}")
    #  "file_url": ["https://s3.ap-south-1.amazonaws.com/getaligned.work/uploads/668baf9e.pdf"]
    
    if file_url and isinstance(file_url, list) and len(file_url) > 0:
      contentFile = download_and_extract_content(file_url[0])
      # print(f"File content extracted: {contentFile[0]}")
      
      

    metadata = ""

    if audience:
        metadata += f"- **Target Audience**: {audience} — Tailor the message, tone, and examples to resonate with this group.\n"

    if pages:
        metadata += f"- **Presentation Length**: {pages} slides — Keep the structure tight and concise to fit within this range.\n"

    if scenario:
        metadata += f"- **Scenario / Use Case**: {scenario} — Adjust the framing, examples, and emphasis to suit this context.\n"

    if tone:
        metadata += f"- **Desired Tone**: {tone} — Adopt a writing style and vocabulary that matches this tone.\n"
        
    if file_url:
      metadata += f"- **File URL**: {file_url} — Use this file to extract additional context and information.\n"
      # Create a comprehensive prompt for processing the file content
      file_context = f"""
      **File Content Analysis**:
      Below is additional context provided by the user to enhance the presentation content:
      
      Content: {contentFile[0]}
      
      **Instructions for Integration**:
      - Extract key insights, data points, and relevant information from this content
      - Incorporate statistics, quotes, and examples where applicable
      - Use this content to support main arguments and provide evidence
      - If this contains sales-related data (customer profiles, market research, product specs, case studies), emphasize:
        * Customer pain points and challenges
        * Product benefits and value propositions  
        * Market trends and competitive insights
        * Success stories and testimonials
        * Technical specifications or features
        * Pricing and ROI information
      - Ensure the file content complements and strengthens the main presentation narrative
      - Reference specific data points with context (e.g., "According to uploaded market research...")
      
      """
      metadata += file_context
    if meetingDealSummarys:
      metadata += f"- **Meeting Deal Summary**: {meetingDealSummarys} — Use this summary to inform the content and focus on key points.\n"
      # Create a comprehensive prompt for processing meeting deal summaries
      deal_summary_context = f"""
      **Meeting Deal Summary Analysis**:
      {meetingDealSummarys}

      Key Focus Areas for Sales-Related Content:
      - Customer pain points and challenges discussed
      - Product/service benefits highlighted
      - Pricing and budget considerations mentioned
      - Decision-making timeline and process
      - Competitive landscape and positioning
      - Stakeholder involvement and buying signals
      - Next steps and follow-up actions identified
      - Objections raised and responses provided
      """
      metadata += deal_summary_context
        

    print(f"Gemini content: {content}")
    prompt = f"""
  You are a helpful assistant. Based on the following content, generate a detailed slide outline in JSON format.

  ### Input Metadata:
  {metadata if metadata else "N/A"}

  ### Objective:
  Create a **presentation-ready structure** for building a professional PowerPoint from the input content. This should include high-level sections, detailed bullet points, and identifiers to support programmatic slide generation.

  ### Output Format:
  Return valid JSON with the following structure:
  {{
    "title": "Overall Presentation Title",
    "id": <unique-integer-id>,
    "outline": [
      {{
        "id": <integer-id>,
        "title": "Slide Title",
        "points": [
          "Bullet point 1",
          "Bullet point 2",
          "Add quotes, statistics, or examples when possible"
        ]
      }},
      ...
    ]
  }}

  ### Requirements:
  - Include `"id"` at both the top level and for each slide section.
  - Each slide section must contain:
    - A clear and informative `"title"`.
    - At least 3–5 detailed `"points"` that can go directly into slides.
  - Emphasize **clarity**, **real-world context**, and **usefulness for presentations**.
  - Use consistent formatting, avoid vague statements like "etc."
  - The output must be **valid JSON**, without Markdown, comments, or extraneous text.

  ### Example Output:
  {{
    "title": "Implementing continuous integration and deployment (CI/CD) pipelines",
    "id": 12345,
    "outline": [
      {{
        "id": 1,
        "title": "Introduction to CI/CD Pipelines",
        "points": [
          "Definition: Automating the software release process",
          "Benefits: Faster releases, fewer bugs, quicker feedback",
          "CI: Continuous Integration; CD: Continuous Delivery/Deployment",
          "Business Impact: Accelerate time to market by 20–50% (Forrester)"
        ]
      }},
      {{
        "id": 2,
        "title": "Step 1: Setting Up Version Control",
        "points": [
          "Git best practices: branching strategies (Gitflow, trunk–based)",
          "Code review process: pull requests, code quality checks (SonarQube)",
          "Feature Branching: Isolating new features for stability",
          "Industry benchmark: 40% reduction in bugs through code review (Studies)"
        ]
      }},
      {{
        "id": 3,
        "title": "Step 5: Monitoring and Feedback",
        "points": [
          "Performance monitoring: tracking key metrics (response time, error rate)",
          "Logging and alerting: identifying and responding to issues (Splunk, ELK)",
          "Continuous feedback: gathering user feedback to improve the product",
          "Mean Time To Recovery (MTTR): Reduce MTTR by 60% with monitoring"
        ]
      }},
      {{
        "id": 4,
        "title": "Conclusion: Embracing the CI/CD Culture",
        "points": [
          "CI/CD is more than tools: it's a cultural shift",
          "Collaboration: breaking down silos between development and operations",
          "Continuous improvement: regularly reviewing and improving the pipeline",
          "ROI: Companies with mature CI/CD see 2x more frequent deployments (DORA)"
        ]
      }}
    ]
  }}

  ### Content to Process:
\"\"\"
{content}
\"\"\"
"""
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)

    raw = response.text.strip()
    print(f"Gemini raw response: {raw}")

    if not raw:
        raise ValueError("Gemini response is empty or malformed.")

    try:
        cleaned = re.sub(r"^```json\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError as e:
        print(f"Failed to parse response as JSON: {e}")
        print(f"Returning raw response: {raw}")
        return raw



@app.route("/api/generate-mindmap", methods=["POST"])
def generate_mindmap_api():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Missing 'content' field in request body"}), 400

    content = data["content"]
    audience = data.get("audience")
    pages = data.get("pages")
    scenario = data.get("scenario")
    tone = data.get("tone")
    meetingDealSummarys = data.get("meeting_data", "")
    file_url = data.get("file_url")
    
    print(f"file_url: {file_url}")
    
    print(f"Received content: {content}")
    print(f"meetingDealSummarys: {meetingDealSummarys}")

    try:
        mindmap = get_mind_map_prompt(content, audience, pages, scenario, tone,meetingDealSummarys,file_url)
        return jsonify(mindmap)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/generate-deal-summary", methods=["POST"])
def generate_deal_summary():
    try:
        data = request.get_json()
        meeting_id = data.get("meeting_id")
        meeting_details = data.get("meeting_details")
        
        if not meeting_details:
            return jsonify({"error": "Missing meeting details"}), 400

        if not meeting_id:
            return jsonify({"error": "Missing meeting_id"}), 400

        transcripts = fetch_transcripts(db_config, meeting_id)

        if not transcripts:
            return jsonify({"error": "No transcripts found for this meeting"}), 404

        deal_summary = "    "

        return jsonify({"deal_summary": deal_summary}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8087)
