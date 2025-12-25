"""
AI-powered response logic using Azure OpenAI API with fallback to rule-based responses
"""
import logging
from openai import AzureOpenAI
from config import Config

logger = logging.getLogger(__name__)

# Initialize Azure OpenAI client
try:
    client = AzureOpenAI(
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version=Config.AZURE_OPENAI_API_VERSION,
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
    )
except Exception as e:
    logger.error(f"Failed to initialize Azure OpenAI client: {e}")
    client = None

QUICK_ACTIONS = {
    'track_order': {
        'name': 'Track Order',
        'requires_input': True,
        'input_prompt': 'Please provide your Order ID',
        'response_template': 'Order #{order_id} Status: {status}\n\n{details}'
    },
    'refund_status': {
        'name': 'Refund Status',
        'requires_input': True,
        'input_prompt': 'Please provide your Order ID',
        'response_template': 'Refund Status for Order #{order_id}:\n{status}\n\n{details}'
    },
    'show_orders': {
        'name': 'Show My Orders',
        'requires_input': False,
        'response': 'Fetching your orders...'
    },
    'talk_to_agent': {
        'name': 'Talk to Agent',
        'requires_input': False,
        'response': 'I\'ll connect you with a human agent. Please choose your preferred contact method:\n\n📞 Phone: 1-800-SUPPORT (Available 24/7)\n📧 Email: support@company.com\n💬 Live Chat: Available Mon-Fri 9AM-5PM EST\n\nOur average response time is under 2 minutes!'
    },
    'product_info': {
        'name': 'Product Info',
        'requires_input': False,
        'response': 'I can help you with product information! Here are our most popular topics:\n\n📦 Shipping & Delivery\n🔄 Returns & Exchanges\n💳 Payment Options\n🛡️ Warranty Information\n📱 Product Specifications\n\nWhat would you like to know more about?'
    }
}


def get_greeting():
    """Return greeting message"""
    return "Hello! 👋 I'm your customer support assistant. How can I help you today?"


def get_quick_actions_prompt():
    """Return quick actions buttons prompt"""
    return "Choose from our quick actions below, or type your question:"


def handle_track_order(order_id, user_id=None, db_client=None):
    """Handle track order request with real user data"""
    if not db_client:
        from app.db import get_db_client
        db_client = get_db_client()
    
    # Normalize order_id - remove spaces and ensure uppercase
    order_id = order_id.strip().upper() if isinstance(order_id, str) else order_id
    
    # Try to fetch real order data - first with user_id, then without if needed
    order = db_client.get_order_by_id(order_id, user_id) if user_id and user_id != 'anonymous' else None
    
    # If not found with user_id, try without (in case user is not logged in or order lookup is global)
    if not order:
        order = db_client.get_order_by_id(order_id, None)
    
    if order:
        # Use real order data
        status = order.get('status', 'Unknown')
        tracking_number = order.get('tracking_number', 'N/A')
        estimated_delivery = order.get('estimated_delivery', 'TBD')
        order_date = order.get('order_date', 'N/A')
        items = order.get('items', [])
        total = order.get('total', 0)
        
        details = f"Order Date: {order_date[:10] if isinstance(order_date, str) else order_date}\n"
        details += f"Order Total: ${total:.2f}\n"
        
        if items:
            details += f"Items: {len(items)} item(s)\n"
            for idx, item in enumerate(items[:3], 1):
                details += f"  {idx}. {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f}\n"
            if len(items) > 3:
                details += f"  ... and {len(items) - 3} more item(s)\n"
        
        if tracking_number != 'N/A':
            details += f"\nTracking Number: {tracking_number}\n"
        if estimated_delivery != 'TBD' and estimated_delivery:
            details += f"Expected Delivery: {estimated_delivery[:10] if isinstance(estimated_delivery, str) else estimated_delivery}\n"
        
        # Add status-specific information
        if status.lower() == 'processing':
            details += "\n📝 Your order is being prepared for shipment."
        elif status.lower() == 'shipped':
            details += "\n📦 Your order has been shipped and is on its way!"
        elif status.lower() in ['in transit', 'in_transit']:
            details += "\n🚚 Your package is currently in transit."
        elif status.lower() == 'delivered':
            details += "\n✅ Your order has been successfully delivered!"
        
        return QUICK_ACTIONS['track_order']['response_template'].format(
            order_id=order_id,
            status=status,
            details=details
        )
    else:
        # Fallback for orders not in system or demo purposes
        logger.warning(f"Order {order_id} not found in database for user {user_id}")
        return f"I couldn't find order #{order_id} in our system. Please verify your order ID or contact support if you need assistance. Your order ID should be in your confirmation email.\n\nIf you just placed an order, it may take a few minutes to appear in the system."


