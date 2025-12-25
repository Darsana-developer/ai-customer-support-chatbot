// Chatbot JavaScript
class Chatbot {
    constructor() {
        this.conversationId = null;
        this.currentAction = null;
        this.awaitingInput = false;
        
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
            // Check if user is logged in
            const userId = sessionStorage.getItem('user_id');
            const userName = sessionStorage.getItem('user_name');
            
            if (!userId) {
                // Redirect to login if not authenticated
                window.location.href = '/login';
                return;
            }
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId
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
            // Get user_id from session storage
            const userId = sessionStorage.getItem('user_id');
            
            if (!userId) {
                window.location.href = '/login';
                return;
            }
            
            const payload = {
                conversation_id: this.conversationId,
                message: message,
                user_id: userId
            };
            
            // If awaiting input for an action, include the action
            if (this.awaitingInput && this.currentAction) {
                payload.action = this.currentAction;
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
            
            // Store conversation ID if returned
            if (data.conversation_id && !this.conversationId) {
                this.conversationId = data.conversation_id;
            }
            
            if (data.response) {
                this.addBotMessage(data.response);
                
                // Update state
                if (data.requires_input) {
                    this.awaitingInput = true;
                    this.currentAction = data.action;
                    this.hideQuickActions();
                } else {
                    this.awaitingInput = false;
                    this.currentAction = null;
                    
                    if (data.show_quick_actions) {
                        this.showQuickActions();
                    }
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator();
            this.addBotMessage('Sorry, I encountered an error. Please try again.');
        }
    }
    
    async handleQuickAction(action) {
        // Add action as user message
        const actionNames = {
            'track_order': '📦 Track Order',
            'refund_status': '🔄 Refund Status',
            'talk_to_agent': '💬 Talk to Agent',
            'product_info': 'ℹ️ Product Info'
        };
        
        this.addUserMessage(actionNames[action] || action);
        
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
                    action: action
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator();
            
            // Store conversation ID if returned
            if (data.conversation_id && !this.conversationId) {
                this.conversationId = data.conversation_id;
            }
            
            if (data.response) {
                this.addBotMessage(data.response);
                
                // Update state
                if (data.requires_input) {
                    this.awaitingInput = true;
                    this.currentAction = data.action;
                    this.hideQuickActions();
                } else {
                    this.awaitingInput = false;
                    this.currentAction = null;
                    
                    if (data.show_quick_actions) {
                        this.showQuickActions();
                    }
                }
            }
        } catch (error) {
            console.error('Error handling quick action:', error);
            this.removeTypingIndicator();
            this.addBotMessage('Sorry, I encountered an error. Please try again.');
        }
    }
    
    addUserMessage(text) {
        const messageDiv = this.createMessageElement('user', text);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(text) {
        const messageDiv = this.createMessageElement('bot', text);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createMessageElement(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        
        if (role === 'bot') {
            avatar.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
            `;
        } else {
            avatar.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
            `;
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = text;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();
        
        contentDiv.appendChild(bubbleDiv);
        contentDiv.appendChild(timeDiv);
        
        // Add feedback buttons only for bot messages
        if (role === 'bot') {
            const feedbackDiv = this.createFeedbackButtons();
            contentDiv.appendChild(feedbackDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }
    
    createFeedbackButtons() {
        const feedbackDiv = document.createElement('div');
        feedbackDiv.className = 'message-feedback';
        
        const thumbsUpBtn = document.createElement('button');
        thumbsUpBtn.className = 'feedback-btn';
        thumbsUpBtn.innerHTML = '👍';
        thumbsUpBtn.onclick = () => this.submitFeedback('up', thumbsUpBtn, feedbackDiv);
        
        const thumbsDownBtn = document.createElement('button');
        thumbsDownBtn.className = 'feedback-btn';
        thumbsDownBtn.innerHTML = '👎';
        thumbsDownBtn.onclick = () => this.submitFeedback('down', thumbsDownBtn, feedbackDiv);
        
        feedbackDiv.appendChild(thumbsUpBtn);
        feedbackDiv.appendChild(thumbsDownBtn);
        
        return feedbackDiv;
    }
    
    async submitFeedback(feedback, button, container) {
        try {
            await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    conversation_id: this.conversationId,
                    feedback: feedback
                })
            });
            
            // Visual feedback
            button.classList.add('active');
            
            // Disable other buttons in the same container
            const buttons = container.querySelectorAll('.feedback-btn');
            buttons.forEach(btn => {
                if (btn !== button) {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                }
            });
            
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
        `;
        
        const indicatorDiv = document.createElement('div');
        indicatorDiv.className = 'typing-indicator';
        indicatorDiv.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(indicatorDiv);
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    showQuickActions() {
        this.quickActions.classList.remove('hidden');
    }
    
    hideQuickActions() {
        this.quickActions.classList.add('hidden');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Chatbot();
});
