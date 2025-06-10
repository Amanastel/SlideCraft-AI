#!/usr/bin/env python3
"""
Strategic Sales Presentation Outline Generator

This module provides functionality to generate strategic sales presentation outlines
using BAML (Boundary AI Markup Language) with advanced sales methodology.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from baml_client import b
from baml_client.types import DynamicInputContext, StrategicPresentationOutline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_json_string(json_str: str) -> bool:
    """Validate if a string is valid JSON"""
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def ensure_json_format(data: Any) -> str:
    """Ensure data is in proper JSON format"""
    if isinstance(data, dict):
        # If it's already a dict, convert to JSON string
        return json.dumps(data, indent=2)
    elif isinstance(data, str):
        # If it's a string, validate it's JSON and format it properly
        if validate_json_string(data):
            # Parse and re-format to ensure consistent formatting
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2)
        else:
            # If it's not valid JSON, wrap it in a JSON structure
            logger.warning("Data is not valid JSON, wrapping in JSON structure")
            return json.dumps({
                "raw_content": data,
                "note": "Original data was not in JSON format"
            }, indent=2)
    else:
        # For any other type, convert to JSON
        return json.dumps({
            "data": str(data),
            "note": "Data converted from non-string type"
        }, indent=2)


@dataclass
class PresentationRequest:
    """Data class for presentation generation requests."""
    content: str
    audience_type: Optional[str] = None
    scenario: Optional[str] = None
    tone: Optional[str] = None
    pages: Optional[str] = None
    meeting_deal_summary: Optional[str] = None
    file_context: Optional[str] = None


class StrategicOutlineGenerator:
    """
    Strategic Sales Presentation Outline Generator
    
    This class encapsulates the logic for generating comprehensive strategic
    sales presentation outlines using AI-powered analysis and proven sales
    methodologies.
    """
    
    def __init__(self):
        """Initialize the generator."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def generate_strategic_outline(self, request: PresentationRequest) -> Dict[str, Any]:
        """
        Generate a comprehensive strategic sales presentation outline.
        
        Args:
            request: PresentationRequest containing all input parameters
            
        Returns:
            Dict containing the strategic presentation outline
            
        Raises:
            Exception: If outline generation fails
        """
        try:
            # Process meeting deal summary to ensure JSON format
            processed_meeting_summary = None
            if request.meeting_deal_summary:
                processed_meeting_summary = ensure_json_format(request.meeting_deal_summary)
                self.logger.info("Meeting deal summary processed and validated as JSON")
            
            # Create input context
            input_context = DynamicInputContext(
                content=request.content,
                audience_type=request.audience_type,
                scenario=request.scenario,
                tone=request.tone,
                pages=request.pages,
                meeting_deal_summary=processed_meeting_summary,
                file_context=request.file_context
            )
            
            self.logger.info(f"Generating strategic outline for: {request.content[:100]}...")
            
            # Generate outline using BAML
            outline = b.GenerateStrategicSalesOutline(input_context)
            
            # Convert to dictionary for JSON serialization
            if hasattr(outline, 'model_dump'):
                result = outline.model_dump()
            else:
                result = outline.__dict__
                
            self.logger.info(f"Successfully generated outline with {len(result.get('slides', []))} slides")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate strategic outline: {str(e)}")
            raise Exception(f"Outline generation failed: {str(e)}")
    
    def generate_quick_outline(self, content: str, audience: Optional[str] = None, 
                             pages: Optional[str] = None, scenario: Optional[str] = None,
                             tone: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a quick presentation outline (for backward compatibility).
        
        Args:
            content: Main content for the presentation
            audience: Target audience
            pages: Number of pages/slides
            scenario: Presentation scenario
            tone: Desired tone
            
        Returns:
            Dict containing the presentation outline
        """
        try:
            self.logger.info(f"Generating quick outline for: {content[:100]}...")
            
            # Generate outline using BAML
            outline = b.GenerateQuickOutline(
                content=content,
                audience=audience,
                pages=pages,
                scenario=scenario,
                tone=tone
            )
            
            # Convert to dictionary for JSON serialization
            if hasattr(outline, 'model_dump'):
                result = outline.model_dump()
            else:
                result = outline.__dict__
                
            self.logger.info(f"Successfully generated quick outline")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate quick outline: {str(e)}")
            raise Exception(f"Quick outline generation failed: {str(e)}")




def extract_file_content(file_url: str) -> str:
    """
    Extract content from a file URL.
    
    Args:
        file_url: URL to the file
        
    Returns:
        Extracted text content
    """
    try:
        # Import here to avoid dependency issues if not needed
        import requests
        from urllib.parse import urlparse
        import tempfile
        import os
        
        # Download file
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()
        
        # Determine file type and extract content
        parsed_url = urlparse(file_url)
        file_extension = os.path.splitext(parsed_url.path)[1].lower()
        
        if file_extension == '.pdf':
            return extract_pdf_content(response.content)
        elif file_extension == '.docx':
            return extract_docx_content(response.content)
        elif file_extension in ['.txt', '.md']:
            return response.text
        else:
            # Try to decode as text
            return response.text
            
    except Exception as e:
        logger.error(f"Failed to extract file content from {file_url}: {str(e)}")
        return ""


def extract_pdf_content(pdf_data: bytes) -> str:
    """Extract text from PDF data."""
    try:
        import PyPDF2
        from io import BytesIO
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
        content = ""
        
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        
        return content.strip()
    except Exception as e:
        logger.error(f"Failed to extract PDF content: {str(e)}")
        return ""


def extract_docx_content(docx_data: bytes) -> str:
    """Extract text from DOCX data."""
    try:
        from docx import Document
        from io import BytesIO
        
        doc = Document(BytesIO(docx_data))
        content = ""
        
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        
        return content.strip()
    except Exception as e:
        logger.error(f"Failed to extract DOCX content: {str(e)}")
        return ""


def process_meeting_data(meeting_data: Dict[str, Any]) -> str:
    """
    Process meeting data into a structured summary.
    
    Args:
        meeting_data: Dictionary containing meeting information
        
    Returns:
        Formatted meeting summary string
    """
    if not meeting_data:
        return ""
    
    summary_parts = []
    
    # Extract key information
    if 'participants' in meeting_data:
        summary_parts.append(f"Participants: {', '.join(meeting_data['participants'])}")
    
    if 'key_points' in meeting_data:
        summary_parts.append(f"Key Discussion Points: {'; '.join(meeting_data['key_points'])}")
    
    if 'action_items' in meeting_data:
        summary_parts.append(f"Action Items: {'; '.join(meeting_data['action_items'])}")
    
    if 'next_steps' in meeting_data:
        summary_parts.append(f"Next Steps: {meeting_data['next_steps']}")
    
    return "\n".join(summary_parts)


# Example usage and testing functions
def test_strategic_outline():
    """Test the strategic outline generation."""
    generator = StrategicOutlineGenerator()
    
    request = PresentationRequest(
        content="I need a presentation to pitch our new AI-driven logistics software to a major retail company.",
        audience_type="Executive Leadership",
        scenario="First-time pitch to a new potential client",
        tone="Formal and data-driven",
        pages="10-12 slides",
        meeting_deal_summary="Previous meeting revealed their main pain point is 5-day delivery delays costing $3M annually. CFO is budget-conscious, VP Ops wants easy implementation.",
        file_context="Market research shows 73% of retailers are investing in AI logistics. Our solution reduces delivery time by 40% on average."
    )
    
    try:
        result = generator.generate_strategic_outline(request)
        print("Strategic Outline Generated Successfully!")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Number of slides: {len(result.get('slides', []))}")
        return result
    except Exception as e:
        print(f"Test failed: {e}")
        return None


def test_quick_outline():
    """Test the quick outline generation."""
    generator = StrategicOutlineGenerator()
    
    try:
        result = generator.generate_quick_outline(
            content="Create a presentation about implementing CI/CD pipelines",
            audience="Technical Leadership",
            pages="8 slides",
            scenario="Internal team presentation",
            tone="Technical and informative"
        )
        print("Quick Outline Generated Successfully!")
        print(f"Title: {result.get('title', 'N/A')}")
        return result
    except Exception as e:
        print(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    # Run tests
    print("Testing Strategic Outline Generator...")
    print("\n" + "="*50)
    print("Testing Strategic Outline Generation:")
    test_strategic_outline()
    
    print("\n" + "="*50)
    print("Testing Quick Outline Generation:")
    test_quick_outline()
