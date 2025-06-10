#!/usr/bin/env python3
"""
Debug FinCore Presentation Generation
Test comprehensive FinCore data to fix incomplete slide generation
"""

import requests
import json
import time

def test_comprehensive_fincore_presentation():
    """Test with complete FinCore data structure that should generate 12+ slides"""
    
    # Complete FinCore presentation data with 12 slides
    comprehensive_fincore_data = {
        "prompt": "Create a comprehensive sales presentation for FinCore Solutions showcasing our AI-powered financial technology solutions",
        "presentation_data": {
            "title": "FinCore Solutions - AI-Powered Financial Technology Platform",
            "slides": [
                {
                    "id": 1,
                    "title": "The Hidden Cost of Manual Financial Processes",
                    "content": """Financial institutions are losing competitive advantage due to:
• Manual data entry consuming 40% of analyst time
• Delayed reporting causing 3-day decision lags
• Inconsistent risk assessments across portfolios
• Regulatory compliance requiring 50+ hours weekly
• Legacy systems creating data silos and inefficiencies""",
                    "objective": "Highlight pain points in current financial operations",
                    "image_search_terms": ["financial stress", "manual processes", "inefficiency"]
                },
                {
                    "id": 2,
                    "title": "Vision: Automated Financial Excellence",
                    "content": """Imagine a financial institution where:
• Real-time risk analysis happens in seconds, not days
• Compliance reporting is automated and error-free
• Portfolio optimization runs continuously 24/7
• Predictive analytics prevent financial losses
• Decision-makers have instant access to actionable insights""",
                    "objective": "Present the promised land vision",
                    "image_search_terms": ["financial technology", "automation", "success"]
                },
                {
                    "id": 3,
                    "title": "FinCore AI Platform: Your Bridge to Transformation",
                    "content": """Our comprehensive AI-powered platform delivers:
• Intelligent Document Processing: 95% accuracy in data extraction
• Real-time Risk Analytics: Instant portfolio health monitoring
• Automated Compliance: Regulatory reporting in one click
• Predictive Market Intelligence: Anticipate trends before competitors
• Seamless Legacy Integration: Connect existing systems effortlessly""",
                    "objective": "Showcase specific features and benefits",
                    "image_search_terms": ["AI platform", "financial dashboard", "technology"]
                },
                {
                    "id": 4,
                    "title": "Proven Results: $2.3M Average ROI in First Year",
                    "content": """Our clients consistently achieve remarkable outcomes:
• 75% reduction in manual processing time
• 90% faster regulatory reporting cycles
• 40% improvement in risk prediction accuracy
• $2.3M average annual cost savings
• 99.7% system uptime with enterprise-grade security""",
                    "objective": "Provide quantifiable social proof",
                    "image_search_terms": ["financial charts", "ROI graphs", "success metrics"],
                    "chart_data": {
                        "type": "bar",
                        "title": "Client ROI Achievements",
                        "categories": ["Cost Savings", "Time Reduction", "Accuracy Improvement", "Compliance Speed"],
                        "values": [2300000, 75, 40, 90]
                    }
                },
                {
                    "id": 5,
                    "title": "Client Success: Global Bank Transformation",
                    "content": """Case Study - International Banking Group:
• Challenge: Manual compliance consuming 200 hours/week
• Solution: FinCore AI Compliance Suite implementation
• Results: 85% reduction in compliance workload
• Impact: $1.8M annual savings, 99% audit success rate
• Timeline: Full implementation completed in 90 days""",
                    "objective": "Provide detailed social proof with storytelling",
                    "image_search_terms": ["banking success", "financial transformation", "case study"]
                },
                {
                    "id": 6,
                    "title": "Advanced AI Capabilities: Beyond Traditional FinTech",
                    "content": """What sets FinCore apart from competitors:
• Natural Language Processing for document analysis
• Machine Learning models trained on 10B+ financial transactions
• Predictive analytics with 94% accuracy rates
• Real-time fraud detection and prevention
• Custom AI model development for unique use cases""",
                    "objective": "Differentiate from competitors with technical excellence",
                    "image_search_terms": ["AI technology", "machine learning", "advanced analytics"]
                },
                {
                    "id": 7,
                    "title": "Enterprise Security: Bank-Grade Protection",
                    "content": """Security features that exceed industry standards:
• SOC 2 Type II and ISO 27001 certified infrastructure
• End-to-end encryption for all data transmissions
• Multi-factor authentication with biometric options
• Regular penetration testing and vulnerability assessments
• GDPR and regional compliance built-in""",
                    "objective": "Address security and compliance concerns",
                    "image_search_terms": ["cybersecurity", "financial security", "compliance"]
                },
                {
                    "id": 8,
                    "title": "Implementation Strategy: 90-Day Success Plan",
                    "content": """Our proven implementation methodology:
• Phase 1 (Days 1-30): System integration and data migration
• Phase 2 (Days 31-60): AI model training and customization
• Phase 3 (Days 61-90): Team training and go-live support
• Dedicated project manager and technical support team
• 24/7 monitoring during transition period""",
                    "objective": "Present clear path to value realization",
                    "image_search_terms": ["project timeline", "implementation plan", "success roadmap"]
                },
                {
                    "id": 9,
                    "title": "Investment Options: Flexible Pricing for Every Scale",
                    "content": """Pricing designed to maximize your ROI:
• Starter Package: $50K annually (up to 100 users)
• Professional Package: $150K annually (up to 500 users)
• Enterprise Package: $300K annually (unlimited users)
• Custom solutions available for unique requirements
• First 60 days risk-free with money-back guarantee""",
                    "objective": "Present pricing and demonstrate value",
                    "image_search_terms": ["pricing strategy", "investment options", "financial planning"]
                },
                {
                    "id": 10,
                    "title": "Technical Integration: Seamless and Secure",
                    "content": """Connect FinCore to your existing ecosystem:
• RESTful APIs for easy system integration
• Pre-built connectors for major financial platforms
• Real-time data synchronization capabilities
• Comprehensive developer documentation and SDKs
• White-glove technical support throughout integration""",
                    "objective": "Address technical implementation concerns",
                    "image_search_terms": ["system integration", "APIs", "technical architecture"]
                },
                {
                    "id": 11,
                    "title": "Next Steps: Begin Your Transformation Today",
                    "content": """Your path to financial AI leadership:
• Week 1: Technical discovery and requirements analysis
• Week 2: Custom solution design and architecture review
• Week 3: Pilot program initiation with core team
• Month 2-3: Full platform deployment and optimization
• Ongoing: Continuous optimization and feature expansion""",
                    "objective": "Provide clear call-to-action and next steps",
                    "image_search_terms": ["next steps", "transformation journey", "partnership"]
                },
                {
                    "id": 12,
                    "title": "Partnership: Your Success is Our Mission",
                    "content": """Why leading financial institutions choose FinCore:
• 15+ years of financial technology expertise
• 99.7% client satisfaction and retention rate
• Dedicated customer success manager for each account
• Continuous platform updates and feature enhancements
• Global support team available 24/7/365""",
                    "objective": "Reinforce partnership value and close with confidence",
                    "image_search_terms": ["partnership", "financial success", "team collaboration"]
                }
            ],
            "strategic_plan": {
                "primary_cta": "Schedule a technical deep-dive and pilot program discussion with our FinCore Solutions team",
                "target_audience": "Financial services executives, CTOs, and decision-makers",
                "goal": "Drive adoption of FinCore AI platform through comprehensive value demonstration"
            }
        },
        "options": {
            "theme": "professional",
            "output_filename": "FinCore_Comprehensive_Sales_Presentation.pptx"
        }
    }
    
    print("🧪 Testing Comprehensive FinCore Presentation Generation")
    print("=" * 60)
    print(f"📊 Input slides count: {len(comprehensive_fincore_data['presentation_data']['slides'])}")
    print("📝 Sending to API...")
    
    try:
        # Send request to API
        response = requests.post(
            "http://127.0.0.1:5001/api/generate-ppt",
            headers={"Content-Type": "application/json"},
            json=comprehensive_fincore_data,
            timeout=120  # 2 minute timeout for comprehensive presentation
        )
        
        print(f"🔄 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Presentation Generated Successfully!")
            print(f"📁 Filename: {result.get('filename')}")
            print(f"📊 File Size: {result.get('file_size')} bytes")
            print(f"⚡ Generation Time: {result.get('generation_time', 'N/A')} seconds")
            
            # Check if all slides were processed
            normalized_slides = result.get('normalized_slides_count', 'Unknown')
            print(f"📋 Slides Processed: {normalized_slides}")
            
            if result.get('session_id'):
                print(f"🔖 Session ID: {result.get('session_id')}")
            
            return True
            
        else:
            result = response.json()
            print(f"❌ Generation Failed!")
            print(f"📝 Error: {result.get('message', 'Unknown error')}")
            print(f"🔍 Details: {result.get('error', 'No details')}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - comprehensive presentations take longer")
        return False
    except Exception as e:
        print(f"💥 Request failed: {e}")
        return False

def check_api_health():
    """Check if API is running and healthy"""
    try:
        response = requests.get("http://127.0.0.1:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and ready")
            return True
        else:
            print(f"⚠️ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API is not accessible: {e}")
        return False

def main():
    print("🔧 FinCore Comprehensive Presentation Debug Test")
    print("=" * 50)
    
    # Check API health first
    print("\n1. Checking API Health...")
    if not check_api_health():
        print("💡 Please ensure the API server is running:")
        print("   cd /Users/amankumar/Desktop/AIPlannerExecutor/ppt")
        print("   python3 ppt_api.py")
        return
    
    # Test comprehensive presentation
    print("\n2. Testing Comprehensive FinCore Presentation...")
    success = test_comprehensive_fincore_presentation()
    
    if success:
        print("\n🎉 SUCCESS! Comprehensive presentation generated!")
        print("📂 Check the generated_presentations/ folder for the output file")
    else:
        print("\n🔍 DEBUGGING NEEDED: Presentation generation incomplete")
        print("💡 This test will help identify why only 4 slides are being generated")

if __name__ == "__main__":
    main()
