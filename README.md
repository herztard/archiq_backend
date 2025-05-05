# ArchIQ Backend

This repository contains the backend for ArchIQ, a comprehensive platform for property management and architectural services with AI-powered search capabilities.

**Production API:** The backend is hosted at https://api.slyamgazy.kz

**Documentation:** [API Documentation](https://api.slyamgazy.kz/api/schema/swagger-ui/)

NOTE: Since this is a newly registered domain, SDU's WiFi is blocking it.


## Team Members

| Name                  | Student ID  | Lecture Group | Practice Group | Role                                          |
|-----------------------|-------------|---------------|----------------|-----------------------------------------------|
| Adilzhan Slyamgazy    | 220103151   | 04-N          | 16-P           | Backend, AI-agent development, Database setup |
| Dauletkhan Izbergenov | 220103015   | 04-N          | 15-P           | Frontend                                      |
| Alikhan Toleberdyyev  | 220103050   | 04-N          | 16-P           | Frontend                                      |
| Bakdaulet Bekkhoja    | 220103014   | 04-N          | 15-P           | DevOps                                        |
| Aknur Bauyrzhankyzy   | 220103314   | 04-N          | 16-P           | PM, Manual testing, Design-scratching         |

## System Requirements

- Python 3.13
- PostgreSQL 17
- Docker and Docker Compose (optional, for containerized setup)
- Nginx (for production deployment)

## Installation Instructions

### Option 1: Using Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/archiq_backend.git

# 2. Navigate into the project directory
cd archiq_backend

# 3. Create .env file (see Environment Variables section below)
cp .env.example .env
# Edit .env with your configuration

# 4. Start the application with Docker Compose
# For local development:
docker-compose -f docker-compose.local.yml up -d --build

# For production:
docker-compose up -d --build
```

### Option 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/archiq_backend.git

# 2. Navigate into the project directory
cd archiq_backend

# 3. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment variables (see section below)
cp .env.example .env
# Edit .env with your configuration

# 6. Set up the database
python manage.py migrate

# 7. Start the development server
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database Configuration
DB_NAME=archiq
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# Django Configuration
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_DEBUG=True

# S3 / AWS Configuration
S3_BUCKET_NAME=your-bucket-name
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_URL=your-bucket-url
S3_BUCKET_FULL_URL=your-full-bucket-url
AWS_S3_CUSTOM_DOMAIN=your-custom-domain

# AI/LLM Configuration
EMBEDDING_MODEL=your-embedding-model
LLM_MODEL=your-llm-model
CHROMA_DB_PATH=your-chroma-db-path
OPENAI_API_KEY=your-openai-api-key

# LangSmith Configuration (Optional)
LANGSMITH_TRACING=False
LANGSMITH_ENDPOINT=your-langsmith-endpoint
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=your-langsmith-project
```

## Project Structure

```
archiq_backend/
├── agent/                # AI agent functionality
├── applications/         # Application management
├── archiq_backend/       # Main project settings
├── clients/              # External client integrations (S3, Mobizon)
├── location/             # Location-related functionality
├── marketing/            # Marketing tools and functionality
├── nginx/                # Nginx configuration
├── properties/           # Property management
├── support/              # Support features
├── users/                # User authentication and management
├── docker-compose.yml    # Docker configuration for production
├── docker-compose.local.yml # Docker configuration for local development
├── Dockerfile            # Docker image definition
└── requirements.txt      # Python dependencies
```

## Usage Guide

### API Endpoints

The backend provides RESTful API endpoints for various functionalities:

- `/accounts/` - User registration, authentication, and management
- `/properties/` - Property listing and search functionality
- `/residential-complexes/` - Residential complexes listing and search functionality
- `/blocks/` - Blocks listing and search functionality
- `/applications/` - Application management
- `/cities/` and `/districts/` - Location-based services
- `/support/reports/` - Support ticketing system
- `/banners/` - Marketing tools and campaigns
- `/agent/` - AI agent interactions and search
- `/states/` - AI agent message state management
- `/chroma/` - Vector storage management

For local development, access the API at `http://localhost:8000/`  
For production, access the API at `https://api.slyamgazy.kz/`

For detailed API documentation, run the server and visit:
```
http://localhost:8000/api/schema/swagger-ui/
```
Or in production:
```
https://api.slyamgazy.kz/api/schema/swagger-ui/
```

### AI Search Functionality

The platform includes advanced AI-powered search capabilities through the agent module, leveraging:
- OpenAI models for natural language understanding
- ChromaDB for vector search
- LangChain, LangGraph for agent workflows
- LangSmith for agent monitoring

## Known Issues / Limitations

- LLM, S3 and telegram integration, requires valid API keys for OpenAI, S3 and telegram

## Backend Tech Stack

| Category              | Technologies                           | Documentation                                                                            |
|-----------------------|----------------------------------------|------------------------------------------------------------------------------------------|
| **Backend Framework** | Django/Django REST Framework           | [Django](https://docs.djangoproject.com/), [DRF](https://www.django-rest-framework.org/) |
| **Database**          | PostgreSQL 17                          | [PostgreSQL](https://www.postgresql.org/docs/)                                           |
| **File Storage**      | ps.kz S3                               | [ps.kz](https://www.ps.kz)                                                               |
| **AI/ML - LLM**       | OpenAI                                 | [OpenAI API](https://platform.openai.com/docs/)                                          |
| **AI/ML - Framework** | LangChain                              | [LangChain](https://python.langchain.com/docs/)                                          |
| **AI/ML - Workflows** | LangGraph                              | [LangGraph](https://langchain-ai.github.io/langgraph/)                                   |
| **AI/ML - Vector DB** | ChromaDB                               | [ChromaDB](https://docs.trychroma.com/)                                                  |
| **AI/ML - Retriever** | LlamaIndex                             | [LlamaIndex](https://docs.llamaindex.ai/)                                                |
| **Containerization**  | Docker                                 | [Docker](https://docs.docker.com/)                                                       |
| **Web Server**        | Nginx                                  | [Nginx](https://nginx.org/en/docs/)                                                      |
| **SMS Integration**   | Mobizon                                | [Mobizon](https://mobizon.kz/)                                                           |

- **Backend Framework**: Django/Django REST Framework
- **Database**: PostgreSQL
- **File Storage**: ps.kz S3
- **AI/ML**: OpenAI, LangChain, LangGraph, ChromaDB, LlamaIndex
- **Containerization**: Docker
- **Web Server**: Nginx
- **SMS Integration**: Mobizon
