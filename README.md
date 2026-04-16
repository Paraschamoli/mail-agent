# Mail Agent 1 - HR Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-green.svg)](https://fastapi.tiangolo.com/)

An intelligent email-based job application processing system that automates HR workflows using AI-powered skills and modular architecture.

## 🚀 Features

### Core Capabilities
- **Intelligent Email Processing**: Automatically parses job application emails and extracts structured data.
- **Dynamic Requirements**: Configurable per-inbox job requirements such as LinkedIn, GitHub, resume, or portfolio.
- **Attachment Management**: Smart classification and storage of resumes, cover letters, and other assets.
- **Automated Triage**: AI-powered evaluation of application completeness.
- **Professional Replies**: Context-aware email responses generated for follow-up communications.
- **State Tracking**: Full audit trail of application progress and communications.

### Technical Features
- **Modular Skills System**: Extensible architecture with deterministic and LLM-powered skills.
- **Real-time Processing**: AgentMail webhook-based email processing.
- **Database Persistence**: Built on SQLAlchemy with support for local SQLite and production databases.
- **Docker Ready**: Containerized deployment with `docker-compose`.
- **API-First Design**: REST endpoints for inbox requirements, applicant state, and file access.
- **OpenAI Integration**: Advanced AI capabilities via OpenRouter.

## 🏗️ Architecture

```
┌─────────────────┐    ┌───────────┐    ┌─────────────────┐
│   AgentMail     │───▶│   ngrok   │───▶│   Mail Agent    │
│   Webhooks      │    │ (HTTPS)   │    │   FastAPI       │
└─────────────────┘    └───────────┘    └─────────────────┘
                                      │
                                      ▼
                               ┌─────────────────┐
                               │   Skills Engine │
                               │                 │
                               │ • Email Parser  │
                               │ • Attachment    │
                               │ • Triage        │
                               │ • Reply Composer│
                               │ • Requirements  │
                               └─────────────────┘
```

## 🧠 Skills Overview

| Skill | Type | Purpose |
|-------|------|---------|
| **Email Parser** | LLM | Extracts applicant data from email content |
| **Attachment Handler** | Deterministic | Classifies and saves file attachments |
| **Application Triage** | LLM | Evaluates application completeness |
| **HR Reply Composer** | LLM | Generates professional email responses |
| **Requirement Manager** | Deterministic | Manages per-inbox job requirements |

## 🚀 Zero to Hero: Running Locally

This project is designed to run locally with minimal setup. Follow these steps to get the agent processing emails in under 5 minutes.

### 1. Prepare your environment

```bash
git clone <repository-url>
cd mail-agent1
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Create AgentMail credentials

- Sign in to AgentMail.
- Create a new inbox for incoming applications.
- Copy your AgentMail API Key.
- Copy the Inbox ID.
- Save the Webhook Secret if AgentMail provides one.

### 3. Create your `.env` file

Use SQLite for the fastest local setup.
Get your agentmail related keys and inbox from [agentmail.to](https://www.agentmail.to/)

```bash
OPENROUTER_API_KEY=sk-or-v1-...
DATABASE_URL=sqlite:///./test.db
AGENTMAIL_API_KEY=your-agentmail-api-key
INBOX_ID=your-inbox-id
```

> `DATABASE_URL` can be a local SQLite file like `sqlite:///./test.db`, so you do not need PostgreSQL to run locally.

### 4. Initialize the database

```bash
python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 5. Start the FastAPI server in the primary terminal

```bash
uvicorn main:app --reload
```

You should see the app start and confirm the dashboard URL.

### 6. Start `ngrok` in a second terminal

```bash
ngrok http 8000
```

This opens a secure public HTTPS endpoint for AgentMail to call your local app.

### 7. Register the webhook in AgentMail

- Copy the `https://...` URL from `ngrok`.
- Set the webhook target to the root endpoint.
- Example:

```text
https://abcd1234.ngrok.io/
```

- Include a trailing slash if AgentMail requires it.
- Save the webhook.

