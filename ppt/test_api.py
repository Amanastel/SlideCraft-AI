#!/usr/bin/env python3
"""
PowerPoint API Test Client
Clean and simple test for the enhanced PPT generation API
"""

import requests
import json
import time

class PPTAPITester:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        
    def test_health(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def test_simple_presentation(self):
        """Test basic presentation generation"""
        data = {
            "prompt": "Create a business presentation about our quarterly results",
            "slides": [
                {
                    "type": "title",
                    "title": "Q4 Business Results",
                    "subtitle": "Performance Review and Strategic Outlook"
                },
                {
                    "type": "content",
                    "title": "Key Achievements",
                    "content": "Revenue increased by 25% this quarter. Customer satisfaction reached 4.5/5 stars. Team productivity improved significantly with new tools and processes."
                },
                {
                    "type": "content",
                    "title": "Strategic Next Steps",
                    "content": "Focus on market expansion in Q1. Invest in technology infrastructure. Launch new product features based on customer feedback."
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate-ppt",
                headers={"Content-Type": "application/json"},
                json=data
            )
            
            print(f"Generation Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                print(f"✅ Presentation generated successfully!")
                print(f"📁 File: {result.get('filename')}")
                print(f"📊 Size: {result.get('file_size')} bytes")
                return True
            else:
                print(f"❌ Generation failed: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"Test failed: {e}")
            return False

def main():
    print("🧪 PowerPoint API Test Suite")
    print("=" * 40)
    
    tester = PPTAPITester()
    
    # Test health
    print("\n1. Testing API Health...")
    if not tester.test_health():
        print("❌ API is not healthy. Please check the server.")
        return
    
    # Test presentation generation
    print("\n2. Testing Presentation Generation...")
    if tester.test_simple_presentation():
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")

if __name__ == "__main__":
    main()
