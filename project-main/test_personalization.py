"""
Simple test script to verify personalized chatbot functionality
Run this after populating sample data
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_chatbot():
    print("="*60)
    print("Testing Personalized Chatbot")
    print("="*60)
    print()
    
    # Test 1: Initialize conversation with user ID
    print("Test 1: Initialize conversation with user_id")
    print("-" * 60)
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"user_id": "user_john123"}
    )
    data = response.json()
    conversation_id = data.get('conversation_id')
    print(f"Status: {response.status_code}")
    print(f"Conversation ID: {conversation_id}")
    print(f"Response: {data.get('response')[:100]}...")
    print()
    
    # Test 2: Ask about orders (should reference user's actual orders)
    print("Test 2: Ask about orders (AI should use user context)")
    print("-" * 60)
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "conversation_id": conversation_id,
            "user_id": "user_john123",
            "message": "What orders do I have?"
        }
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {data.get('response')}")
    print()
    
    # Test 3: Get user orders via API
    print("Test 3: Get user orders directly")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/api/user/user_john123/orders")
    data = response.json()
    print(f"Status: {response.status_code}")
    if data.get('orders'):
        print(f"Found {len(data['orders'])} orders:")
        for order in data['orders'][:3]:  # Show first 3
            print(f"  - Order {order.get('order_id')}: {order.get('status')} (${order.get('total')})")
    print()
    
    # Test 4: Track specific order (real data)
    print("Test 4: Track specific order")
    print("-" * 60)
    if data.get('orders'):
        test_order_id = data['orders'][0].get('order_id')
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "conversation_id": conversation_id,
                "user_id": "user_john123",
                "action": "track_order",
                "message": test_order_id
            }
        )
        result = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {result.get('response')}")
    print()
    
    # Test 5: Compare anonymous vs authenticated user
    print("Test 5: Compare anonymous vs authenticated experience")
    print("-" * 60)
    
    # Anonymous conversation
    print("Anonymous user:")
    response = requests.post(f"{BASE_URL}/api/chat", json={})
    anon_data = response.json()
    print(f"  Response: {anon_data.get('response')[:80]}...")
    
    # Authenticated conversation
    print("\\nAuthenticated user (John):")
    response = requests.post(f"{BASE_URL}/api/chat", json={"user_id": "user_john123"})
    auth_data = response.json()
    print(f"  Response: {auth_data.get('response')[:80]}...")
    print()
    
    print("="*60)
    print("Tests Complete!")
    print("="*60)
    print()
    print("✅ If you see order information and personalized responses,")
    print("   your chatbot is successfully using user-specific data!")
    print()
    print("Next: Open http://localhost:5000/?user_id=user_john123")
    print("      and test the chatbot widget in the browser.")
    print()


if __name__ == '__main__':
    try:
        print()
        print("Make sure your Flask app is running on port 5000!")
        print("(Run: python run.py)")
        print()
        input("Press Enter to start tests...")
        print()
        
        test_chatbot()
        
    except requests.exceptions.ConnectionError:
        print()
        print("❌ Error: Could not connect to Flask app")
        print("   Make sure the app is running: python run.py")
        print()
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
