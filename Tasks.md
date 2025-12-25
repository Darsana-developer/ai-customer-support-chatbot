# AI-Powered Customer Support Chatbot - MVP Tasks

## Phase 1: Project Setup

- [ ] **Task 1.1**: Create Flask project structure with folders: `app/`, `static/`, `templates/`, `config/`
- [ ] **Task 1.2**: Create `requirements.txt` with dependencies (Flask, azure-cosmos, python-dotenv, gunicorn)
- [ ] **Task 1.3**: Create `.env.example` file for environment variables (Cosmos DB connection, Azure settings)
- [ ] **Task 1.4**: Create `config.py` for application configuration

## Phase 2: Azure Cosmos DB Setup

- [ ] **Task 2.1**: Create Cosmos DB connection utility in `app/db.py`
- [ ] **Task 2.2**: Define database schema for conversations (id, user_id, messages[], timestamp, feedback)
- [ ] **Task 2.3**: Create CRUD operations for chat sessions (create, read, update)
- [ ] **Task 2.4**: Create function to store feedback (thumbs up/down)

## Phase 3: Backend API Development

- [ ] **Task 3.1**: Create main Flask app entry point `app/__init__.py`
- [ ] **Task 3.2**: Create `/api/chat` POST endpoint to handle user messages
- [ ] **Task 3.3**: Create `/api/conversation` GET endpoint to retrieve chat history
- [ ] **Task 3.4**: Create `/api/feedback` POST endpoint to store thumbs up/down
- [ ] **Task 3.5**: Implement simple rule-based response logic for quick actions (Track Order, Refund Status, Talk to Agent, Product Info)
- [ ] **Task 3.6**: Add error handling and logging

## Phase 4: Frontend UI Development

- [ ] **Task 4.1**: Create base HTML template `templates/index.html`
- [ ] **Task 4.2**: Create chatbot widget CSS in `static/css/chatbot.css` (floating button, chat window, message bubbles)
- [ ] **Task 4.3**: Implement chat window header with bot avatar, status indicator, close/minimize buttons
- [ ] **Task 4.4**: Implement conversation area with user/bot message styling and timestamps
- [ ] **Task 4.5**: Implement user input section with text field and send button
- [ ] **Task 4.6**: Implement quick reply buttons (Track Order, Refund Status, Talk to Agent, Product Info)
- [ ] **Task 4.7**: Implement thumbs up/down feedback UI
- [ ] **Task 4.8**: Create chatbot JavaScript in `static/js/chatbot.js` for API interactions
- [ ] **Task 4.9**: Add typing indicator animation
- [ ] **Task 4.10**: Add open/close animation for chat widget

## Phase 5: Integration & Testing

- [ ] **Task 5.1**: Connect frontend to backend API endpoints
- [ ] **Task 5.2**: Test conversation flow end-to-end
- [ ] **Task 5.3**: Test feedback submission and storage
- [ ] **Task 5.4**: Test quick action buttons functionality
- [ ] **Task 5.5**: Verify Cosmos DB data persistence

## Phase 6: Azure Deployment

- [ ] **Task 6.1**: Create `startup.txt` for Azure App Service (gunicorn command)
- [ ] **Task 6.2**: Create Azure App Service configuration files
- [ ] **Task 6.3**: Configure environment variables in Azure App Service
- [ ] **Task 6.4**: Deploy Flask app to Azure App Service
- [ ] **Task 6.5**: Verify Cosmos DB connectivity in production
- [ ] **Task 6.6**: Test deployed application

## File Structure (Expected)

```
MBA_PROJECT_MAIN_2/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── db.py
│   └── responses.py
├── static/
│   ├── css/
│   │   └── chatbot.css
│   └── js/
│       └── chatbot.js
├── templates/
│   └── index.html
├── config.py
├── requirements.txt
├── .env.example
├── startup.txt
└── run.py
```

## Quick Action Responses (MVP Scope)

| Action | Response Type |
|--------|---------------|
| Track Order | Ask for Order ID, return mock status |
| Refund Status | Ask for Order ID, return mock refund info |
| Talk to Agent | Display contact info/message |
| Product Info | Return general product FAQ |
