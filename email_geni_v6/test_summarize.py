#!/usr/bin/env python3
"""
Test script to verify email summarization functionality
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_service import ai_service

def test_summarization():
    """Test email summarization with sample content"""
    test_email = """
    Subject: Project Update - Quarterly Review Meeting

    Hi Team,

    I hope this email finds you well. I wanted to provide you with an update on our current project status and schedule our quarterly review meeting.

    Current Project Status:
    - Phase 1 development is 85% complete
    - We've successfully implemented the user authentication system
    - Database migration is scheduled for next Tuesday
    - The design team has finalized the UI mockups

    Upcoming Deadlines:
    - Code review deadline: Friday, August 9th
    - Beta testing begins: Monday, August 12th
    - Final delivery: August 30th

    Meeting Details:
    I'd like to schedule our quarterly review meeting for next week. Please let me know your availability for the following time slots:
    - Wednesday 2-4 PM
    - Thursday 10 AM - 12 PM
    - Friday 1-3 PM

    Please reply by end of business tomorrow so I can send out calendar invites.

    Best regards,
    Project Manager
    """
    
    print("🔍 Testing Email Summarization with LangChain...")
    print("=" * 60)
    print("Original Email:")
    print(test_email)
    print("=" * 60)
    
    try:
        # Test summarization
        result = ai_service.summarize_email_with_langchain(
            email_content=test_email,
            context="test_summary",
            user_id="test_user",
            model_preference="auto"
        )
        
        print("✅ Summarization Result:")
        if result.get('success'):
            print(f"📝 Summary: {result['content']}")
            print(f"🤖 Model Used: {result.get('model_used', 'Unknown')}")
            print(f"⏱️  Processing Time: {result.get('processing_time_ms', 0)}ms")
            print(f"📊 Original Length: {result.get('original_length', 0)} chars")
            print(f"📊 Summary Length: {result.get('summary_length', 0)} chars")
            print("\n✅ Email summarization is working correctly!")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summarization()