def handle_show_orders(user_id=None, db_client=None):
    """Handle 'show my orders' request with real user data"""
    if not user_id or user_id == 'anonymous':
        return "I need you to be logged in to show your orders. Please log in first!"
    
    if not db_client:
        from app.db import get_db_client
        db_client = get_db_client()
    
    try:
        # Fetch all user orders
        orders = db_client.get_user_orders(user_id)
        
        if not orders:
            return "You don't have any orders yet. Start shopping and your orders will appear here!"
        
        # Format orders for display
        response = f"📦 Here are your {len(orders)} order(s):\n\n"
        
        for idx, order in enumerate(orders, 1):
            order_id = order.get('order_id', 'N/A')
            status = order.get('status', 'Unknown')
            total = order.get('total', 0)
            order_date = order.get('order_date', 'N/A')
            items = order.get('items', [])
            
            # Format individual order
            response += f"{idx}. **Order #{order_id}**\n"
            response += f"   Status: {status}\n"
            response += f"   Total: ${total:.2f}\n"
            response += f"   Date: {order_date[:10] if isinstance(order_date, str) else order_date}\n"
            
            if items:
                response += f"   Items: {len(items)} item(s)\n"
                for item in items[:2]:  # Show first 2 items
                    response += f"     • {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f}\n"
                if len(items) > 2:
                    response += f"     • ... and {len(items) - 2} more item(s)\n"
            
            # Add refund status if applicable
            if order.get('refund'):
                refund = order['refund']
                response += f"   Refund: {refund.get('status', 'N/A')}\n"
            
            response += "\n"
        
        response += "Click 'Track Order' to get detailed tracking information for any order."
        return response
        
    except Exception as e:
        logger.error(f"Error fetching user orders: {e}")
        return "I encountered an error retrieving your orders. Please try again later or contact support."


def handle_refund_status(order_id, user_id=None, db_client=None):
    """Handle refund status request with real user data"""
    if not db_client:
        from app.db import get_db_client
        db_client = get_db_client()
    
    # Try to fetch real order and refund data
    order = db_client.get_order_by_id(order_id, user_id)
    
    if order:
        refund_info = order.get('refund', {})
        
        if refund_info:
            # Real refund data exists
            status = refund_info.get('status', 'No refund request')
            amount = refund_info.get('amount', 0)
            request_date = refund_info.get('request_date', 'N/A')
            expected_completion = refund_info.get('expected_completion', 'TBD')
            reason = refund_info.get('reason', 'N/A')
            payment_method = refund_info.get('payment_method', 'N/A')
            
            details = f"Request Date: {request_date}\n"
            if amount > 0:
                details += f"Refund Amount: ${amount:.2f}\n"
            details += f"Reason: {reason}\n"
            details += f"Payment Method: {payment_method}\n"
            if expected_completion and expected_completion != 'TBD':
                details += f"Expected Completion: {expected_completion}\n"
            
            # Add status-specific information
            if status.lower() == 'pending':
                details += "\n⏳ Your refund request is being reviewed by our team. We'll update you within 24-48 hours."
            elif status.lower() == 'approved':
                details += f"\n✅ Your refund has been approved! Amount: ${amount:.2f} will be credited to your {payment_method} within 5-7 business days."
            elif status.lower() == 'processing':
                details += "\n⚙️ Your refund is being processed. Expected completion: 3-5 business days."
            elif status.lower() == 'completed':
                details += "\n✓ Your refund has been completed and should appear in your account within 1-2 business days."
            
            return QUICK_ACTIONS['refund_status']['response_template'].format(
                order_id=order_id,
                status=status,
                details=details
            )
        else:
            return f"No refund request found for order #{order_id}. If you'd like to request a refund, please contact our support team or visit your account dashboard."
    else:
        return f"I couldn't find order #{order_id} in our system. Please verify your order ID or contact support if you need assistance."


