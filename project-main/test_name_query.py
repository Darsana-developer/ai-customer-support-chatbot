"""
Test script to verify chatbot responds to name queries
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_name_query():
    """Test if chatbot responds with user's name"""
    
    print("=" * 60)
    print("Testing Chatbot Name Query")
    print("=" * 60)
    
    # Step 1: Login as John Smith
    print("\n1. Logging in as John Smith...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={"email": "john.smith@example.com"}
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"   ✓ Login successful!")
        print(f"   User ID: {login_data['user']['user_id']}")
        print(f"   Name: {login_data['user']['name']}")
        user_id = login_data['user']['user_id']
    else:
        print(f"   ✗ Login failed: {login_response.text}")
        return
    
    # Step 2: Initialize conversation
    print("\n2. Initializing conversation...")
    init_response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"user_id": user_id}
    )
    
    if init_response.status_code == 200:
        init_data = init_response.json()
        print(f"   ✓ Conversation initialized!")
        print(f"   Conversation ID: {init_data['conversation_id']}")
        print(f"   Bot: {init_data['response']}")
        conversation_id = init_data['conversation_id']
    else:
        print(f"   ✗ Initialization failed: {init_response.text}")
        return
    
    # Step 3: Ask "What's my name?"
    print("\n3. Asking 'What's my name?'...")
    name_query_response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "conversation_id": conversation_id,
            "message": "What's my name?",
            "user_id": user_id
        }
    )
    
    if name_query_response.status_code == 200:
        name_data = name_query_response.json()
        print(f"   ✓ Response received!")
        print(f"   Bot: {name_data['response']}")
        
        # Check if response contains the user's name
        if "John Smith" in name_data['response']:
            print("\n   ✅ SUCCESS: Bot correctly identified user's name!")
        else:
            print("\n   ⚠️  WARNING: Bot response doesn't contain 'John Smith'")
    else:
        print(f"   ✗ Query failed: {name_query_response.text}")
        return
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_name_query()
