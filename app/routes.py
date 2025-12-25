from flask import Blueprint, request, jsonify, render_template
from app.db import get_db_client
from app.responses import get_greeting, get_quick_actions_prompt, get_response, handle_general_message
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Render main page with chatbot widget"""
    return render_template('index.html')


@bp.route('/login')
def login_page():
    """Render login page"""
    return render_template('login.html')


@bp.route('/api/login', methods=['POST'])
def login():
    """
    Handle user login by email
    
    Expected JSON payload:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required', 'success': False}), 400
        
        email = data.get('email').strip().lower()
        
        db = get_db_client()
        user = db.get_user_by_email(email)
        
        if not user:
            return jsonify({
                'error': 'No account found with this email address',
                'success': False
            }), 404
        
        # Return user info (in production, you'd create a session/JWT token here)
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'name': user['name'],
                'email': user['email']
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed', 'success': False}), 500


@bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages
    
    Expected JSON payload:
    {
        "conversation_id": "optional-existing-id",
        "message": "user message",
        "action": "optional-quick-action",
        "user_id": "optional-user-id"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_message = data.get('message', '').strip()
        action = data.get('action')
        conversation_id = data.get('conversation_id')
        user_id = data.get('user_id')
        
        db = get_db_client()
        
        # Create new conversation if no ID provided
        if not conversation_id:
            conversation = db.create_conversation(user_id=user_id)
            conversation_id = conversation['id']
            
            # If no message provided, send greeting and return
            if not user_message and not action:
                greeting = get_greeting()
                db.add_message(conversation_id, 'bot', greeting)
                
                return jsonify({
                    'conversation_id': conversation_id,
                    'response': greeting,
                    'show_quick_actions': True
                })
            # Otherwise, continue to process the message/action below
        
        # Handle quick action
        if action:
            response_data = get_response(action, user_message if user_message else None, user_id, db)
            
            # Store user message if provided
            if user_message:
                db.add_message(conversation_id, 'user', user_message)
            
            # Store bot response
            db.add_message(conversation_id, 'bot', response_data['text'])
            
            return jsonify({
                'conversation_id': conversation_id,
                'response': response_data['text'],
                'requires_input': response_data.get('requires_input', False),
                'action': response_data.get('action'),
                'show_quick_actions': not response_data.get('requires_input', False)
            })
        
        # Handle general message
        if user_message:
            # Store user message
            db.add_message(conversation_id, 'user', user_message)
            
            # Get conversation history for context
            conversation = db.get_conversation(conversation_id)
            conversation_history = conversation.get('messages', []) if conversation else None
            
            # Get user-specific context for AI personalization
            user_context = None
            if user_id and user_id != 'anonymous':
                try:
                    user_context = db.get_user_context_summary(user_id)
                    logger.info(f"Retrieved user context for {user_id}: name={user_context.get('name')}, orders={len(user_context.get('recent_orders', []))}")
                except Exception as e:
                    logger.warning(f"Could not retrieve user context: {e}")
            
            # Generate response with AI using user context
            bot_response = handle_general_message(user_message, conversation_history, user_context)
            
            # Store bot response
            db.add_message(conversation_id, 'bot', bot_response)
            
            return jsonify({
                'conversation_id': conversation_id,
                'response': bot_response,
                'show_quick_actions': True
            })
        
        return jsonify({'error': 'No message or action provided'}), 400
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Retrieve conversation history
    
    Returns all messages for the given conversation ID
    """
    try:
        db = get_db_client()
        conversation = db.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify(conversation)
        
    except Exception as e:
        logger.error(f"Error retrieving conversation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback (thumbs up/down)
    
    Expected JSON payload:
    {
        "conversation_id": "conversation-id",
        "feedback": "up" or "down"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conversation_id = data.get('conversation_id')
        feedback = data.get('feedback')
        
        if not conversation_id or not feedback:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if feedback not in ['up', 'down']:
            return jsonify({'error': 'Invalid feedback value'}), 400
        
        db = get_db_client()
        db.update_feedback(conversation_id, feedback)
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/user/profile', methods=['POST'])
def create_user_profile():
    """
    Create or update user profile with sample data
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "name": "John Doe",
        "email": "john@example.com",
        "preferences": {
            "language": "en",
            "preferred_contact": "email"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_id'):
            return jsonify({'error': 'user_id is required'}), 400
        
        db = get_db_client()
        profile = db.create_or_update_user_profile(data.get('user_id'), data)
        
        return jsonify({
            'success': True,
            'message': 'User profile created/updated',
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/user/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get user's order history"""
    try:
        db = get_db_client()
        orders = db.get_user_orders(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'orders': orders
        })
        
    except Exception as e:
        logger.error(f"Error retrieving user orders: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