### 8. Verify local UIs

- Admin Dashboard: `http://localhost:8000/dashboard`
- Bindu Agent interface: `http://localhost:3773`
- FastAPI docs: `http://localhost:8000/docs`

## 🔍 Monitoring & UIs

Use these URLs to verify that the app is running and to inspect health and state.

- `http://localhost:8000/dashboard` — Admin dashboard UI.
- `http://localhost:3773` — Local Bindu agent interface.
- `http://localhost:8000/docs` — FastAPI API documentation.

## 🧪 Testing the System

### E2E test with a real AgentMail email

1. Send an email to the configured AgentMail inbox.
2. Watch the `uvicorn` logs in the primary terminal.
3. Confirm the webhook event and processing output.
4. Open `http://localhost:8000/dashboard` to review state.

### Manual webhook simulation with `curl`

Send a simulated AgentMail webhook payload directly to `POST /`.

```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "message.received",
    "message": {
      "from_": "applicant@example.com",
      "thread_id": "thread-123",
      "inbox_id": "your-inbox-id",
      "message_id": "msg-123",
      "text": "Hello, I am applying for the job. My LinkedIn is https://linkedin.com/in/example.",
      "attachments": []
    }
  }'
```

A successful response looks like:

```json
{
  "status": "processed",
  "applicant_status": "PENDING"
}
```

## 📡 API Endpoints

### Webhook processing

- `POST /` — AgentMail webhook handler for `message.received` events.

### Applicant state

- `GET /applicants` — List all applicants.
- `GET /applicants/{thread_id}` — Fetch state for one thread.

### Requirements management

- `POST /requirements/{inbox_id}` — Create required fields.
- `PUT /requirements/{inbox_id}` — Update required fields.
- `GET /requirements/{inbox_id}` — Retrieve requirements.
- `DELETE /requirements/{inbox_id}` — Reset custom requirements.

### Files

- `GET /files/{file_id}` — Download saved attachment by record ID.

### Diagnostics

- `GET /skills` — List loaded skill metadata.
- `GET /dashboard` — Serve the admin dashboard.

## ⚙️ Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter/OpenAI API key | Yes |
| `DATABASE_URL` | Database connection URL | Yes |
| `AGENTMAIL_API_KEY` | AgentMail API key | Yes |
| `INBOX_ID` | AgentMail inbox ID | Yes |
| `AGENTMAIL_WEBHOOK_SECRET` | AgentMail Webhook Secret Key | Yes |

### Example `.env`

```bash
OPENROUTER_API_KEY=sk-or-v1-...
DATABASE_URL=sqlite:///./test.db
AGENTMAIL_API_KEY=your-agentmail-api-key
INBOX_ID=your-inbox-id
AGENTMAIL_WEBHOOK_SECRET=your-agentmail-webhook-secret
```

## 🏗️ Project Structure

```
mail-agent1/
├── main.py                 # FastAPI application + webhook orchestrator
├── main1.py                # Alternative entry point
├── skills/                 # Skill definitions for the agent
│   ├── email-parser.md
│   ├── attachment-handler.md
│   ├── application-triage.md
│   ├── hr-reply-composer.md
│   └── requirement-manager.md
├── skills_loader.py        # Skill loading utilities
├── static/
│   └── dashboard.html      # Admin dashboard HTML
├── uploads/                # Stored attachments
│   ├── resumes/
│   ├── cover_letters/
│   └── other/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## 🔧 Development Notes

- `DATABASE_URL` can be local SQLite for immediate testing.
- Run `python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"` after updating the database URL.
- The app ignores webhook events that are not `message.received`.
- The webhook root endpoint is `POST /`.

## 🚀 Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  mail-agent:
    build: .
    environment:
      - DATABASE_URL=postgresql://prod-db:5432/mailagent
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mailagent
      POSTGRES_USER: mailagent
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## 🤝 Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Commit your work: `git commit -m 'Add feature'`.
4. Push and open a pull request.

---

**Built for fast local setup, transparent debugging, and real-world HR automation workflows.**
