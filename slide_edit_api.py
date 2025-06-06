#!/usr/bin/env python3
"""
Slide Edit API Service

This service provides a REST API endpoint for editing PowerPoint slides using AI.
Send a slide with an edit prompt and get back the modified slide.

Usage:
    python slide_edit_api.py

Endpoints:
    POST /edit-slide - Edit a single slide
    POST /edit-slides - Edit multiple slides in batch
    GET /health - Health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback
from typing import Dict, Any, List
import json

# Import BAML client
try:
    from baml_client import b
except ImportError as e:
    print(f"Error importing BAML client: {e}")
    print("Make sure you have run 'pip install baml-py' and generated the BAML client")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class SlideEditService:
    """Service class for handling slide editing operations"""
    
    @staticmethod
    def convert_baml_result_to_dict(baml_result):
        """Convert BAML result objects to dictionaries for JSON serialization"""
        if hasattr(baml_result, 'model_dump'):
            return baml_result.model_dump()
        elif hasattr(baml_result, 'dict'):
            return baml_result.dict()
        else:
            # Manual conversion for BAML objects
            result_dict = {
                "slide_id": baml_result.slide_id,
                "background": baml_result.background,
                "content": []
            }
            
            for content_item in baml_result.content:
                if hasattr(content_item, 'model_dump'):
                    result_dict["content"].append(content_item.model_dump())
                elif hasattr(content_item, 'dict'):
                    result_dict["content"].append(content_item.dict())
                else:
                    # Manual conversion for content items
                    item_dict = {
                        "id": content_item.id,
                        "type": content_item.type,
                        "x": content_item.x,
                        "y": content_item.y,
                        "width": content_item.width,
                        "height": content_item.height
                    }
                    
                    # Add HTML content for HTML elements
                    if hasattr(content_item, 'html'):
                        item_dict["html"] = content_item.html
                    
                    # Add image properties for image elements
                    if hasattr(content_item, 'src'):
                        item_dict["src"] = content_item.src
                        item_dict["alt"] = content_item.alt
                        item_dict["caption"] = content_item.caption
                        item_dict["prompt"] = content_item.prompt
                        
                        # Convert style object
                        if hasattr(content_item, 'style') and content_item.style:
                            if hasattr(content_item.style, 'model_dump'):
                                item_dict["style"] = content_item.style.model_dump()
                            elif hasattr(content_item.style, 'dict'):
                                item_dict["style"] = content_item.style.dict()
                            else:
                                item_dict["style"] = {
                                    "borderRadius": content_item.style.borderRadius,
                                    "objectFit": content_item.style.objectFit,
                                    "marginBottom": content_item.style.marginBottom
                                }
                    
                    result_dict["content"].append(item_dict)
            
            return result_dict
    
    @staticmethod
    def validate_slide_data(slide_data: Dict[str, Any]) -> bool:
        """Validate that slide data has the required structure"""
        required_fields = ["slide_id", "background", "content"]
        
        if not all(field in slide_data for field in required_fields):
            return False
        
        if not isinstance(slide_data["content"], list):
            return False
        
        # Validate each content element
        for element in slide_data["content"]:
            required_element_fields = ["id", "type", "x", "y", "width", "height"]
            if not all(field in element for field in required_element_fields):
                return False
            
            # Check for html field in html elements
            if element["type"] == "html" and "html" not in element:
                return False
            
            # Check for image-specific fields (more flexible)
            if element["type"] == "image":
                # src is required for images
                if "src" not in element:
                    return False
                # alt_text or alt can be present (or neither)
                # Other image fields are optional
        
        return True
    
    @staticmethod
    def validate_edit_request(request_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate the edit request data"""
        if "slide" not in request_data:
            return False, "Missing 'slide' field in request"
        
        if "editPrompt" not in request_data:
            return False, "Missing 'editPrompt' field in request"
        
        if not SlideEditService.validate_slide_data(request_data["slide"]):
            return False, "Invalid slide data structure"
        
        if not isinstance(request_data["editPrompt"], str) or not request_data["editPrompt"].strip():
            return False, "editPrompt must be a non-empty string"
        
        # Theme is optional, default to "light"
        theme = request_data.get("theme", "light")
        if theme not in ["light", "dark"]:
            return False, "theme must be either 'light' or 'dark'"
        
        return True, ""

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Slide Edit API",
        "version": "1.0.0"
    })
    
    
