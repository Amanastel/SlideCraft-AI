#!/usr/bin/env python3
"""
PowerPoint Generation API
Flask API endpoint for generating presentations from data and prompts.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, Any

# Import your existing PPT generator
try:
    from prompt_based_ppt_generator import AdvancedPPTGenerator
    PPT_GENERATOR_AVAILABLE = True
except ImportError:
    PPT_GENERATOR_AVAILABLE = False
    print("⚠️  PPT Generator not available. Please check imports.")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'generated_presentations'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
ALLOWED_EXTENSIONS = {'.pptx'}

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class PPTGenerationAPI:
    """Main API class for handling PPT generation requests."""
    
    def __init__(self):
        self.generator = AdvancedPPTGenerator() if PPT_GENERATOR_AVAILABLE else None
        self.active_sessions = {}
    
    def validate_request_data(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate incoming request data - flexible validation for any JSON structure."""
        
        # Check required fields
        required_fields = ['prompt']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # Validate prompt
        if not isinstance(data['prompt'], str) or len(data['prompt'].strip()) == 0:
            return False, "Prompt must be a non-empty string"
        
        if len(data['prompt']) > 2000:  # Increased limit for more flexibility
            return False, "Prompt must be less than 2000 characters"
        
        # Flexible validation for presentation data
        if 'presentation_data' in data:
            if not isinstance(data['presentation_data'], dict):
                return False, "presentation_data must be a JSON object"
            
            # If slides are provided, validate basic structure
            pres_data = data['presentation_data']
            if 'slides' in pres_data:
                if not isinstance(pres_data['slides'], list):
                    return False, "slides must be an array"
                
                # Validate each slide has at minimum a title or content
                for i, slide in enumerate(pres_data['slides']):
                    if not isinstance(slide, dict):
                        return False, f"Slide {i+1} must be an object"
                    
                    # Flexible requirement - slide can have title, content, or both
                    if not any(key in slide for key in ['title', 'content', 'key_content_elements']):
                        return False, f"Slide {i+1} must have at least 'title', 'content', or 'key_content_elements'"
        
        return True, "Valid"
    
    def create_default_presentation_data(self, prompt: str) -> Dict[str, Any]:
        """Create default presentation structure if none provided."""
        
        # Extract key themes from prompt for default slides
        prompt_lower = prompt.lower()
        
        # Determine presentation type based on prompt keywords
        if any(word in prompt_lower for word in ['sales', 'pitch', 'revenue', 'customer']):
            template_type = 'sales'
        elif any(word in prompt_lower for word in ['tech', 'innovation', 'ai', 'technology']):
            template_type = 'tech'
        elif any(word in prompt_lower for word in ['business', 'strategy', 'corporate']):
            template_type = 'business'
        else:
            template_type = 'general'
        
        templates = {
            'sales': {
                "title": "Sales Presentation",
                "slides": [
                    {
                        "id": 1,
                        "title": "Market Opportunity",
                        "key_content_elements": [
                            "Growing market demand",
                            "Target customer analysis",
                            "Competitive landscape overview"
                        ],
                        "objective": "Establish market context",
                        "image_search_terms": ["business growth", "market opportunity"]
                    },
                    {
                        "id": 2,
                        "title": "Our Solution",
                        "key_content_elements": [
                            "Unique value proposition",
                            "Key features and benefits",
                            "Competitive advantages"
                        ],
                        "objective": "Present solution",
                        "image_search_terms": ["innovation", "solution", "technology"]
                    },
                    {
                        "id": 3,
                        "title": "Results & ROI",
                        "key_content_elements": [
                            "Customer success stories",
                            "Quantifiable benefits",
                            "Return on investment"
                        ],
                        "objective": "Demonstrate value",
                        "image_search_terms": ["success", "growth", "results"],
                        "chart_data": {
                            "categories": ["Before", "After", "Future"],
                            "values": [25, 65, 90]
                        }
                    }
                ]
            },
            'tech': {
                "title": "Technology Innovation Presentation",
                "slides": [
                    {
                        "id": 1,
                        "title": "Technical Challenge",
                        "key_content_elements": [
                            "Current limitations",
                            "Technical requirements",
                            "Innovation opportunity"
                        ],
                        "objective": "Define the problem",
                        "image_search_terms": ["technology", "innovation", "challenge"]
                    },
                    {
                        "id": 2,
                        "title": "Our Technical Solution",
                        "key_content_elements": [
                            "Architecture overview",
                            "Key technologies used",
                            "Implementation approach"
                        ],
                        "objective": "Present technical solution",
                        "image_search_terms": ["software", "architecture", "technology stack"]
                    }
                ]
            },
            'business': {
                "title": "Business Strategy Presentation",
                "slides": [
                    {
                        "id": 1,
                        "title": "Strategic Overview",
                        "key_content_elements": [
                            "Business objectives",
                            "Market analysis",
                            "Strategic priorities"
                        ],
                        "objective": "Set strategic context",
                        "image_search_terms": ["business strategy", "corporate", "planning"]
                    },
                    {
                        "id": 2,
                        "title": "Implementation Plan",
                        "key_content_elements": [
                            "Key initiatives",
                            "Timeline and milestones",
                            "Success metrics"
                        ],
                        "objective": "Present execution plan",
                        "image_search_terms": ["planning", "execution", "business process"]
                    }
                ]
            },
            'general': {
                "title": "Presentation",
                "slides": [
                    {
                        "id": 1,
                        "title": "Overview",
                        "key_content_elements": [
                            "Key topic introduction",
                            "Main objectives",
                            "Expected outcomes"
                        ],
                        "objective": "Introduce topic",
                        "image_search_terms": ["presentation", "business", "professional"]
                    },
                    {
                        "id": 2,
                        "title": "Details",
                        "key_content_elements": [
                            "Important information",
                            "Supporting details",
                            "Key insights"
                        ],
                        "objective": "Provide details",
                        "image_search_terms": ["information", "data", "insights"]
                    }
                ]
            }
        }
        
        default_data = templates.get(template_type, templates['general'])
        default_data["strategic_plan"] = {
            "primary_cta": "Let's discuss next steps and how we can move forward together"
        }
        
        return default_data

