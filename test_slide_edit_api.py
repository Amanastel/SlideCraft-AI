#!/usr/bin/env python3
"""
Test script for the Slide Edit API

This script demonstrates how to use the slide editing API with example requests.
"""

import requests
import json
import time

# API base URL
API_BASE = "http://localhost:8087"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_single_slide_edit():
    """Test editing a single slide"""
    print("\n📝 Testing single slide edit...")
    
    # Sample slide data matching your format
    slide_data = {
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
                    "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Summary: Transforming Customer Engagement with AI</h1>"
                },
                {
                    "id": "s10_para",
                    "type": "html",
                    "x": 100,
                    "y": 150,
                    "width": 800,
                    "height": 300,
                    "html": "<p style='font-size:22px;line-height:1.55'>Our AI-powered solution is designed to revolutionize your customer engagement strategy. By leveraging personalized recommendations, AI-powered chatbots, and predictive analytics, you can deliver exceptional customer experiences, improve customer retention rates, and drive revenue growth.</p>"
                }
            ]
        },
        "editPrompt": "Change the title color to blue and make the paragraph text smaller",
        "theme": "light"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/edit-slide",
            headers={"Content-Type": "application/json"},
            json=slide_data
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Slide edit successful!")
            print("📋 Original slide ID:", result.get("originalSlideId"))
            print("📝 Edit prompt:", result.get("editPrompt"))
            print("🎨 Theme:", result.get("theme"))
            print("📄 Edited slide structure:")
            edited_slide = result.get("editedSlide", {})
            print(f"   Slide ID: {edited_slide.get('slide_id')}")
            print(f"   Background: {edited_slide.get('background')}")
            print(f"   Content elements: {len(edited_slide.get('content', []))}")
            
            # Show the HTML content of the first element to see changes
            if edited_slide.get('content'):
                first_element = edited_slide['content'][0]
                print(f"   First element HTML: {first_element.get('html', '')[:100]}...")
                
            return True
        else:
            print(f"❌ Slide edit failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_batch_slide_edit():
    """Test editing multiple slides"""
    print("\n📝 Testing batch slide edit...")
    
    # Sample data for batch editing
    batch_data = {
        "requests": [
            {
                "slide": {
                    "slide_id": "slide_1",
                    "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
                    "content": [
                        {
                            "id": "s1_title",
                            "type": "html",
                            "x": 120,
                            "y": 40,
                            "width": 960,
                            "height": 60,
                            "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>First Slide Title</h1>"
                        }
                    ]
                },
                "editPrompt": "Change title color to red",
                "theme": "light"
            },
            {
                "slide": {
                    "slide_id": "slide_2",
                    "background": "linear-gradient(135deg,#ffffff,#f0f4f8)",
                    "content": [
                        {
                            "id": "s2_title",
                            "type": "html",
                            "x": 120,
                            "y": 40,
                            "width": 960,
                            "height": 60,
                            "html": "<h1 style='text-align:center;font-size:46px;color:#2c3e50'>Second Slide Title</h1>"
                        }
                    ]
                },
                "editPrompt": "Change title color to green",
                "theme": "light"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/edit-slides",
            headers={"Content-Type": "application/json"},
            json=batch_data
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Batch slide edit successful!")
            print(f"📄 Total slides processed: {result.get('totalSlides')}")
            return True
        else:
            print(f"❌ Batch slide edit failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_invalid_request():
    """Test error handling with invalid request"""
    print("\n🚫 Testing error handling...")
    
    invalid_data = {
        "slide": {
            "slide_id": "test",
            # Missing required fields
        },
        "editPrompt": ""  # Empty prompt
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/edit-slide",
            headers={"Content-Type": "application/json"},
            json=invalid_data
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if response.status_code == 400:
            print("✅ Error handling works correctly!")
            print(f"Error message: {result.get('error')}")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Slide Edit API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Single Slide Edit", test_single_slide_edit),
        ("Batch Slide Edit", test_batch_slide_edit),
        ("Error Handling", test_invalid_request)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API server and try again.")

if __name__ == "__main__":
    print("📋 Slide Edit API Test Suite")
    print("🔗 Make sure the API server is running on http://localhost:5000")
    print("💡 Start the server with: python slide_edit_api.py")
    
    input("\nPress Enter to start tests...")
    main()
