# GaiA-ABiz Backend Architecture

## System Overview

GaiA-ABiz is a modern, AI-powered backend system built with FastAPI, Claude AI, and Voyage AI embeddings. It provides authentication, monitoring, encryption, and a sophisticated AI agent with RAG (Retrieval Augmented Generation) capabilities.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Layer                              │
│  (REST API Clients, Frontend Applications, Mobile Apps)          │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ HTTP/REST
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│                        FastAPI Application                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │   Auth     │  │ Monitoring │  │ Encryption │  │ AI Agent  │ │
│  │  (OAuth2)  │  │(Prometheus)│  │  (Fernet)  │  │(LangGraph)│ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
┌───────────────▼──┐  ┌────────▼────────┐  ┌──▼──────────────────┐
│   PostgreSQL     │  │  Milvus Vector  │  │   External APIs     │
│   (Relational)   │  │    Database     │  │                     │
│                  │  │                 │  │  • Claude AI        │
│  • Users         │  │  • Embeddings   │  │  • Voyage AI        │
│  • Sessions      │  │  • Documents    │  │                     │
│  • Tokens        │  │  • Semantic     │  │  (Anthropic Stack)  │
│  • Messages      │  │    Search       │  │                     │
└──────────────────┘  └────────┬────────┘  └─────────────────────┘
                               │
                         ┌─────┴─────┐
                         │           │
                    ┌────▼────┐ ┌───▼────┐
                    │  ETCD   │ │ MinIO  │
                    │ (Meta)  │ │ (Data) │
                    └─────────┘ └────────┘
```

## Technology Stack

### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11**: Latest stable Python version
- **Uvicorn**: ASGI server for FastAPI

### AI & LLM
- **Claude Sonnet 4**: Latest Anthropic AI model for chat
- **Voyage AI (voyage-3)**: Embeddings optimized for Claude
- **LangChain**: LLM application framework
- **LangGraph**: Workflow orchestration for AI agents

### Databases
- **PostgreSQL 16**: Primary relational database
- **Milvus v2.3.3**: Vector database for embeddings
- **ETCD v3.5.5**: Metadata storage for Milvus
- **MinIO**: Object storage for Milvus

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local development orchestration
- **Kubernetes**: Production deployment (optional)

### Monitoring & Logging
- **Prometheus**: Metrics collection
- **Structlog**: Structured logging
- **Python JSON Logger**: JSON log formatting

### Security
- **OAuth2.0 + JWT**: Authentication & authorization
- **Fernet + AES-256**: Data encryption
- **PBKDF2-HMAC**: Key derivation
- **Bcrypt**: Password hashing

## Module Architecture

### 1. Authentication Module (`auth/`)

```
auth/
├── routes.py          # Auth endpoints (login, register, refresh)
├── models.py          # User, Token database models
├── security.py        # JWT, password hashing
└── oauth.py           # OAuth2.0 implementation
```

**Features:**
- User registration with email validation
- JWT-based authentication (access + refresh tokens)
- OAuth2.0 password flow
- Token refresh mechanism
- Password hashing with bcrypt

**Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user

### 2. AI Agent Module (`agent/`)

```
agent/
├── routes.py          # Agent endpoints
├── graph_agent.py     # LangGraph workflow
├── llm_client.py      # LLM abstraction (Claude/OpenAI)
├── vector_store.py    # Milvus client
└── models.py          # Session, Message models
```

**Features:**
- Multi-provider LLM support (Claude, OpenAI)
- RAG with semantic search
- Conversation history management
- Session-based interactions
- Context retrieval from vector database

**Workflow:**
```
User Query
    │
    ├─→ Retrieve Context (Vector Search)
    │      │
    │      ├─→ Generate Embeddings (Voyage AI)
    │      └─→ Search Similar Docs (Milvus)
    │
    └─→ Generate Response (Claude AI)
           │
           └─→ Return with Retrieved Context
