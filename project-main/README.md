# AI-Powered Customer Support Chatbot - MVP

A Flask-based customer support chatbot with Azure Cosmos DB integration, featuring real-time chat, quick actions, and feedback collection.

## Features

- ✅ Real-time chat interface with modern UI
- ✅ Quick action buttons (Track Order, Refund Status, Talk to Agent, Product Info)
- ✅ Rule-based response system
- ✅ Azure Cosmos DB for conversation persistence
- ✅ Thumbs up/down feedback collection
- ✅ Typing indicator and animations
- ✅ Responsive design
- ✅ RESTful API architecture

## Project Structure

```
MBA_PROJECT_MAIN_2/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # API endpoints
│   ├── db.py                # Cosmos DB client and operations
│   └── responses.py         # Response logic and quick actions
├── static/
│   ├── css/
│   │   └── chatbot.css      # Chatbot styling
│   └── js/
│       └── chatbot.js       # Chatbot JavaScript
├── templates/
│   └── index.html           # Main page with chatbot widget
├── config.py                # Application configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── run.py                   # Application entry point
└── README.md               # This file
```

## Prerequisites

- Python 3.8 or higher
- Azure Cosmos DB account
- pip (Python package manager)

## Setup Instructions

### 1. Clone or Download the Project

```bash
cd MBA_PROJECT_MAIN_2
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Azure Cosmos DB

1. Create an Azure Cosmos DB account (if you don't have one):
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new Cosmos DB account (Core SQL API)
   - Create a database named `chatbot_db`
   - Create a container named `conversations` with partition key `/id`

2. Get your connection details:
   - Endpoint URL (e.g., `https://your-account.documents.azure.com:443/`)
   - Primary Key (from Keys section in Azure Portal)

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

2. Edit `.env` and add your Azure Cosmos DB credentials:

```env
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-db-primary-key
COSMOS_DATABASE=chatbot_db
COSMOS_CONTAINER=conversations
SECRET_KEY=your-secret-key-here
```

### 6. Run the Application

```bash
python run.py
```

The application will start at `http://localhost:5000`

## API Endpoints

### POST /api/chat
Handle chat messages and quick actions

**Request:**
```json
{
  "conversation_id": "optional-existing-id",
  "message": "user message",
  "action": "optional-quick-action",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "conversation_id": "conversation-uuid",
  "response": "bot response text",
  "show_quick_actions": true,
  "requires_input": false
}
```

### GET /api/conversation/<conversation_id>
Retrieve conversation history

**Response:**
```json
{
  "id": "conversation-uuid",
  "user_id": "user-id",
  "messages": [
    {
      "id": "message-uuid",
      "role": "user|bot",
      "content": "message text",
      "timestamp": "ISO-8601 timestamp"
    }
  ],
  "timestamp": "ISO-8601 timestamp",
  "feedback": {
    "value": "up|down",
    "timestamp": "ISO-8601 timestamp"
  }
}
```

### POST /api/feedback
Submit thumbs up/down feedback

**Request:**
```json
{
  "conversation_id": "conversation-uuid",
  "feedback": "up|down"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully"
}
```

## Quick Actions

| Action | Description |
|--------|-------------|
| Track Order | Ask for Order ID and return mock tracking status |
| Refund Status | Ask for Order ID and return mock refund information |
| Talk to Agent | Display contact information and methods |
| Product Info | Show general product FAQ topics |

## Testing the Application

1. Open browser and navigate to `http://localhost:5000`
2. Click the chat button in the bottom-right corner
3. Try the following:
   - Click quick action buttons
   - Type general messages
   - Provide Order IDs when prompted
   - Submit feedback using thumbs up/down

## Deployment to Azure App Service

### Prerequisites
- Azure CLI installed
- Azure subscription

### Steps

1. Create `startup.txt`:
```bash
gunicorn --bind=0.0.0.0 --timeout 600 run:app
```

2. Login to Azure:
```bash
az login
```

3. Create resource group:
```bash
az group create --name chatbot-rg --location eastus
```

4. Create App Service Plan:
```bash
az appservice plan create --name chatbot-plan --resource-group chatbot-rg --sku B1 --is-linux
```

5. Create Web App:
```bash
az webapp create --resource-group chatbot-rg --plan chatbot-plan --name your-chatbot-app --runtime "PYTHON:3.11"
```

6. Configure environment variables:
```bash
az webapp config appsettings set --resource-group chatbot-rg --name your-chatbot-app --settings COSMOS_ENDPOINT="your-endpoint" COSMOS_KEY="your-key" COSMOS_DATABASE="chatbot_db" COSMOS_CONTAINER="conversations" SECRET_KEY="your-secret-key"
```

7. Deploy the application:
```bash
az webapp up --name your-chatbot-app --resource-group chatbot-rg
```

## Troubleshooting

### Cosmos DB Connection Issues
- Verify endpoint URL and key in `.env`
- Check network connectivity to Azure
- Ensure database and container exist

### Application Won't Start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)
- Review logs for error messages

### Frontend Issues
- Clear browser cache
- Check browser console for JavaScript errors
- Verify static files are being served correctly

## Future Enhancements

- AI/ML integration (Azure OpenAI, LUIS)
- Multi-language support
- File upload capability
- Live agent handoff
- Analytics dashboard
- Email notifications
- Authentication and user accounts

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: Azure Cosmos DB
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Azure App Service (planned)

## License

MIT License - feel free to use this project for learning and development purposes.

## Support

For issues or questions, please refer to the documentation or create an issue in the project repository.
