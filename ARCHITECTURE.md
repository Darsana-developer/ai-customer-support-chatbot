# Architecture: Personalized AI Chatbot

## Data Flow Diagram

```
┌─────────────────┐
│   Web Browser   │
│   (Frontend)    │
└────────┬────────┘
         │ 1. Send message + user_id
         ↓
┌─────────────────────────────────────────────┐
│           Flask Backend (routes.py)          │
│  • Receives user_id from frontend           │
│  • Retrieves conversation from Cosmos DB    │
└────────┬───────────────────────┬────────────┘
         │                       │
         │ 2. Get user context   │ 3. Generate response
         ↓                       ↓
┌──────────────────┐    ┌─────────────────────┐
│   Database       │    │   AI Response        │
│   (db.py)        │    │   (responses.py)     │
│                  │    │                      │
│ • User profile   │    │ • Azure OpenAI API   │
│ • Order history  │───>│ • User context       │
│ • Preferences    │    │ • Conversation hist. │
│ • Past convos    │    └──────────────────────┘
└──────────────────┘
         ↓
┌─────────────────────────────────────────────┐
│         Azure Cosmos DB                      │
│                                              │
│  Documents:                                  │
│  ┌──────────────────────────────────────┐  │
│  │ type: "user_profile"                  │  │
│  │ - user_id, name, email, preferences   │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ type: "order"                         │  │
│  │ - order_id, status, items, refund     │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ type: "conversation"                  │  │
│  │ - messages[], user_id, timestamp      │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

## Key Components

### 1. Frontend (`static/js/chatbot.js`)
```javascript
// Captures user_id and sends with every request
{
  user_id: "user_john123",
  message: "Track my order",
  conversation_id: "abc-123"
}
```

### 2. Backend Routes (`app/routes.py`)
```python
# Retrieves user context before processing
user_context = db.get_user_context_summary(user_id)

# Passes context to AI
bot_response = handle_general_message(
    message, 
    conversation_history, 
    user_context  # ← NEW: User-specific data
)
```

### 3. Database Layer (`app/db.py`)
```python
# NEW: Methods for user data
get_user_profile(user_id)
get_user_orders(user_id)
get_order_by_id(order_id, user_id)
get_user_context_summary(user_id)  # ← Aggregates all user data
```

### 4. AI Response (`app/responses.py`)
```python
# Enhanced system prompt with user context
system_prompt += f"""
User Context:
- Name: {user_name}
- Recent Orders: 
  * Order #1001: Shipped - $89.99
  * Order #1002: Delivered - $149.99
- Preferences: Email contact preferred
"""

# Azure OpenAI generates personalized response
```

## Before vs After

### Before Implementation
```
User: "Track my order"
Bot: "Please provide your Order ID"  ❌ Generic

User: "Track order 1001"
Bot: "Status: [Random mock data]"    ❌ Not real
```

### After Implementation
```
User: "Track my order"
Bot: "Hi John! I can help. Which order? 
     You have:
     - Order #1001 (Shipped)
     - Order #1002 (Delivered)"      ✅ Personalized

User: "Track order 1001"
Bot: "Order #1001 Status: Shipped
     Items: Wireless Headphones
     Tracking: 1Z999AA12345678
     Est. Delivery: Jan 15, 2025"    ✅ Real data
```

## User Context Summary Structure

```json
{
  "user_id": "user_john123",
  "name": "John Smith",
  "total_orders": 3,
  "recent_orders": [
    {
      "order_id": "ORD1001",
      "status": "Shipped",
      "total": 89.99,
      "date": "2025-01-10T14:20:00Z"
    }
  ],
  "preferences": {
    "language": "en",
    "preferred_contact": "email"
  },
  "previous_issues": [
    "Asked about refund for order 1002"
  ]
}
```

## AI Personalization Flow

```
Step 1: User sends message
   ↓
Step 2: Backend retrieves user_context_summary
   ↓
Step 3: Build enhanced system prompt:
   "This is John Smith, he has 3 orders, 
    recently ordered Wireless Headphones..."
   ↓
Step 4: Send to Azure OpenAI with context
   ↓
Step 5: AI generates personalized response
   (references orders, uses name, etc.)
   ↓
Step 6: Return to user
```

## Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Order Tracking** | Mock random data | Real tracking from DB |
| **Greetings** | Generic "Hello!" | "Hi John! How can I help?" |
| **Context** | No memory of user | Knows order history |
| **Accuracy** | Hash-based fake data | Actual database queries |
| **Personalization** | None | Full user profile aware |
| **AI Quality** | Generic responses | Context-rich answers |

## Security Considerations

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ user_id from session/token
       ↓
┌──────────────────┐
│  Auth Middleware │ ← Add this in production
│  (Validates ID)  │
└──────┬───────────┘
       │ verified user_id
       ↓
┌──────────────────┐
│  Chatbot Routes  │
└──────────────────┘
```

**Important:** Always validate that the user_id matches the authenticated session!

## Scalability

### Current Setup
- User profiles in Cosmos DB
- Orders in Cosmos DB
- Conversations in Cosmos DB

### Production Options

**Option 1: Hybrid**
```
Cosmos DB (user profiles + conversations)
    ↓
External API (real-time order data)
```

**Option 2: Sync**
```
Main Database (orders, users)
    ↓ periodic sync
Cosmos DB (cached data for chatbot)
```

**Option 3: Direct**
```
Chatbot → Direct queries to main database
         (bypasses Cosmos DB)
```

## Next Enhancements

1. **Proactive Support**
   ```
   AI: "Hi John! I noticed your order #1001 
        is delayed. Would you like an update?"
   ```

2. **Product Recommendations**
   ```
   AI: "Based on your purchase of headphones,
        you might like our premium carrying case!"
   ```

3. **Sentiment Analysis**
   ```
   If user_sentiment < 0.3:
       escalate_to_human_agent()
   ```

4. **Multi-language**
   ```python
   if user_context['preferences']['language'] == 'es':
       system_prompt += "Respond in Spanish"
   ```

---

**Your chatbot now uses real data and provides intelligent, personalized support! 🚀**
