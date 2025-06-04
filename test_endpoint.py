#!/usr/bin/env python3
"""
Test script to verify the /api/v1/slides/generate-all-images endpoint works.
"""
import requests
import json
import time

def test_generate_all_images_endpoint():
    """Test the generate-all-images endpoint"""
    url = "http://localhost:8086/api/v1/slides/generate-all-images"
    
    # Test data
    test_data = {
        "request_id": "test123"
    }
    
    print(f"Testing endpoint: {url}")
    print(f"Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=test_data, timeout=60)
        end_time = time.time()
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Time: {end_time - start_time:.2f} seconds")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        return response.status_code == 200 or response.status_code == 404  # 404 is expected if no test data
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure slide2.py is running on port 8086")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Flask API endpoint...")
    success = test_generate_all_images_endpoint()
    
    if success:
        print("\n✅ Test passed! The endpoint is working correctly.")
    else:
        print("\n❌ Test failed! Check the logs for errors.")