def normalize_slide_data(slide_data):
    """
    Normalize slide data to match BAML schema expectations
    
    Args:
        slide_data: Dictionary containing slide information
    
    Returns:
        Dictionary with normalized slide data
    """
    normalized_slide = {
        "slide_id": slide_data["slide_id"],
        "background": slide_data["background"],
        "content": []
    }
    
    for element in slide_data["content"]:
        normalized_element = {
            "id": element["id"],
            "type": element["type"],
            "x": element["x"],
            "y": element["y"],
            "width": element["width"],
            "height": element["height"]
        }
        
        if element["type"] == "html":
            normalized_element["html"] = element["html"]
        elif element["type"] == "image":
            # Map fields to match BAML schema
            normalized_element["src"] = element["src"]
            normalized_element["alt"] = element.get("alt_text", element.get("alt", ""))
            normalized_element["caption"] = element.get("caption", "")
            normalized_element["prompt"] = element.get("prompt", "")
            
            # Handle style object - provide defaults if missing
            if "style" in element and element["style"]:
                normalized_element["style"] = element["style"]
            else:
                # Provide default style for images
                normalized_element["style"] = {
                    "borderRadius": "8px",
                    "objectFit": "cover",
                    "marginBottom": "20px"
                }
        
        normalized_slide["content"].append(normalized_element)
    
    return normalized_slide

def edit_slide_function(slide_data, edit_prompt, theme="light"):
    """
    Function to edit a single slide that can be called from other files
    
    Args:
        slide_data: Dictionary containing slide information
        edit_prompt: String describing the edit to be made
        theme: Theme for the slide ("light" or "dark"), defaults to "light"
    
    Returns:
        Dictionary containing the edited slide data and metadata
        
    Raises:
        ValueError: If input validation fails
        Exception: If BAML processing fails
    """
    
    print("edit_slide_function called with parameters:")
    print(f"slide_data: {json.dumps(slide_data, indent=2)}")
    print(f"edit_prompt: {edit_prompt}")
    print(f"theme: {theme}")
    # Validate input parameters
    if not isinstance(slide_data, dict) or not slide_data:
        raise ValueError("slide_data must be a non-empty dictionary")
    if not isinstance(edit_prompt, str) or not edit_prompt.strip():
        raise ValueError("edit_prompt must be a non-empty string")
    if theme not in ["light", "dark"]:
        raise ValueError("theme must be either 'light' or 'dark'")
        
        
        
    try:
        # Normalize slide data to match BAML schema
        normalized_slide_data = normalize_slide_data(slide_data)
        
        # Prepare request data for validation
        request_data = {
            "slide": normalized_slide_data,
            "editPrompt": edit_prompt,
            "theme": theme
        }
        
        # Validate request using the original validation (less strict)
        is_valid, error_message = SlideEditService.validate_edit_request({
            "slide": slide_data,
            "editPrompt": edit_prompt,
            "theme": theme
        })
        if not is_valid:
            raise ValueError(f"Invalid input: {error_message}")
        
        # Prepare BAML request with normalized data
        slide_edit_request = {
            "slide": normalized_slide_data,
            "editPrompt": edit_prompt,
            "theme": theme
        }
        
        logger.info(f"Processing slide edit request for slide_id: {normalized_slide_data['slide_id']}")
        logger.info(f"Edit prompt: {edit_prompt}")
        
        # Call BAML function
        result = b.EditSlide(slide_edit_request)
        
        logger.info("Slide edit completed successfully")
        
        # Convert BAML result to dictionary for JSON serialization
        edited_slide = SlideEditService.convert_baml_result_to_dict(result)
        
        return {
            "success": True,
            "editedSlide": edited_slide,
            "originalSlideId": slide_data["slide_id"],
            "editPrompt": edit_prompt,
            "theme": theme
        }
        
    except ValueError as ve:
        logger.error(f"Validation error in edit_slide_function: {str(ve)}")
        raise ve
    except Exception as e:
        logger.error(f"Error in edit_slide_function: {str(e)}")
        logger.error(traceback.format_exc())
        raise Exception(f"Internal error: {str(e)}")

