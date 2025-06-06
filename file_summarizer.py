#!/usr/bin/env python3
"""
Standalone File Summarization Tool

This script provides file summarization functionality that can be used
independently of the Flask API.
"""

import requests
import os
import json
from urllib.parse import urlparse
import google.generativeai as genai

# Set up Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def extract_pdf_content(pdf_data):
    """Extract text from PDF data"""
    try:
        import PyPDF2
        from io import BytesIO
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
        content = ""
        
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        
        return content.strip()
    except ImportError:
        raise Exception("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2==3.0.1")
    except Exception as e:
        raise Exception(f"Failed to extract PDF content: {str(e)}")


def extract_docx_content(docx_data):
    """Extract text from DOCX data"""
    try:
        from docx import Document
        from io import BytesIO
        
        doc = Document(BytesIO(docx_data))
        content = ""
        
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        
        return content.strip()
    except ImportError:
        raise Exception("python-docx is required for DOCX processing. Install with: pip install python-docx==1.1.0")
    except Exception as e:
        raise Exception(f"Failed to extract DOCX content: {str(e)}")


def extract_html_content(html_text):
    """Extract text from HTML"""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        return soup.get_text(separator='\n').strip()
    except ImportError:
        # Fallback: simple HTML tag removal
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_text).strip()
    except Exception as e:
        # Fallback: simple HTML tag removal
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html_text).strip()


def extract_json_content(json_text):
    """Extract readable content from JSON"""
    try:
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


def generate_file_summary(content, summary_type="brief", max_length=500, file_info=None):
    """Generate AI summary of the file content"""
    
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY environment variable not set")
    
    if file_info is None:
        file_info = {}
    
    # Prepare the prompt based on summary type
    if summary_type == "brief":
        summary_instruction = f"Provide a brief, concise summary in {max_length} words or less that captures the main purpose and key information."
    elif summary_type == "detailed":
        summary_instruction = f"Provide a detailed summary in {max_length} words or less that covers the main topics, key findings, and important details."
    elif summary_type == "key_points":
        summary_instruction = f"Extract and list the key points, main findings, or important information in bullet format, using {max_length} words or less."
    else:
        summary_instruction = f"Provide a summary in {max_length} words or less."
    
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


def summarize_file_from_url(file_url, summary_type="brief", max_length=500):
    """
    Main function to summarize a file from URL
    
    Args:
        file_url (str): URL of the file to summarize
        summary_type (str): "brief", "detailed", or "key_points"
        max_length (int): Maximum words in summary
    
    Returns:
        dict: Summary result with file info
    """
    try:
        # Download and extract content
        content, file_info = download_and_extract_content(file_url)
        
        # Generate summary
        summary = generate_file_summary(content, summary_type, max_length, file_info)
        
        return {
            "success": True,
            "summary": summary,
            "file_info": file_info,
            "summary_type": summary_type,
            "content_length": len(content),
            "summary_length": len(summary.split())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_summarizer.py <file_url> [summary_type] [max_length]")
        print("Example: python file_summarizer.py https://example.com/document.pdf brief 300")
        sys.exit(1)
    
    file_url = sys.argv[1]
    summary_type = sys.argv[2] if len(sys.argv) > 2 else "brief"
    max_length = int(sys.argv[3]) if len(sys.argv) > 3 else 500
    
    print(f"Summarizing file: {file_url}")
    print(f"Summary type: {summary_type}")
    print(f"Max length: {max_length} words")
    print("-" * 50)
    
    result = summarize_file_from_url(file_url, summary_type, max_length)
    
    if result["success"]:
        print(f"Title: {result['file_info']['title']}")
        print(f"File type: {result['file_info']['file_type']}")
        print(f"File size: {result['file_info']['file_size']} bytes")
        print(f"Content length: {result['content_length']} characters")
        print("-" * 50)
        print("SUMMARY:")
        print(result["summary"])
        print("-" * 50)
        print(f"Summary length: {result['summary_length']} words")
    else:
        print(f"Error: {result['error']}")