# Initialize API instance
ppt_api = PPTGenerationAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ppt_generator_available": PPT_GENERATOR_AVAILABLE
    }), 200

@app.route('/api/generate-ppt', methods=['POST'])
def generate_presentation():
    """
    Generate PowerPoint presentation from prompt and data.
    
    Expected JSON payload:
    {
        "prompt": "Create a sales presentation with modern visuals",
        "presentation_data": {
            "title": "My Presentation",
            "slides": [...],
            "strategic_plan": {...}
        },
        "options": {
            "theme": "professional",
            "output_filename": "custom_name.pptx",
            "include_charts": true,
            "include_images": true
        }
    }
    """
    
    try:
        # Check if PPT generator is available
        if not PPT_GENERATOR_AVAILABLE:
            return jsonify({
                "error": "PPT generation service not available",
                "message": "Please check server configuration"
            }), 503
        
        # Get JSON data from request
        if not request.is_json:
            return jsonify({
                "error": "Invalid request format",
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        # Validate request data
        is_valid, validation_message = ppt_api.validate_request_data(data)
        if not is_valid:
            return jsonify({
                "error": "Invalid request data",
                "message": validation_message
            }), 400
        
        # Extract parameters
        prompt = data['prompt'].strip()
        presentation_data = data.get('presentation_data')
        options = data.get('options', {})
        
        # Use provided data or create default
        if presentation_data:
            ppt_data = presentation_data
        else:
            logger.info("No presentation data provided, creating default template")
            ppt_data = ppt_api.create_default_presentation_data(prompt)
        
        # Extract options
        theme = options.get('theme', 'professional')
        include_charts = options.get('include_charts', True)
        include_images = options.get('include_images', True)
        custom_filename = options.get('output_filename')
        
        # Generate unique session ID and filename
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_filename:
            # Ensure it ends with .pptx
            if not custom_filename.endswith('.pptx'):
                custom_filename += '.pptx'
            output_filename = custom_filename
        else:
            output_filename = f"presentation_{timestamp}_{session_id[:8]}.pptx"
        
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        logger.info(f"Generating presentation: {output_filename}")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Theme: {theme}")
        
        # Store session info
        ppt_api.active_sessions[session_id] = {
            "status": "generating",
            "filename": output_filename,
            "prompt": prompt,
            "started_at": datetime.now().isoformat()
        }
        
        # Generate presentation
        try:
            result_file = ppt_api.generator.generate_presentation_from_prompt(
                prompt=prompt,
                input_data=ppt_data,
                output_filename=output_path
            )
            
            # Check if file was created
            if os.path.exists(result_file):
                file_size = os.path.getsize(result_file)
                
                # Update session status
                ppt_api.active_sessions[session_id].update({
                    "status": "completed",
                    "file_size": file_size,
                    "completed_at": datetime.now().isoformat()
                })
                
                logger.info(f"Presentation generated successfully: {output_filename} ({file_size} bytes)")
                
                return jsonify({
                    "success": True,
                    "message": "Presentation generated successfully",
                    "session_id": session_id,
                    "filename": output_filename,
                    "file_size": file_size,
                    "download_url": f"/api/download/{session_id}",
                    "preview_url": f"/api/preview/{session_id}",
                    "generated_at": datetime.now().isoformat()
                }), 200
            else:
                raise Exception("Presentation file was not created")
                
        except Exception as gen_error:
            logger.error(f"Presentation generation failed: {str(gen_error)}")
            
            # Update session status
            ppt_api.active_sessions[session_id].update({
                "status": "failed",
                "error": str(gen_error),
                "failed_at": datetime.now().isoformat()
            })
            
            return jsonify({
                "error": "Presentation generation failed",
                "message": str(gen_error),
                "session_id": session_id
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/download/<session_id>', methods=['GET'])
def download_presentation(session_id):
    """Download generated presentation file."""
    
    try:
        # Check if session exists
        if session_id not in ppt_api.active_sessions:
            return jsonify({
                "error": "Session not found",
                "message": f"No presentation found for session {session_id}"
            }), 404
        
        session_info = ppt_api.active_sessions[session_id]
        
        # Check if generation completed successfully
        if session_info['status'] != 'completed':
            return jsonify({
                "error": "Presentation not ready",
                "message": f"Presentation status: {session_info['status']}",
                "session_info": session_info
            }), 400
        
        filename = session_info['filename']
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                "error": "File not found",
                "message": f"Presentation file {filename} not found on server"
            }), 404
        
        # Send file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({
            "error": "Download failed",
            "message": str(e)
        }), 500

