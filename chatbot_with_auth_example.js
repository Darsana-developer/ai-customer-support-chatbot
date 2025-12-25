// Enhanced Chatbot JavaScript with User Authentication Support
// Copy this to replace your existing chatbot.js to enable user-specific personalization

class Chatbot {
    constructor() {
        this.conversationId = null;
        this.currentAction = null;
        this.awaitingInput = false;
        this.userId = null;  // NEW: Store user ID
        
        // DOM elements
        this.chatButton = document.getElementById('chat-button');
        this.chatWindow = document.getElementById('chat-window');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendButton = document.getElementById('send-button');
        this.minimizeButton = document.getElementById('minimize-chat');
        this.quickActions = document.getElementById('quick-actions');
        
        this.init();
    }
    
    init() {
        // Get user ID from your authentication system
        this.userId = this.getUserId();
        
        // Event listeners
        this.chatButton.addEventListener('click', () => this.toggleChat());
        this.minimizeButton.addEventListener('click', () => this.toggleChat());
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Quick action buttons
        const actionButtons = document.querySelectorAll('.quick-action-btn');
        actionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }
    
    /**
     * NEW METHOD: Get user ID from your authentication system
     * Modify this method based on how you handle authentication
     */
    getUserId() {
        // Option 1: Get from session storage (if you store it there after login)
        const sessionUserId = sessionStorage.getItem('userId');
        if (sessionUserId) return sessionUserId;
        
        // Option 2: Get from a cookie (if you use cookie-based auth)
        const cookieUserId = this.getCookie('user_id');
        if (cookieUserId) return cookieUserId;
        
        // Option 3: Get from a global JavaScript variable (if set on page load)
        if (typeof window.currentUserId !== 'undefined') {
            return window.currentUserId;
        }
        
        // Option 4: Get from URL parameter (for testing)
        const urlParams = new URLSearchParams(window.location.search);
        const urlUserId = urlParams.get('user_id');
        if (urlUserId) return urlUserId;
        
        // Option 5: Prompt user (for demo/testing purposes)
        // Remove this in production!
        const promptUserId = prompt('Enter your user ID (for testing):');
        if (promptUserId) {
            sessionStorage.setItem('userId', promptUserId);
            return promptUserId;
        }
        
        // Fallback to anonymous
        return 'anonymous';
    }
    
    /**
     * Helper method to get cookie value
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    toggleChat() {
        this.chatWindow.classList.toggle('open');
        this.chatButton.classList.toggle('active');
        
        // Initialize conversation on first open
        if (this.chatWindow.classList.contains('open') && !this.conversationId) {
            this.initializeConversation();
        }
        
        // Focus input when opening
        if (this.chatWindow.classList.contains('open')) {
            this.chatInput.focus();
        }
    }
    
    async initializeConversation() {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId  // MODIFIED: Pass user ID
                })
            });
            
            const data = await response.json();
            
            if (data.conversation_id) {
                this.conversationId = data.conversation_id;
                this.addBotMessage(data.response);
                
                if (data.show_quick_actions) {
                    this.showQuickActions();
                }
            }
        } catch (error) {
            console.error('Error initializing conversation:', error);
            this.addBotMessage('Sorry, I\'m having trouble connecting. Please try again later.');
        }
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message) return;
        
        // Clear input
        this.chatInput.value = '';
        
        // Add user message to UI
        this.addUserMessage(message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const payload = {
                conversation_id: this.conversationId,
                message: message,
                user_id: this.userId  // MODIFIED: Always include user ID
            };
            
            // If awaiting input for an action, include the action
            if (this.awaitingInput && this.currentAction) {
                payload.action = this.currentAction;
                this.awaitingInput = false;
                this.currentAction = null;
            }
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add bot response
            this.addBotMessage(data.response);
            
            // Handle requires_input state
            if (data.requires_input) {
                this.awaitingInput = true;
                this.currentAction = data.action;
                this.hideQuickActions();
            } else if (data.show_quick_actions) {
                this.showQuickActions();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addBotMessage('Sorry, I encountered an error. Please try again.');
        }
    }
    
    async handleQuickAction(action) {
        // Hide quick actions during processing
        this.hideQuickActions();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    action: action,
                    user_id: this.userId  // MODIFIED: Include user ID
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Add bot response
            this.addBotMessage(data.response);
            
            // Handle requires_input state
            if (data.requires_input) {
                this.awaitingInput = true;
                this.currentAction = data.action;
            } else if (data.show_quick_actions) {
                this.showQuickActions();
            }
            
        } catch (error) {
            console.error('Error handling quick action:', error);
            this.removeTypingIndicator();
            this.addBotMessage('Sorry, I encountered an error. Please try again.');
            this.showQuickActions();
        }
    }
    
    // ... rest of the methods remain the same ...
    // (Copy all other methods from your original chatbot.js)
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Chatbot();
});

/**
 * INTEGRATION EXAMPLES:
 * 
 * 1. For Session-Based Auth:
 *    After user logs in, store their ID:
 *    sessionStorage.setItem('userId', loggedInUserId);
 * 
 * 2. For JWT Auth:
 *    Decode JWT and extract user ID:
 *    const token = localStorage.getItem('authToken');
 *    const decoded = jwt_decode(token);
 *    window.currentUserId = decoded.userId;
 * 
 * 3. For Server-Side Rendered Pages:
 *    In your HTML template, inject user ID:
 *    <script>window.currentUserId = '{{ user.id }}';</script>
 * 
 * 4. For Cookie-Based Auth:
 *    Set a cookie after login:
 *    document.cookie = `user_id=${userId}; path=/`;
 */