```

**Endpoints:**
- `POST /agent/query` - Ask the AI agent
- `POST /agent/sessions` - Create new session
- `GET /agent/sessions` - List user sessions
- `GET /agent/sessions/{id}/messages` - Get session messages

### 3. Monitoring Module (`monitoring/`)

```
monitoring/
├── prometheus.py      # Metrics collection
└── logging.py         # Structured logging setup
```

**Features:**
- Request duration metrics
- Request count by endpoint
- Active requests gauge
- Structured JSON logging
- Request ID tracking

**Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `http_requests_in_progress` - Active requests

### 4. Encryption Module (`encryption/`)

```
encryption/
├── crypto.py          # Encryption/decryption logic
└── key_management.py  # Key rotation and management
```

**Features:**
- Fernet symmetric encryption
- AES-256 encryption support
- PBKDF2-HMAC key derivation
- Automatic key rotation
- Secure key storage

### 5. Common Module (`common/`)

```
common/
├── database.py        # Database connection
└── dependencies.py    # FastAPI dependencies
```

**Features:**
- SQLAlchemy ORM setup
- Connection pooling
- Dependency injection
- Database session management

## Data Flow

### Authentication Flow

```
1. User Registration
   Client → POST /auth/register
        → Validate email
        → Hash password (bcrypt)
        → Create user in PostgreSQL
        → Return success

2. User Login
   Client → POST /auth/login
        → Verify credentials
        → Generate JWT tokens
        → Store refresh token in PostgreSQL
        → Return access + refresh tokens

3. Protected Request
   Client → Request with Bearer token
        → Validate JWT
        → Extract user ID
        → Execute request
        → Return response

4. Token Refresh
   Client → POST /auth/refresh with refresh token
        → Validate refresh token
        → Generate new access token
        → Return new tokens
```

### AI Agent Query Flow

```
1. User sends query
   Client → POST /agent/query
        → Authenticate user
        → Load/create session

2. Retrieve context (RAG)
   Query → Generate embedding (Voyage AI)
        → Search Milvus (vector similarity)
        → Extract top-K documents

3. Generate response
   Context + Query → Format prompt
                  → Send to Claude AI
                  → Receive response

4. Store and return
   Save to PostgreSQL → Message history
   Return → Client with response + sources
```

### Document Ingestion Flow

```
1. Prepare documents
   Documents → Extract text
            → Split into chunks

2. Generate embeddings
   Chunks → Voyage AI API
         → 1024-dim vectors

3. Store in Milvus
   Vectors + Text + Metadata → Milvus
                             → Create indexes
                             → Enable search
```

## Database Schemas

### PostgreSQL

**users**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**refresh_tokens**
```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**agent_sessions**
```sql
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    agent_type VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);
```

**agent_messages**
```sql
CREATE TABLE agent_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES agent_sessions(id),
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    message_metadata JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Milvus

**gaia_embeddings** Collection
```python
{
    "id": INT64 (primary, auto_id),
    "embedding": FLOAT_VECTOR (dim=1024),  # Voyage AI voyage-3 dimensions
    "text": VARCHAR (max_length=65535),
    "metadata": VARCHAR (max_length=65535)  # JSON string
}
```

**Index:**
- Type: IVF_FLAT
- Metric: L2 (Euclidean distance)
- nlist: 1024

## API Design

### RESTful Principles

- **Resource-based URLs**: `/users/{id}`, `/sessions/{id}`
- **HTTP methods**: GET, POST, PUT, DELETE
- **Status codes**: 200, 201, 400, 401, 404, 500
- **JSON payloads**: All requests/responses use JSON

### Authentication

All protected endpoints require:
```http
Authorization: Bearer <access_token>
```

### Error Responses

```json
{
    "detail": "Error message",
    "code": "ERROR_CODE",
    "timestamp": "2025-10-01T12:00:00Z"
}
```

### Pagination

```http
GET /resources?skip=0&limit=10
```

## Security Architecture

### Defense in Depth

1. **Network Layer**
   - Docker network isolation
   - Firewall rules
   - TLS/HTTPS in production

2. **Application Layer**
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection
   - CORS configuration

3. **Authentication Layer**
   - JWT with short expiration
   - Refresh token rotation
   - Password complexity requirements
   - Rate limiting

4. **Data Layer**
   - Encrypted sensitive fields
   - Database access controls
   - Audit logging
   - Regular backups

### Secrets Management

```bash
.env (Never commit!)
├── API Keys (Claude, Voyage)
├── Database credentials
├── Encryption keys
└── JWT secret
```

## Performance Optimizations

### Database
- Connection pooling (20 connections)
- Query optimization with indexes
- Lazy loading for relationships

### Caching
- Milvus index for fast vector search
- Session caching in memory

### Async Operations
- Async FastAPI endpoints
- Async database queries
- Async LLM calls

### Batch Processing
- Batch embedding generation
- Bulk inserts to Milvus

## Scalability

### Horizontal Scaling

```
                  Load Balancer
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    API Instance   API Instance   API Instance
         │             │             │
         └─────────────┼─────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
       PostgreSQL            Milvus Cluster
    (with replicas)         (distributed)
