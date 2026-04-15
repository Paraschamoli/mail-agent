# Mail Agent 1 - HR Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-green.svg)](https://fastapi.tiangolo.com/)

An intelligent email-based job application processing system that automates HR workflows using AI-powered skills and modular architecture.

## 🚀 Features

### Core Capabilities
- **Intelligent Email Processing**: Automatically parses job application emails and extracts structured data
- **Dynamic Requirements**: Configurable per-inbox job requirements (LinkedIn, GitHub, resume, etc.)
- **Attachment Management**: Smart classification and storage of resume/cover letter attachments
- **Automated Triage**: AI-powered evaluation of application completeness
- **Professional Replies**: Context-aware email composition for HR responses
- **State Tracking**: Complete audit trail of application progress and communications

### Technical Features
- **Modular Skills System**: Extensible architecture with deterministic and LLM-powered skills
- **Real-time Processing**: Webhook-based email processing with immediate responses
- **Database Persistence**: PostgreSQL with comprehensive state management
- **Docker Ready**: Containerized deployment with docker-compose
- **API-First Design**: RESTful APIs for integration and monitoring
- **OpenAI Integration**: Advanced AI capabilities via OpenRouter

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AgentMail     │───▶│   Mail Agent    │───▶│   PostgreSQL    │
│   Webhooks      │    │   FastAPI       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
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

### Skills Overview

| Skill | Type | Purpose |
|-------|------|---------|
| **Email Parser** | LLM | Extracts applicant data from email content |
| **Attachment Handler** | Deterministic | Classifies and saves file attachments |
| **Application Triage** | LLM | Evaluates application completeness |
| **HR Reply Composer** | LLM | Generates professional email responses |
| **Requirement Manager** | Deterministic | Manages per-inbox job requirements |

## 📋 Prerequisites

- **Python**: 3.12 or higher
- **PostgreSQL**: 13+ database
- **Docker**: For containerized deployment
- **API Keys**:
  - OpenRouter API key (for OpenAI models)
  - AgentMail API key
  - Database connection string

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mail-agent1
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URL
   ```

5. **Run database migrations**
   ```bash
   python -c "from main import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Start the application**
   ```bash
   uvicorn main:app --reload
   ```

### Docker Deployment

1. **Build and run with docker-compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually**
   ```bash
   docker build -t mail-agent1 .
   docker run -p 8000:8000 --env-file .env mail-agent1
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | API key for OpenRouter/OpenAI | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `AGENTMAIL_API_KEY` | AgentMail service API key | Yes |
| `INBOX_ID` | AgentMail inbox identifier | Yes |

### Example .env file
```bash
OPENROUTER_API_KEY=sk-or-v1-...
DATABASE_URL=postgresql://user:password@localhost:5432/mailagent
AGENTMAIL_API_KEY=am-...
INBOX_ID=your-inbox-id
```

## 📖 Usage

### API Endpoints

#### Health Check
```http
GET /health
```

#### Webhook Processing
```http
POST /webhook
Content-Type: application/json

{
  "thread_id": "thread-123",
  "sender_email": "applicant@example.com",
  "email_body": "Hi, I'm applying...",
  "attachments": [...]
}
```

#### Job Requirements Management
```http
POST /requirements/{inbox_id}
GET /requirements/{inbox_id}
PUT /requirements/{inbox_id}
DELETE /requirements/{inbox_id}
```

#### Application Status
```http
GET /applications/{thread_id}
GET /applications
```

### Testing the System

1. **Send a test email** to your AgentMail inbox
2. **Check application status** via API
3. **Review processed data** in the database

## 🔧 Development

### Project Structure
```
mail-agent1/
├── main.py                 # FastAPI application
├── main1.py               # Alternative entry point
├── skills/                # AI skills directory
│   ├── email-parser.md
│   ├── attachment-handler.md
│   ├── application-triage.md
│   ├── hr-reply-composer.md
│   └── requirement-manager.md
├── skills_loader.py       # Skills loading utilities
├── uploads/               # File storage
│   ├── resumes/
│   ├── cover_letters/
│   └── other/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Adding New Skills

1. Create a new `.md` file in `skills/` directory
2. Follow the skill file format with YAML frontmatter and markdown body
3. Implement the required sections: Context, Logic, Output Format
4. Update `skills_loader.py` if needed

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=false` in environment
- [ ] Use production database (not SQLite)
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Enable HTTPS/SSL
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Docker Compose Production
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

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Add unit tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [AgentMail](https://agentmail.com/) - Email processing service
- [OpenAI](https://openai.com/) - AI model provider
- [SQLAlchemy](https://sqlalchemy.org/) - Database toolkit
- [Agno](https://github.com/agno-ai/agno) - AI agent framework

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review the skills files for implementation details

---

**Built with ❤️ for efficient HR automation**