@app.route('/api/status/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """Get status of presentation generation session."""
    
    if session_id not in ppt_api.active_sessions:
        return jsonify({
            "error": "Session not found",
            "message": f"No session found with ID {session_id}"
        }), 404
    
    session_info = ppt_api.active_sessions[session_id]
    return jsonify({
        "session_id": session_id,
        "status": session_info['status'],
        "session_info": session_info
    }), 200

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """List all active sessions."""
    
    return jsonify({
        "active_sessions": len(ppt_api.active_sessions),
        "sessions": ppt_api.active_sessions
    }), 200

@app.route('/api/preview/<session_id>', methods=['GET'])
def preview_presentation(session_id):
    """Get preview information about generated presentation."""
    
    try:
        if session_id not in ppt_api.active_sessions:
            return jsonify({
                "error": "Session not found"
            }), 404
        
        session_info = ppt_api.active_sessions[session_id]
        
        if session_info['status'] != 'completed':
            return jsonify({
                "error": "Presentation not ready",
                "status": session_info['status']
            }), 400
        
        filename = session_info['filename']
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "error": "File not found"
            }), 404
        
        # Get file info
        file_stats = os.stat(file_path)
        
        return jsonify({
            "session_id": session_id,
            "filename": filename,
            "file_size": file_stats.st_size,
            "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            "prompt": session_info.get('prompt', ''),
            "download_url": f"/api/download/{session_id}",
            "status": session_info['status']
        }), 200
        
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return jsonify({
            "error": "Preview failed",
            "message": str(e)
        }), 500

@app.route('/api/templates', methods=['GET'])
def get_available_templates():
    """Get list of available presentation templates."""
    
    templates = {
        "sales": {
            "name": "Sales Presentation",
            "description": "Professional sales pitch with market analysis, solution overview, and ROI",
            "slides": ["Market Opportunity", "Our Solution", "Results & ROI"]
        },
        "tech": {
            "name": "Technology Innovation",
            "description": "Technical presentation for innovation and solution architecture",
            "slides": ["Technical Challenge", "Our Technical Solution"]
        },
        "business": {
            "name": "Business Strategy",
            "description": "Corporate strategy presentation with objectives and implementation",
            "slides": ["Strategic Overview", "Implementation Plan"]
        },
        "general": {
            "name": "General Presentation",
            "description": "Flexible template for any topic",
            "slides": ["Overview", "Details"]
        }
    }
    
    return jsonify({
        "templates": templates,
        "themes": ["professional", "modern", "corporate"]
    }), 200

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": "File too large",
        "message": "Request exceeds maximum size limit"
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    # Development server
    print("🚀 Starting PowerPoint Generation API Server")
    print("=" * 50)
    print(f"📁 Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🤖 PPT Generator available: {PPT_GENERATOR_AVAILABLE}")
    print(f"🌐 API will be available at: http://localhost:5001")
    print("\n📋 Available endpoints:")
    print("  POST /api/generate-ppt  - Generate presentation")
    print("  GET  /api/download/<id> - Download presentation")
    print("  GET  /api/status/<id>   - Check generation status")
    print("  GET  /api/sessions      - List all sessions")
    print("  GET  /api/templates     - Get available templates")
    print("  GET  /health            - Health check")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
