"""
Helper script to populate sample user data for testing personalized chatbot
Run this script to add sample users and orders to your Cosmos DB
"""
from app.db import get_db_client
from datetime import datetime, timedelta
import random

def populate_sample_users():
    """Create sample user profiles and orders"""
    db = get_db_client()
    
    # Sample users
    users = [
        {
            'user_id': 'user_john123',
            'name': 'John Smith',
            'email': 'john.smith@example.com',
            'preferences': {
                'language': 'en',
                'preferred_contact': 'email',
                'newsletter': True
            }
        },
        {
            'user_id': 'user_sarah456',
            'name': 'Sarah Johnson',
            'email': 'sarah.j@example.com',
            'preferences': {
                'language': 'en',
                'preferred_contact': 'phone',
                'newsletter': False
            }
        },
        {
            'user_id': 'user_mike789',
            'name': 'Mike Davis',
            'email': 'mike.davis@example.com',
            'preferences': {
                'language': 'en',
                'preferred_contact': 'email',
                'newsletter': True
            }
        },
        {
            'user_id': 'user_refund_test',
            'name': 'Refund Tester',
            'email': 'refund.tester@example.com',
            'preferences': {
                'language': 'en',
                'preferred_contact': 'email',
                'newsletter': False
            }
        }
    ]
    
    # Create user profiles
    print("Creating user profiles...")
    for user in users:
        try:
            profile = db.create_or_update_user_profile(user['user_id'], user)
            print(f"✓ Created profile for {user['name']} ({user['user_id']})")
        except Exception as e:
            print(f"✗ Error creating profile for {user['name']}: {e}")
    
    # Sample orders for each user
    order_statuses = ['Processing', 'Shipped', 'In Transit', 'Delivered']
    product_samples = [
        {'name': 'Wireless Headphones', 'price': 89.99},
        {'name': 'Smart Watch', 'price': 249.99},
        {'name': 'Laptop Stand', 'price': 39.99},
        {'name': 'USB-C Hub', 'price': 59.99},
        {'name': 'Mechanical Keyboard', 'price': 129.99},
        {'name': 'Webcam HD', 'price': 79.99}
    ]
    
    print("\nCreating sample orders...")
    order_counter = 1000
    
    # Define refund statuses to cycle through
    refund_statuses = ['Pending', 'Approved', 'Processing', 'Completed']
    refund_reasons = [
        'Product not as described',
        'Arrived damaged',
        'Ordered by mistake',
        'Better price elsewhere',
        'Changed mind',
        'Item defective',
        'Not satisfied with quality'
    ]
    payment_methods = ['Credit Card', 'PayPal', 'Debit Card', 'Gift Card']
    
    for user_idx, user in enumerate(users):
        # Create 2-4 regular orders per user
        num_orders = random.randint(2, 4)
        
        for i in range(num_orders):
            order_counter += 1
            order_date = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            
            # Select 1-3 products for this order
            num_items = random.randint(1, 3)
            items = random.sample(product_samples, num_items)
            total = sum(item['price'] for item in items)
            
            status = random.choice(order_statuses)
            
            order = {
                'id': f"order_{order_counter}",
                'user_id': user['user_id'],
                'type': 'order',
                'order_id': f"ORD{order_counter}",
                'status': status,
                'total': round(total, 2),
                'items': items,
                'order_date': order_date.isoformat(),
                'tracking_number': f"1Z999AA{random.randint(10000000, 99999999)}" if status in ['Shipped', 'In Transit', 'Delivered'] else None,
                'estimated_delivery': (order_date + timedelta(days=5)).isoformat() if status in ['Processing', 'Shipped', 'In Transit'] else None
            }
            
            try:
                db.container.create_item(body=order)
                print(f"✓ Created order {order['order_id']} for {user['name']} - Status: {status}")
            except Exception as e:
                print(f"✗ Error creating order: {e}")

        # Add multiple refunded orders with different statuses per user
        print(f"\n  Creating refund samples for {user['name']}:")
        
        for refund_idx, refund_status in enumerate(refund_statuses):
            order_counter += 1
            order_date = datetime.utcnow() - timedelta(days=60 - (refund_idx * 10))
            refund_amount = round(random.uniform(50, 300), 2)
            
            # Determine expected completion based on status
            if refund_status == 'Pending':
                days_until_completion = 2
                request_date = order_date + timedelta(days=5)
            elif refund_status == 'Approved':
                days_until_completion = 7
                request_date = order_date + timedelta(days=4)
            elif refund_status == 'Processing':
                days_until_completion = 5
                request_date = order_date + timedelta(days=3)
            else:  # Completed
                days_until_completion = 0
                request_date = order_date + timedelta(days=2)
            
            refunded_order = {
                'id': f"order_{order_counter}",
                'user_id': user['user_id'],
                'type': 'order',
                'order_id': f"ORD{order_counter}",
                'status': 'Delivered',
                'total': refund_amount,
                'items': [random.choice(product_samples)],
                'order_date': order_date.isoformat(),
                'tracking_number': f"1Z{random.randint(100000000, 999999999)}",
                'estimated_delivery': None,
                'refund': {
                    'status': refund_status,
                    'amount': refund_amount,
                    'request_date': request_date.isoformat(),
                    'expected_completion': (request_date + timedelta(days=days_until_completion)).isoformat() if refund_status != 'Completed' else None,
                    'reason': random.choice(refund_reasons),
                    'payment_method': random.choice(payment_methods)
                }
            }
            try:
                db.container.create_item(body=refunded_order)
                print(f"    ✓ Order {refunded_order['order_id']}: Refund Status = {refund_status}")
            except Exception as e:
                print(f"    ✗ Error creating refund order: {e}")
        
        print()
    
    print("\n" + "="*60)
    print("Sample data population complete!")
    print("="*60)
    print("\nTest Users:")
    for user in users:
        print(f"\n{user['name']}:")
        print(f"  User ID: {user['user_id']}")
        print(f"  Email: {user['email']}")
    
    print("\n" + "="*60)
    print("Usage Instructions:")
    print("="*60)
    print("\n1. In the chatbot, pass user_id when initializing:")
    print('   POST /api/chat with {"user_id": "user_john123"}')
    print("\n2. The chatbot will now have access to:")
    print("   - User's name and preferences")
    print("   - Order history")
    print("   - Real order tracking data")
    print("   - Refund status (where applicable)")
    print("\n3. Try asking:")
    print("   - 'Show me my orders'")
    print("   - 'Track order ORD1001'")
    print("   - 'What's the status of my refund for order ORD1003?'")
    print("\n" + "="*60)


if __name__ == '__main__':
    print("="*60)
    print("Populating Sample User Data for Personalized Chatbot")
    print("="*60)
    print()
    
    try:
        populate_sample_users()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("1. Your .env file has correct Cosmos DB credentials")
        print("2. The database and container exist")
        print("3. You have proper permissions")
