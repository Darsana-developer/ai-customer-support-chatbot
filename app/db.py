from azure.cosmos import CosmosClient, exceptions
from datetime import datetime
import uuid
from config import Config

class CosmosDBClient:
    """Azure Cosmos DB client for managing chat conversations"""
    
    def __init__(self):
        """Initialize Cosmos DB client"""
        self.client = CosmosClient(Config.COSMOS_ENDPOINT, Config.COSMOS_KEY)
        self.database = self.client.get_database_client(Config.COSMOS_DATABASE)
        self.container = self.database.get_container_client(Config.COSMOS_CONTAINER)
    
    def create_conversation(self, user_id=None):
        """
        Create a new conversation session
        
        Args:
            user_id (str, optional): User identifier
            
        Returns:
            dict: Created conversation document
        """
        conversation = {
            'id': str(uuid.uuid4()),
            'user_id': user_id or 'anonymous',
            'messages': [],
            'timestamp': datetime.utcnow().isoformat(),
            'feedback': None,
            'status': 'active'
        }
        
        try:
            created = self.container.create_item(body=conversation)
            return created
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating conversation: {e}")
            raise
    
    def add_message(self, conversation_id, role, content):
        """
        Add a message to an existing conversation
        
        Args:
            conversation_id (str): Conversation ID
            role (str): Message role ('user' or 'bot')
            content (str): Message content
            
        Returns:
            dict: Updated conversation document
        """
        try:
            # Read existing conversation
            conversation = self.container.read_item(
                item=conversation_id,
                partition_key=conversation_id
            )
            
            # Add new message
            message = {
                'id': str(uuid.uuid4()),
                'role': role,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }
            conversation['messages'].append(message)
            
            # Update conversation
            updated = self.container.replace_item(
                item=conversation_id,
                body=conversation
            )
            return updated
            
        except exceptions.CosmosResourceNotFoundError:
            print(f"Conversation {conversation_id} not found")
            raise
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error adding message: {e}")
            raise
    
    def get_conversation(self, conversation_id):
        """
        Retrieve a conversation by ID
        
        Args:
            conversation_id (str): Conversation ID
            
        Returns:
            dict: Conversation document
        """
        try:
            conversation = self.container.read_item(
                item=conversation_id,
                partition_key=conversation_id
            )
            return conversation
        except exceptions.CosmosResourceNotFoundError:
            print(f"Conversation {conversation_id} not found")
            return None
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving conversation: {e}")
            raise
    
    def update_feedback(self, conversation_id, feedback):
        """
        Store user feedback (thumbs up/down) for a conversation
        
        Args:
            conversation_id (str): Conversation ID
            feedback (str): Feedback value ('up' or 'down')
            
        Returns:
            dict: Updated conversation document
        """
        try:
            # Read existing conversation
            conversation = self.container.read_item(
                item=conversation_id,
                partition_key=conversation_id
            )
            
            # Update feedback
            conversation['feedback'] = {
                'value': feedback,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Update conversation
            updated = self.container.replace_item(
                item=conversation_id,
                body=conversation
            )
            return updated
            
        except exceptions.CosmosResourceNotFoundError:
            print(f"Conversation {conversation_id} not found")
            raise
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error updating feedback: {e}")
            raise
    
    def list_conversations(self, user_id=None, limit=10):
        """
        List conversations, optionally filtered by user_id
        
        Args:
            user_id (str, optional): Filter by user ID
            limit (int): Maximum number of conversations to return
            
        Returns:
            list: List of conversation documents
        """
        try:
            if user_id:
                query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.timestamp DESC"
                parameters = [{"name": "@user_id", "value": user_id}]
            else:
                query = "SELECT * FROM c ORDER BY c.timestamp DESC"
                parameters = []
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                max_item_count=limit,
                enable_cross_partition_query=True
            ))
            return items
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error listing conversations: {e}")
            raise
    
    def get_user_profile(self, user_id):
        """
        Retrieve user profile with order history and preferences
        
        Args:
            user_id (str): User identifier
            
        Returns:
            dict: User profile data or None if not found
        """
        try:
            # Query user profile from a separate container or partition
            query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.type = 'user_profile'"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                max_item_count=1,
                enable_cross_partition_query=True
            ))
            
            return items[0] if items else None
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving user profile: {e}")
            return None
    
    def create_or_update_user_profile(self, user_id, profile_data):
        """
        Create or update user profile
        
        Args:
            user_id (str): User identifier
            profile_data (dict): Profile data including name, email, preferences, etc.
            
        Returns:
            dict: Created/updated profile document
        """
        try:
            existing_profile = self.get_user_profile(user_id)
            
            if existing_profile:
                # Update existing profile
                existing_profile.update(profile_data)
                existing_profile['updated_at'] = datetime.utcnow().isoformat()
                updated = self.container.replace_item(
                    item=existing_profile['id'],
                    body=existing_profile
                )
                return updated
            else:
                # Create new profile
                profile = {
                    'id': f"profile_{user_id}_{uuid.uuid4()}",
                    'user_id': user_id,
                    'type': 'user_profile',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    **profile_data
                }
                created = self.container.create_item(body=profile)
                return created
                
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating/updating user profile: {e}")
            raise
    
    def get_user_orders(self, user_id, limit=10):
        """
        Retrieve user's order history
        
        Args:
            user_id (str): User identifier
            limit (int): Maximum number of orders to return
            
        Returns:
            list: List of order documents
        """
        try:
            query = "SELECT * FROM c WHERE c.user_id = @user_id AND c.type = 'order' ORDER BY c.order_date DESC"
            parameters = [{"name": "@user_id", "value": user_id}]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                max_item_count=limit,
                enable_cross_partition_query=True
            ))
            return items
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving user orders: {e}")
            return []
    
    def get_order_by_id(self, order_id, user_id=None):
        """
        Retrieve specific order by ID
        
        Args:
            order_id (str): Order identifier (e.g., 'ORD1003')
            user_id (str, optional): User identifier for authorization
            
        Returns:
            dict: Order document or None if not found
        """
        try:
            # Normalize order_id
            order_id = str(order_id).strip().upper()
            
            query = "SELECT * FROM c WHERE c.order_id = @order_id AND c.type = 'order'"
            parameters = [{"name": "@order_id", "value": order_id}]
            
            if user_id:
                query += " AND c.user_id = @user_id"
                parameters.append({"name": "@user_id", "value": user_id})
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                max_item_count=1,
                enable_cross_partition_query=True
            ))
            
            return items[0] if items else None
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving order: {e}")
            return None
    
    def get_user_context_summary(self, user_id):
        """
        Get a summary of user context for AI personalization
        
        Args:
            user_id (str): User identifier
            
        Returns:
            dict: Summary of user information for AI context
        """
        profile = self.get_user_profile(user_id)
        recent_orders = self.get_user_orders(user_id, limit=5)
        recent_conversations = self.list_conversations(user_id, limit=3)
        
        context = {
            'user_id': user_id,
            'name': profile.get('name', 'Customer') if profile else 'Customer',
            'total_orders': len(recent_orders),
            'recent_orders': [
                {
                    'order_id': order.get('order_id'),
                    'status': order.get('status'),
                    'total': order.get('total'),
                    'date': order.get('order_date')
                } for order in recent_orders
            ] if recent_orders else [],
            'preferences': profile.get('preferences', {}) if profile else {},
            'previous_issues': []
        }
        
        # Extract common issues from previous conversations
        if recent_conversations:
            for conv in recent_conversations:
                messages = conv.get('messages', [])
                user_messages = [m.get('content') for m in messages if m.get('role') == 'user']
                if user_messages:
                    context['previous_issues'].append(user_messages[0][:100])  # First message snippet
        
        return context
    
    def get_user_by_email(self, email):
        """
        Retrieve user profile by email address
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: User profile or None if not found
        """
        try:
            query = "SELECT * FROM c WHERE c.email = @email AND c.type = 'user_profile'"
            parameters = [{"name": "@email", "value": email}]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                return items[0]
            return None
            
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving user by email: {e}")
            return None


# Create a singleton instance
db_client = None

def get_db_client():
    """Get or create Cosmos DB client instance"""
    global db_client
    if db_client is None:
        db_client = CosmosDBClient()
    return db_client
