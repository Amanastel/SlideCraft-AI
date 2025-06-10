#!/usr/bin/env python3
"""
Test Different Data Structures
Compare what works vs what causes incomplete presentations
"""

import requests
import json

def test_simple_data_structure():
    """Test with simple data structure that might cause issues"""
    
    simple_data = {
        "prompt": "Create a presentation for FinCore Solutions",
        "presentation_data": {
            "title": "FinCore Solutions",
            "slides": [
                {"title": "Problem Statement"},
                {"title": "Our Solution"},
                {"title": "Market Opportunity"},
                {"title": "Next Steps"}
            ]
        }
    }
    
    print("🧪 Testing Simple Data Structure (4 slides)")
    print(f"📊 Input slides: {len(simple_data['presentation_data']['slides'])}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/generate-ppt",
            headers={"Content-Type": "application/json"},
            json=simple_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated: {result.get('filename')} ({result.get('file_size')} bytes)")
            return result.get('file_size')
        else:
            print(f"❌ Failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def test_detailed_data_structure():
    """Test with detailed data structure that should work well"""
    
    detailed_data = {
        "prompt": "Create a comprehensive sales presentation for FinCore Solutions",
        "presentation_data": {
            "title": "FinCore Solutions - Detailed Presentation",
            "slides": [
                {
                    "id": 1,
                    "title": "Market Problem Analysis", 
                    "content": "Financial institutions face significant challenges:\n• Manual processes consuming 40% of time\n• Delayed reporting causing decision lags\n• Compliance requiring extensive resources",
                    "objective": "Establish problem context"
                },
                {
                    "id": 2,
                    "title": "FinCore AI Solution",
                    "content": "Our platform delivers:\n• Automated document processing\n• Real-time risk analytics\n• Intelligent compliance reporting\n• Predictive market insights",
                    "objective": "Present comprehensive solution"
                },
                {
                    "id": 3,
                    "title": "Proven ROI Results",
                    "content": "Client achievements include:\n• 75% reduction in processing time\n• $2.3M average annual savings\n• 99.7% system uptime\n• 90% faster reporting cycles",
                    "objective": "Demonstrate value with metrics"
                },
                {
                    "id": 4,
                    "title": "Implementation Strategy",
                    "content": "90-day success plan:\n• Phase 1: System integration\n• Phase 2: AI model training\n• Phase 3: Team training and go-live\n• Ongoing optimization and support",
                    "objective": "Show clear path to value"
                }
            ],
            "strategic_plan": {
                "primary_cta": "Schedule a pilot program discussion",
                "target_audience": "Financial executives and decision-makers"
            }
        }
    }
    
    print("🧪 Testing Detailed Data Structure (4 slides with rich content)")
    print(f"📊 Input slides: {len(detailed_data['presentation_data']['slides'])}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5001/api/generate-ppt",
            headers={"Content-Type": "application/json"},
            json=detailed_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated: {result.get('filename')} ({result.get('file_size')} bytes)")
            return result.get('file_size')
        else:
            print(f"❌ Failed: {response.json()}")
            return None
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return None

def main():
    print("🔍 Data Structure Comparison Test")
    print("=" * 50)
    
    print("\n1. Testing Simple Structure (minimal content):")
    simple_size = test_simple_data_structure()
    
    print("\n2. Testing Detailed Structure (rich content):")
    detailed_size = test_detailed_data_structure()
    
    print("\n📊 COMPARISON RESULTS:")
    print("=" * 30)
    if simple_size and detailed_size:
        print(f"Simple structure file size:   {simple_size:,} bytes")
        print(f"Detailed structure file size: {detailed_size:,} bytes")
        print(f"Size difference: {detailed_size - simple_size:,} bytes ({((detailed_size - simple_size) / simple_size * 100):.1f}% larger)")
        
        print("\n💡 KEY INSIGHTS:")
        print("• Rich content in slides creates much larger, more comprehensive presentations")
        print("• Simple titles-only slides result in minimal presentations")
        print("• The original FinCore issue was likely due to minimal slide content")
        print("• Each slide should have detailed 'content' field with bullet points and explanations")
    else:
        print("❌ Could not complete comparison due to generation failures")

if __name__ == "__main__":
    main()