def show_user_orders_with_refunds(user_id, db_client=None):
    """Show user's orders with order IDs and refund information"""
    if not db_client:
        from app.db import get_db_client
        db_client = get_db_client()
    
    try:
        orders = db_client.get_user_orders(user_id, limit=20)
        
        if not orders:
            return "You don't have any orders yet."
        
        response = "📦 **Your Orders:**\n\n"
        
        has_refunds = False
        
        for order in orders:
            order_id = order.get('order_id', 'Unknown')
            status = order.get('status', 'Unknown')
            order_date = order.get('order_date', 'N/A')
            total = order.get('total', 0)
            refund = order.get('refund', {})
            
            # Format date nicely
            if isinstance(order_date, str) and 'T' in order_date:
                order_date = order_date.split('T')[0]
            
            response += f"**Order #{order_id}** (Date: {order_date})\n"
            response += f"  Status: {status} | Total: ${total:.2f}\n"
            
            # Show refund information if available
            if refund:
                has_refunds = True
                refund_status = refund.get('status', 'Unknown')
                refund_amount = refund.get('amount', 0)
                response += f"  💰 Refund: {refund_status} (${refund_amount:.2f})\n"
            
            response += "\n"
        
        response += "---\n\n"
        response += "**To check refund status for any order, use the 'Refund Status' action and provide the Order ID above.**\n\n"
        
        if has_refunds:
            response += "You have orders with refunds. Click 'Refund Status' and enter the Order ID to get details."
        
        return response
        
    except Exception as e:
        logger.error(f"Error showing user orders: {e}")
        return "I encountered an error retrieving your orders. Please try again later or contact support."


def get_response(action, user_input=None, user_id=None, db_client=None):
    """
    Get response for a given action
    
    Args:
        action (str): Action identifier
        user_input (str, optional): User input (e.g., order ID)
        user_id (str, optional): User identifier for personalized data
        db_client (object, optional): Database client for data access
        
    Returns:
        dict: Response containing text and metadata
    """
    if action not in QUICK_ACTIONS:
        return {
            'text': 'I\'m sorry, I didn\'t understand that. Please choose from the quick actions or type your question.',
            'requires_input': False
        }
    
    action_config = QUICK_ACTIONS[action]
    
    # If action requires input and none provided, ask for it
    if action_config['requires_input'] and not user_input:
        return {
            'text': action_config['input_prompt'],
            'requires_input': True,
            'action': action
        }
    
    # Handle specific actions with user context
    if action == 'track_order':
        response_text = handle_track_order(user_input, user_id, db_client)
    elif action == 'refund_status':
        response_text = handle_refund_status(user_input, user_id, db_client)
    elif action == 'show_orders':
        response_text = show_user_orders_with_refunds(user_id, db_client) if user_id and user_id != 'anonymous' else "Please log in to view your orders."
    else:
        response_text = action_config['response']
    
    return {
        'text': response_text,
        'requires_input': False
    }