```

### Vertical Scaling

- Increase container resources
- Tune database parameters
- Optimize indexes
- Add caching layer (Redis)

## Deployment

### Development (Docker Compose)

```bash
docker-compose up -d
```

### Production (Kubernetes)

```yaml
Deployments:
├── api (3 replicas)
├── postgres (StatefulSet)
├── milvus (StatefulSet)
├── etcd (StatefulSet)
└── minio (StatefulSet)

Services:
├── api (LoadBalancer)
├── postgres (ClusterIP)
└── milvus (ClusterIP)
```

## Monitoring & Observability

### Metrics (Prometheus)
- Request rates
- Response times
- Error rates
- Database connection pool
- Milvus query performance

### Logging (Structlog)
- Request/response logging
- Error tracking
- User actions
- System events

### Tracing (Future)
- OpenTelemetry integration
- Distributed tracing
- Performance profiling

## Testing Strategy

### Unit Tests
- Individual module testing
- Mock external dependencies
- Database fixtures

### Integration Tests
- API endpoint testing
- Database integration
- LLM integration

### End-to-End Tests
- Full workflow testing
- User journey simulation

## Future Enhancements

### Planned Features
1. **WebSocket support** for streaming responses
2. **Caching layer** with Redis
3. **Rate limiting** per user
4. **Admin dashboard** for management
5. **Multi-tenancy** support
6. **GraphQL API** alongside REST

### Performance Improvements
1. **Query optimization** with materialized views
2. **CDN integration** for static assets
3. **Database sharding** for scale
4. **Async background tasks** with Celery

## Development Guidelines

### Code Organization
- **Modular design**: Each module is self-contained
- **Dependency injection**: Use FastAPI dependencies
- **Type hints**: All functions have type annotations
- **Docstrings**: Document all public APIs

### Best Practices
1. **Use async/await** for I/O operations
2. **Validate inputs** with Pydantic
3. **Handle errors gracefully** with proper HTTP codes
4. **Log important events** with structured logging
5. **Write tests** for new features

## Configuration Management

### Environment Variables

All configuration via `.env`:

```bash
# Application
APP_NAME=GaiA-ABiz-Backend
DEBUG=False

# Database
DATABASE_URL=postgresql://...

# LLM & Embeddings
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=...

# Security
SECRET_KEY=...
ENCRYPTION_KEY=...
```

### Configuration Loading

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    # ... more settings

    class Config:
        env_file = ".env"
```

## Summary

GaiA-ABiz provides a robust, scalable architecture for AI-powered applications:

- ✅ **Modern stack**: FastAPI + Python 3.11
- ✅ **AI-first**: Claude + Voyage AI (Anthropic stack)
- ✅ **Secure**: OAuth2, JWT, encryption
- ✅ **Observable**: Metrics, logging, monitoring
- ✅ **Scalable**: Containerized, cloud-ready
- ✅ **Maintainable**: Modular, tested, documented

## Reference Documentation

- [LLM Configuration](LLM_CONFIGURATION.md)
- [Milvus Setup](MILVUS_SETUP.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Development Guide](DEVELOPMENT_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
