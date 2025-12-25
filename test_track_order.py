"""
Test script to verify order tracking functionality
"""
from app.db import get_db_client
from app.responses import handle_track_order

def test_track_order():
    """Test tracking different orders"""
    db = get_db_client()
    
    # Get all orders to see what's in the system
    print("=" * 60)
    print("Fetching all orders from database...")
    print("=" * 60)
    
    try:
        # Query to get all orders
        query = "SELECT c.order_id, c.user_id, c.status, c.total FROM c WHERE c.type = 'order'"
        items = list(db.container.query_items(
            query=query,
            enable_cross_partition_query=True,
            max_item_count=20
        ))
        
        if items:
            print(f"\nFound {len(items)} orders in database:\n")
            for order in items:
                print(f"  Order ID: {order.get('order_id')}")
                print(f"  User ID: {order.get('user_id')}")
                print(f"  Status: {order.get('status')}")
                print(f"  Total: ${order.get('total', 0):.2f}")
                print()
        else:
            print("No orders found in database!")
            
    except Exception as e:
        print(f"Error querying orders: {e}")
    
    # Test tracking specific orders
    print("\n" + "=" * 60)
    print("Testing order tracking...")
    print("=" * 60)
    
    test_orders = [
        "ORD1001",
        "ORD1003",
        "ORD1999"  # Non-existent order
    ]
    
    for order_id in test_orders:
        print(f"\nTracking {order_id}:")
        print("-" * 40)
        response = handle_track_order(order_id)
        print(response)
        print()

if __name__ == '__main__':
    test_track_order()
