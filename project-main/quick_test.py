"""
Quick test to verify chatbot is working with user data
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("Testing Personalized Chatbot API")
print("=" * 60)

# Step 1: Initialize conversation
print("\n1. Initializing conversation with user_id...")
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"user_id": "user_john123"}
)

if response.status_code == 200:
    data = response.json()
    conversation_id = data.get('conversation_id')
    print(f"✓ Success! Conversation ID: {conversation_id}")
    print(f"  Bot says: {data.get('response')}")
else:
    print(f"✗ Error {response.status_code}: {response.text}")
    exit(1)

# Step 2: Ask about orders
print("\n2. Asking 'What orders do I have?'...")
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "conversation_id": conversation_id,
        "user_id": "user_john123",
        "message": "What orders do I have?"
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Success!")
    print(f"  Bot says:\n  {data.get('response')}")
else:
    print(f"✗ Error {response.status_code}: {response.text}")

# Step 3: Get orders directly via API
print("\n3. Getting orders directly from API...")
response = requests.get(f"{BASE_URL}/api/user/user_john123/orders")

if response.status_code == 200:
    data = response.json()
    orders = data.get('orders', [])
    print(f"✓ Found {len(orders)} orders:")
    for order in orders[:3]:
        print(f"  - {order.get('order_id')}: {order.get('status')} (${order.get('total')})")
else:
    print(f"✗ Error {response.status_code}: {response.text}")

print("\n" + "=" * 60)
print("Test complete!")
