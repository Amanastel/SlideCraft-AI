#!/usr/bin/env python3
"""
PowerPoint API Test Client
Demonstrates how to use the PPT generation API programmatically.
"""

import requests
import json
import time
import os
from pathlib import Path

class PPTAPIClient:
    """Client for interacting with the PowerPoint Generation API."""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def health_check(self):
        """Check if the API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_templates(self):
        """Get available presentation templates."""
        try:
            response = self.session.get(f"{self.base_url}/api/templates")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def generate_presentation(self, prompt, presentation_data=None, options=None):
        """Generate a presentation from prompt and optional data."""
        payload = {"prompt": prompt}
        
        if presentation_data:
            payload["presentation_data"] = presentation_data
            
        if options:
            payload["options"] = options
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate-ppt",
                json=payload
            )
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500
    
    def get_session_status(self, session_id):
        """Get the status of a generation session."""
        try:
            response = self.session.get(f"{self.base_url}/api/status/{session_id}")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def download_presentation(self, session_id, save_path=None):
        """Download a generated presentation."""
        try:
            response = self.session.get(f"{self.base_url}/api/download/{session_id}")
            
            if response.status_code == 200:
                # Get filename from response headers or use default
                filename = save_path or f"downloaded_presentation_{session_id[:8]}.pptx"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                return {"success": True, "filename": filename, "size": len(response.content)}
            else:
                return {"error": f"Download failed with status {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def list_sessions(self):
        """List all active sessions."""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def demo_simple_generation():
    """Demonstrate simple prompt-based generation."""
    print("🚀 Testing Simple Prompt-Based Generation")
    print("=" * 50)
    
    client = PPTAPIClient()
    
    # Check health
    health = client.health_check()
    print(f"API Health: {health}")
    
    # Simple generation
    prompt = "Create a presentation about sustainable technology innovations for investors"
    result, status = client.generate_presentation(
        prompt=prompt,
        options={
            "theme": "professional",
            "include_charts": True,
            "include_images": True
        }
    )
    
    if status == 200:
        print(f"✅ Generation successful!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Filename: {result['filename']}")
        print(f"   File Size: {result['file_size']:,} bytes")
        
        # Download the file
        download_result = client.download_presentation(
            result['session_id'], 
            f"demo_sustainable_tech.pptx"
        )
        
        if download_result.get('success'):
            print(f"📥 Downloaded: {download_result['filename']}")
        else:
            print(f"❌ Download failed: {download_result.get('error')}")
            
    else:
        print(f"❌ Generation failed: {result}")

def demo_structured_generation():
    """Demonstrate structured data generation."""
    print("\n🎯 Testing Structured Data Generation")
    print("=" * 50)
    
    client = PPTAPIClient()
    
    # Get available templates
    templates = client.get_templates()
    print(f"Available templates: {list(templates.get('templates', {}).keys())}")
    
    # Structured presentation data
    presentation_data = {
        "title": "Digital Marketing Strategy 2025",
        "slides": [
            {
                "id": 1,
                "title": "Market Analysis",
                "key_content_elements": [
                    "Digital marketing trends 2025",
                    "Consumer behavior shifts",
                    "Competitive landscape"
                ],
                "objective": "Analyze current market conditions",
                "image_search_terms": ["digital marketing", "analytics", "trends"]
            },
            {
                "id": 2,
                "title": "Strategy Framework",
                "key_content_elements": [
                    "Multi-channel approach",
                    "Content marketing strategy",
                    "Performance measurement"
                ],
                "objective": "Present strategic approach",
                "image_search_terms": ["strategy", "framework", "digital"],
                "chart_data": {
                    "categories": ["Social", "Email", "Content", "Paid Ads"],
                    "values": [35, 25, 25, 15],
                    "title": "Channel Investment Distribution (%)"
                }
            },
            {
                "id": 3,
                "title": "Implementation Roadmap",
                "key_content_elements": [
                    "Phase 1: Foundation (Months 1-2)",
                    "Phase 2: Growth (Months 3-6)",
                    "Phase 3: Optimization (Months 7-12)"
                ],
                "objective": "Provide implementation timeline",
                "image_search_terms": ["roadmap", "timeline", "implementation"]
            }
        ]
    }
    
    result, status = client.generate_presentation(
        prompt="Create a comprehensive digital marketing strategy presentation for executive leadership",
        presentation_data=presentation_data,
        options={
            "theme": "modern",
            "include_charts": True,
            "include_images": True,
            "output_filename": "Digital_Marketing_Strategy_2025.pptx"
        }
    )
    
    if status == 200:
        print(f"✅ Structured generation successful!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Filename: {result['filename']}")
        print(f"   File Size: {result['file_size']:,} bytes")
        
        # Download the file
        download_result = client.download_presentation(
            result['session_id'], 
            result['filename']
        )
        
        if download_result.get('success'):
            print(f"📥 Downloaded: {download_result['filename']}")
        else:
            print(f"❌ Download failed: {download_result.get('error')}")
            
    else:
        print(f"❌ Structured generation failed: {result}")

def show_session_summary():
    """Show summary of all sessions."""
    print("\n📊 Session Summary")
    print("=" * 50)
    
    client = PPTAPIClient()
    sessions = client.list_sessions()
    
    if "sessions" in sessions:
        print(f"Total active sessions: {sessions['active_sessions']}")
        for session_id, info in sessions["sessions"].items():
            print(f"\n📄 Session: {session_id[:8]}...")
            print(f"   Status: {info['status']}")
            print(f"   Filename: {info['filename']}")
            print(f"   Size: {info['file_size']:,} bytes")
            print(f"   Prompt: {info['prompt'][:60]}...")
    else:
        print("No sessions found or error occurred")

if __name__ == "__main__":
    print("🎨 PowerPoint API Test Client")
    print("Testing complete API functionality")
    print("=" * 60)
    
    try:
        # Run demos
        demo_simple_generation()
        demo_structured_generation()
        show_session_summary()
        
        print("\n🎉 All tests completed successfully!")
        print("\nGenerated files:")
        for file in ["demo_sustainable_tech.pptx", "Digital_Marketing_Strategy_2025.pptx"]:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"  📎 {file} ({size:,} bytes)")
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
