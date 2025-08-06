#!/usr/bin/env python3
"""
Test script to verify token tracking is working correctly
"""

import requests
import json
import time
from datetime import datetime

def test_token_tracking():
    """Test that all AI operations are properly logging tokens"""
    
    base_url = "http://localhost:5000"
    
    # Test data
    test_email_content = """
    Hi John,

    I hope this email finds you well. I wanted to follow up on our discussion about the quarterly budget review meeting. 

    Could you please send me the updated financial reports by Friday? We need to review them before presenting to the board next week.

    Also, I'd like to schedule a brief call to discuss the marketing campaign performance. Are you available Monday afternoon?

    Looking forward to your response.

    Best regards,
    Sarah
    """
    
    print("🧪 Testing Token Tracking System...")
    print("=" * 50)
    
    # Test 1: Email Generation
    print("\n1. Testing Email Generation Token Tracking...")
    try:
        response = requests.post(f"{base_url}/api/generate-reply", 
            json={
                'original_email': test_email_content,
                'context': 'Professional follow-up',
                'tone': 'professional',
                'model': 'qwen-4-turbo'
            },
            cookies={'session': 'test_session'}  # Placeholder for authentication
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email generation: {data.get('success', False)}")
            if data.get('success'):
                print(f"   Model used: {data.get('model_used', 'unknown')}")
                print(f"   Generation time: {data.get('generation_time_ms', 0)}ms")
        else:
            print(f"❌ Email generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Email generation error: {str(e)}")
    
    # Test 2: Email Summarization
    print("\n2. Testing Email Summarization Token Tracking...")
    try:
        response = requests.post(f"{base_url}/api/test-summarize", 
            json={'email_content': test_email_content}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email summarization: {data.get('success', False)}")
            if data.get('success'):
                print(f"   Model used: {data.get('model_used', 'unknown')}")
                print(f"   Summary length: {data.get('summary_length', 0)} chars")
                print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
        else:
            print(f"❌ Email summarization failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Email summarization error: {str(e)}")
    
    # Test 3: Email Analysis
    print("\n3. Testing Sentiment Analysis Token Tracking...")
    try:
        response = requests.post(f"{base_url}/api/analyze-sentiment", 
            json={'email_content': test_email_content},
            cookies={'session': 'test_session'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sentiment analysis: {data.get('success', False)}")
            if data.get('success'):
                analysis = data.get('analysis', {})
                print(f"   Sentiment: {analysis.get('sentiment', 'unknown')}")
                print(f"   Urgency: {analysis.get('urgency', 'unknown')}")
                print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
        else:
            print(f"❌ Sentiment analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sentiment analysis error: {str(e)}")
    
    # Test 4: Email Suggestions
    print("\n4. Testing Email Suggestions Token Tracking...")
    try:
        response = requests.post(f"{base_url}/api/suggest-improvements", 
            json={'email_content': test_email_content},
            cookies={'session': 'test_session'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Email suggestions: {data.get('success', False)}")
            if data.get('success'):
                suggestions = data.get('suggestions', [])
                print(f"   Suggestions count: {len(suggestions)}")
                if data.get('analysis_metrics'):
                    print(f"   Analysis time: {data.get('analysis_metrics', {}).get('total_analysis_time_ms', 0)}ms")
        else:
            print(f"❌ Email suggestions failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Email suggestions error: {str(e)}")
    
    # Test 5: Template Generation
    print("\n5. Testing Template Generation Token Tracking...")
    try:
        response = requests.post(f"{base_url}/api/generate-template", 
            json={
                'template_type': 'professional',
                'purpose': 'Follow-up meeting request',
                'tone': 'friendly',
                'industry': 'technology'
            },
            cookies={'session': 'test_session'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Template generation: {data.get('success', False)}")
            if data.get('success'):
                print(f"   Template name: {data.get('template_name', 'unknown')}")
                print(f"   Model used: {data.get('model_used', 'unknown')}")
                print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
        else:
            print(f"❌ Template generation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Template generation error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Token Tracking Test Complete!")
    print("\n💡 Check the application logs for token usage entries.")
    print("💡 Navigate to the teams page to verify token counts are updating.")

if __name__ == "__main__":
    test_token_tracking()