@app.route('/edit-slide', methods=['POST'])
def edit_slide():
    """
    Edit a single slide based on the provided edit prompt
    
    Expected request body:
    {
        "slide": {
            "slide_id": "slide_10",
            "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
            "content": [
                {
                    "id": "s10_title",
                    "type": "html",
                    "x": 120,
                    "y": 40,
                    "width": 960,
                    "height": 60,
                    "html": "<h1 style='...'>Title</h1>"
                }
            ]
        },
        "editPrompt": "Change the title color to blue",
        "theme": "light"  // optional, defaults to "light"
    }
    """
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False
            }), 400
        
        # Use the new function
        result = edit_slide_function(
            slide_data=request_data["slide"],
            edit_prompt=request_data["editPrompt"],
            theme=request_data.get("theme", "light")
        )
        
        return jsonify(result)
        
    except ValueError as ve:
        return jsonify({
            "error": str(ve),
            "success": False
        }), 400
    except Exception as e:
        logger.error(f"Error editing slide: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/edit-slides', methods=['POST'])
def edit_slides():
    """
    Edit multiple slides in batch
    
    Expected request body:
    {
        "requests": [
            {
                "slide": { ... },
                "editPrompt": "...",
                "theme": "light"
            },
            ...
        ]
    }
    """
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False
            }), 400
        
        if "requests" not in request_data or not isinstance(request_data["requests"], list):
            return jsonify({
                "error": "Missing 'requests' field or it's not a list",
                "success": False
            }), 400
        
        if not request_data["requests"]:
            return jsonify({
                "error": "Empty requests list",
                "success": False
            }), 400
        
        # Validate each request
        for i, req in enumerate(request_data["requests"]):
            is_valid, error_message = SlideEditService.validate_edit_request(req)
            if not is_valid:
                return jsonify({
                    "error": f"Invalid request at index {i}: {error_message}",
                    "success": False
                }), 400
        
        logger.info(f"Processing batch edit for {len(request_data['requests'])} slides")
        
        # Call BAML function
        result = b.EditMultipleSlides(request_data["requests"])
        
        logger.info("Batch slide edit completed successfully")
        
        # Convert BAML results to dictionaries for JSON serialization
        edited_slides = [SlideEditService.convert_baml_result_to_dict(slide_result) for slide_result in result]
        
        return jsonify({
            "success": True,
            "editedSlides": edited_slides,
            "totalSlides": len(edited_slides)
        })
        
    except Exception as e:
        logger.error(f"Error editing slides: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/validate-edit', methods=['POST'])
def validate_edit():
    """
    Validate that an edit was applied correctly
    
    Expected request body:
    {
        "originalSlide": { ... },
        "editedSlide": { ... },
        "editPrompt": "..."
    }
    """
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False
            }), 400
        
        required_fields = ["originalSlide", "editedSlide", "editPrompt"]
        if not all(field in request_data for field in required_fields):
            return jsonify({
                "error": f"Missing required fields: {required_fields}",
                "success": False
            }), 400
        
        # Call BAML validation function
        is_valid = b.ValidateEditedSlide(
            request_data["originalSlide"],
            request_data["editedSlide"],
            request_data["editPrompt"]
        )
        
        return jsonify({
            "success": True,
            "isValid": is_valid,
            "editPrompt": request_data["editPrompt"]
        })
        
    except Exception as e:
        logger.error(f"Error validating edit: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "success": False,
        "available_endpoints": [
            "GET /health",
            "POST /edit-slide", 
            "POST /edit-slides",
            "POST /validate-edit"
        ]
    }), 404

# @app.errorhandler(405)
# def method_not_allowed(error):
#     """Handle 405 errors"""
#     return jsonify({
#         "error": "Method not allowed",
#         "success": False
#     }), 405


if __name__ == "__main__":
    app.run(port=8087, debug=True, threaded=True)
