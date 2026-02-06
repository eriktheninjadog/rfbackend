#!/usr/bin/env python3
"""
Test script for the new /llm_query endpoint
"""
import requests
import json

# Base URL for your Flask app
BASE_URL = "http://localhost:5000"

def test_basic_query():
    """Test basic LLM query"""
    payload = {
        "model": "claude-3.5-sonnet",
        "prompt": "Hello, can you introduce yourself briefly?"
    }
    
    response = requests.post(f"{BASE_URL}/llm_query", json=payload)
    print("=== Basic Query Test ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_system_message():
    """Test with system message and custom parameters"""
    payload = {
        "model": "claude-3.5-sonnet",
        "prompt": "Translate 'Good morning, how are you?' to Cantonese",
        "system_message": "You are a Cantonese language expert. Always provide traditional Chinese characters.",
        "temperature": 0.3,
        "max_tokens": 200,
        "metadata": {
            "use_case": "translation",
            "language": "cantonese",
            "user_level": "beginner"
        }
    }
    
    response = requests.post(f"{BASE_URL}/llm_query", json=payload)
    print("=== System Message Test ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_json_format():
    """Test JSON response format"""
    payload = {
        "model": "claude-3.5-sonnet",
        "prompt": "Create a simple study schedule for learning Cantonese. Include 3 daily activities.",
        "response_format": "json",
        "temperature": 0.5,
        "system_message": "Return a valid JSON object with a 'schedule' array containing daily activities."
    }
    
    response = requests.post(f"{BASE_URL}/llm_query", json=payload)
    print("=== JSON Format Test ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_session_management():
    """Test session management"""
    session_id = "test-session-001"
    
    # First message in session
    payload1 = {
        "model": "claude-3.5-sonnet",
        "prompt": "Let's have a conversation about Cantonese tones. Start by explaining the 6 main tones.",
        "session_id": session_id,
        "clear_history": True
    }
    
    response1 = requests.post(f"{BASE_URL}/llm_query", json=payload1)
    print("=== Session Test - Message 1 ===")
    print(f"Status: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")
    print()
    
    # Continue conversation (note: actual session storage not implemented yet)
    payload2 = {
        "model": "claude-3.5-sonnet", 
        "prompt": "Which tone is the most difficult for English speakers to learn?",
        "session_id": session_id,
        "clear_history": False
    }
    
    response2 = requests.post(f"{BASE_URL}/llm_query", json=payload2)
    print("=== Session Test - Message 2 ===")
    print(f"Status: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    print()


def test_error_handling():
    """Test error handling"""
    # Test missing required parameters
    payload = {
        "model": "claude-3.5-sonnet"
        # Missing prompt
    }
    
    response = requests.post(f"{BASE_URL}/llm_query", json=payload)
    print("=== Error Handling Test ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("Testing /llm_query endpoint...")
    print("Make sure your Flask server is running on localhost:5000")
    print()
    
    try:
        # Run all tests
        test_basic_query()
        test_system_message()
        test_json_format()
        test_session_management()
        test_error_handling()
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Flask server.")
        print("Make sure the server is running on localhost:5000")
    except Exception as e:
        print(f"ERROR: {e}")