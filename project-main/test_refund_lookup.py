"""
Test script to demonstrate refund status lookup using the chatbot
This shows how users can find refund IDs and check refund status
"""

from app.db import get_db_client
from app.responses import show_user_orders_with_refunds, handle_refund_status

def test_refund_workflow():
    """Test the complete refund lookup workflow"""
    
    db = get_db_client()
    
    # Test user IDs from populate_sample_data.py
    test_users = [
        'user_john123',
        'user_sarah456',
        'user_mike789',
        'user_refund_test'
    ]
    
    print("="*70)
    print("REFUND STATUS LOOKUP WORKFLOW TEST")
    print("="*70)
    
    for user_id in test_users:
        print(f"\n\n{'='*70}")
        print(f"User: {user_id}")
        print(f"{'='*70}\n")
        
        # Step 1: Show user's orders with refund information
        print("STEP 1: User asks 'Show My Orders'")
        print("-" * 70)
        orders_info = show_user_orders_with_refunds(user_id, db)
        print(orders_info)
        
        # Step 2: Get all orders for this user and check for refunds
        user_orders = db.get_user_orders(user_id, limit=20)
        refunded_orders = [o for o in user_orders if 'refund' in o]
        
        if refunded_orders:
            print("\n\nSTEP 2: User selects 'Refund Status' and provides Order ID")
            print("-" * 70)
            
            for order in refunded_orders:
                order_id = order.get('order_id')
                print(f"\nChecking refund for Order ID: {order_id}")
                print("-" * 50)
                
                refund_info = handle_refund_status(order_id, user_id, db)
                print(refund_info)
        else:
            print("\n\n[This user has no refunded orders]")
    
    print(f"\n\n{'='*70}")
    print("TEST COMPLETE")
    print("="*70)
    print("\n✓ Users can now:")
    print("  1. Click 'Show My Orders' to see all their orders")
    print("  2. Note the Order IDs from the list")
    print("  3. Click 'Refund Status' and enter the Order ID")
    print("  4. Get detailed refund information (status, amount, dates, etc.)")
    print("\n✓ No separate refund ID needed - just use the Order ID!")


if __name__ == '__main__':
    try:
        test_refund_workflow()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
