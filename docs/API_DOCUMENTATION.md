# API Documentation

## Base URL

**Local Development**: `http://localhost:8000`
**Production**: `https://api.gaia-abiz.example.com`

## Authentication

Most endpoints require authentication using JWT Bearer tokens.

### Getting a Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the access token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### POST /auth/register

사용자 등록

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "password123",
  "full_name": "Test User"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-01T00:00:00"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

---

### POST /auth/login

사용자 로그인 및 토큰 발급

**Request Body**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

---

### POST /auth/refresh

Refresh Token을 사용하여 새 Access Token 발급

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### GET /auth/me

현재 로그인한 사용자 정보 조회

**Headers**:
- `Authorization: Bearer <access_token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-01T00:00:00"
}
```

**Example**:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

---

### POST /auth/logout

로그아웃 및 Refresh Token 무효화

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

## AI Agent Endpoints

### POST /agent/query

AI 에이전트에 질의

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "query": "What is the capital of France?",
  "agent_type": "general",
  "session_id": 1
}
```

**Response** (200 OK):
```json
{
  "response": "The capital of France is Paris.",
  "session_id": 1,
  "context": "Retrieved context from knowledge base...",
  "retrieval_results": [
    {
      "id": 123,
      "distance": 0.15,
      "text": "Paris is the capital and most populous city of France...",
      "metadata": "{\"source\": \"wikipedia\"}"
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is FastAPI?",
    "agent_type": "general"
  }'
```

---

### POST /agent/sessions

새 AI Agent 세션 생성

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "agent_type": "general"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "agent_type": "general",
  "created_at": "2025-10-01T00:00:00",
  "status": "active"
}
```

---

### GET /agent/sessions

사용자의 모든 세션 조회

**Headers**:
- `Authorization: Bearer <access_token>`

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "agent_type": "general",
    "created_at": "2025-10-01T00:00:00",
    "status": "active"
  },
  {
    "id": 2,
    "user_id": 1,
    "agent_type": "technical",
    "created_at": "2025-10-01T01:00:00",
    "status": "completed"
  }
]
```

---

### GET /agent/sessions/{session_id}/messages

특정 세션의 모든 메시지 조회

**Headers**:
- `Authorization: Bearer <access_token>`

**Path Parameters**:
- `session_id`: 세션 ID

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "session_id": 1,
    "role": "user",
    "content": "What is FastAPI?",
    "created_at": "2025-10-01T00:00:00"
  },
  {
    "id": 2,
    "session_id": 1,
    "role": "assistant",
    "content": "FastAPI is a modern, fast web framework...",
    "created_at": "2025-10-01T00:00:05"
  }
]
```

---

### POST /agent/knowledge-base

지식베이스에 새 문서 추가

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "title": "FastAPI Documentation",
  "content": "FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+...",
  "category": "technology",
  "tags": ["python", "fastapi", "web framework"]
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "title": "FastAPI Documentation",
  "content": "FastAPI is a modern, fast...",
  "category": "technology",
  "tags": ["python", "fastapi", "web framework"],
  "created_at": "2025-10-01T00:00:00"
}
```

---

### GET /agent/knowledge-base

지식베이스 문서 조회

**Headers**:
- `Authorization: Bearer <access_token>`

**Query Parameters**:
- `category` (optional): 카테고리 필터

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "title": "FastAPI Documentation",
    "content": "FastAPI is a modern...",
    "category": "technology",
    "tags": ["python", "fastapi"],
    "created_at": "2025-10-01T00:00:00"
  }
]
```

---

## Encryption Endpoints

### POST /encryption/encrypt

텍스트 암호화

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "plaintext": "Secret message"
}
```

**Response** (200 OK):
```json
{
  "ciphertext": "Z0FBQUFBQm1...(base64 encoded)"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/encryption/encrypt \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"plaintext": "Secret message"}'
```

---

### POST /encryption/decrypt

암호문 복호화

**Headers**:
- `Authorization: Bearer <access_token>`

**Request Body**:
```json
{
  "ciphertext": "Z0FBQUFBQm1..."
}
```

**Response** (200 OK):
```json
{
  "plaintext": "Secret message"
}
```

---

### POST /encryption/encrypt-file

파일 암호화

**Headers**:
- `Authorization: Bearer <access_token>`
- `Content-Type: multipart/form-data`

**Request Body** (multipart/form-data):
- `file`: 암호화할 파일

**Response** (200 OK):
- 암호화된 파일 (binary)
- `Content-Disposition: attachment; filename=encrypted_<original_filename>`

**Example**:
```bash
curl -X POST http://localhost:8000/encryption/encrypt-file \
  -H "Authorization: Bearer <your-access-token>" \
  -F "file=@document.pdf" \
  -o encrypted_document.pdf
```

---

### POST /encryption/decrypt-file

암호화된 파일 복호화

**Headers**:
- `Authorization: Bearer <access_token>`
- `Content-Type: multipart/form-data`

**Request Body** (multipart/form-data):
- `file`: 복호화할 파일

**Response** (200 OK):
- 복호화된 파일 (binary)

**Example**:
```bash
curl -X POST http://localhost:8000/encryption/decrypt-file \
  -H "Authorization: Bearer <your-access-token>" \
  -F "file=@encrypted_document.pdf" \
  -o document.pdf
```

---

## Monitoring Endpoints

### GET /monitoring/metrics

Prometheus 메트릭

**Response** (200 OK - Prometheus format):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/auth/me",status="200"} 150.0
...
```

**Example**:
```bash
curl http://localhost:8000/monitoring/metrics
```

---

### GET /monitoring/api-logs/stats

API 로그 통계

**Query Parameters**:
- `hours` (default: 24): 조회 시간 범위 (시간)

**Response** (200 OK):
```json
{
  "total_requests": 1523,
  "average_duration": 0.125,
  "success_rate": 98.5,
  "error_count": 23
}
```

**Example**:
```bash
curl http://localhost:8000/monitoring/api-logs/stats?hours=24
```

---

### GET /monitoring/api-logs/endpoints

엔드포인트별 통계

**Query Parameters**:
- `hours` (default: 24): 조회 시간 범위
- `limit` (default: 10): 반환할 엔드포인트 수

**Response** (200 OK):
```json
[
  {
    "endpoint": "/auth/login",
    "count": 450,
    "avg_duration": 0.234
  },
  {
    "endpoint": "/agent/query",
    "count": 320,
    "avg_duration": 2.145
  }
]
```

---

### GET /monitoring/agent-logs/stats

AI Agent 통계

**Query Parameters**:
- `hours` (default: 24): 조회 시간 범위

**Response** (200 OK):
```json
[
  {
    "agent_type": "general",
    "total_requests": 320,
    "success_count": 315,
    "error_count": 5,
    "avg_duration": 2.145,
    "total_tokens": 125000
  }
]
```

---

### GET /monitoring/health

헬스 체크

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T00:00:00",
  "database": "connected"
}
```

**Example**:
```bash
curl http://localhost:8000/monitoring/health
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

현재 구현되지 않음. 향후 추가 예정:
- 인증된 사용자: 1000 req/hour
- 비인증 사용자: 100 req/hour

---

## Pagination

대용량 데이터 조회 시 페이지네이션 사용:

**Query Parameters**:
- `skip` (default: 0): 건너뛸 항목 수
- `limit` (default: 100): 반환할 최대 항목 수

**Example**:
```bash
curl "http://localhost:8000/agent/knowledge-base?skip=0&limit=10"
```

---

## Webhooks

향후 지원 예정:
- AI Agent 작업 완료 알림
- 시스템 알림
- 오류 알림