def get_ai_response(message, conversation_history=None, user_context=None):
    """
    Get AI-powered response using Azure OpenAI API with user context
    
    Args:
        message (str): User message
        conversation_history (list, optional): Previous conversation messages
        user_context (dict, optional): User-specific context for personalization
        
    Returns:
        str: AI-generated response
    """
    if not client:
        logger.error("Azure OpenAI client not initialized")
        return handle_general_message_fallback(message, user_context)
    
    # Check for "show my orders" pattern early
    message_lower = message.lower()
    if any(phrase in message_lower for phrase in ['show my orders', 'show orders', 'list orders', 'all my orders', 'my orders']):
        if user_context:
            user_id = user_context.get('user_id')
            from app.db import get_db_client
            db = get_db_client()
            return handle_show_orders(user_id, db)
        else:
            return "I need you to be logged in to show your orders. Please log in first!"
    
    try:
        # Build personalized system prompt
        system_prompt = """You are a helpful customer support assistant for an e-commerce company. 
        Be friendly, professional, and concise. Help customers with:
        - Order tracking and shipping inquiries
        - Refund and return requests
        - Product information
        - General support questions
        
        When customers need to track orders or check refunds, ask for their Order ID.
        If they need human assistance, guide them to use the 'Talk to Agent' button.
        Keep responses brief and actionable."""
        
        # Add user-specific context if available
        if user_context:
            user_name = user_context.get('name', 'Customer')
            recent_orders = user_context.get('recent_orders', [])
            preferences = user_context.get('preferences', {})
            
            context_info = f"\n\nUser Context:\n- Customer Name: {user_name}"
            
            if recent_orders:
                context_info += f"\n- Recent Orders: {len(recent_orders)} order(s)"
                for order in recent_orders[:3]:  # Show top 3 recent orders
                    context_info += f"\n  * Order #{order.get('order_id')}: {order.get('status')} - ${order.get('total', 0):.2f}"
            
            if preferences:
                if preferences.get('preferred_contact'):
                    context_info += f"\n- Preferred Contact: {preferences['preferred_contact']}"
                if preferences.get('language'):
                    context_info += f"\n- Language: {preferences['language']}"
            
            system_prompt += context_info
            system_prompt += f"\n\nUse this context to provide personalized assistance. When the user asks about their name or personal information, use the name '{user_name}'. Reference their orders when relevant."
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = "assistant" if msg.get('role') == 'bot' else "user"
                messages.append({"role": role, "content": msg.get('content', '')})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call Azure OpenAI API
        response = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            max_completion_tokens=Config.AZURE_OPENAI_MAX_TOKENS,
            temperature=Config.AZURE_OPENAI_TEMPERATURE
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error calling Azure OpenAI API: {e}")
        return handle_general_message_fallback(message, user_context)


def handle_general_message_fallback(message, user_context=None):
    """
    Fallback to keyword matching when Azure OpenAI API is unavailable
    
    Args:
        message (str): User message
        user_context (dict, optional): User-specific context for personalization
        
    Returns:
        str: Bot response
    """
    message_lower = message.lower()
    
    # Keyword matching for common queries
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return get_greeting()
    
    elif any(phrase in message_lower for phrase in ["what's my name", 'my name', 'who am i', 'what is my name']):
        if user_context and user_context.get('name'):
            return f"Your name is {user_context.get('name')}."
        else:
            return "I don't have your name on file. Please make sure you're logged in."
    
    elif any(phrase in message_lower for phrase in ['show my orders', 'show orders', 'list orders', 'all my orders', 'my orders']):
        if user_context:
            user_id = user_context.get('user_id')
            from app.db import get_db_client
            db = get_db_client()
            return handle_show_orders(user_id, db)
        else:
            return "I need you to be logged in to show your orders. Please log in first!"
    
    elif any(word in message_lower for word in ['track', 'order', 'shipping', 'delivery']):
        return "I can help you track your order! Please click the 'Track Order' button below and provide your Order ID."
    
    elif any(word in message_lower for word in ['refund', 'return', 'exchange']):
        return "I can help you check your refund status! Please click the 'Refund Status' button below and provide your Order ID."
    
    elif any(word in message_lower for word in ['agent', 'human', 'representative', 'talk', 'speak']):
        return "I can connect you with a human agent. Please click the 'Talk to Agent' button below for contact options."
    
    elif any(word in message_lower for word in ['product', 'item', 'specification', 'warranty']):
        return "I can provide product information! Please click the 'Product Info' button below to see what topics I can help with."
    
    elif any(word in message_lower for word in ['help', 'support', 'assist']):
        return "I'm here to help! You can use the quick action buttons below, or ask me about:\n\n• Order tracking\n• Refunds and returns\n• Product information\n• Speaking with an agent\n\nWhat would you like to know?"
    
    elif any(word in message_lower for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
        return "Thank you for contacting us! Have a great day! 👋"
    
    else:
        return "I'm here to help! I can assist you with:\n\n• Tracking your orders\n• Checking refund status\n• Providing product information\n• Connecting you with an agent\n\nPlease use the quick action buttons below or let me know how I can help!"


def handle_general_message(message, conversation_history=None, user_context=None):
    """
    Handle general user messages using AI with user context or fallback to keyword matching
    
    Args:
        message (str): User message
        conversation_history (list, optional): Previous conversation messages
        user_context (dict, optional): User-specific context for personalization
        
    Returns:
        str: Bot response
    """
    return get_ai_response(message, conversation_history, user_context)
