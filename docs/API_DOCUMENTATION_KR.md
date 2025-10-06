# API 문서

**GaiA-ABiz 백엔드 REST API 참조**

---

## 개요

- **Base URL**: `http://localhost:8000`
- **API 버전**: v1
- **인증**: JWT Bearer Token (프로덕션)
- **Content-Type**: `application/json`

---

## 대화형 문서

개발 서버 실행 후 자동 생성된 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 엔드포인트 목록

### RAG (검색 증강 생성)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/rag/search` | 의미적 유사도 검색 |
| POST | `/api/v1/rag/documents` | 문서 추가 |
| GET | `/api/v1/rag/stats` | 벡터 저장소 통계 |
| GET | `/api/v1/rag/health` | RAG 시스템 상태 |
| DELETE | `/api/v1/rag/documents/{doc_id}` | 문서 삭제 |

### 시스템

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스 체크 |
| GET | `/metrics` | 프로메테우스 메트릭 |

---

## RAG 엔드포인트

### 1. 의미적 검색

**POST** `/api/v1/rag/search`

벡터 유사도 기반 문서 검색을 수행합니다.

#### 요청

```json
{
  "query": "SK Hynix에 대해 알려주세요",
  "k": 3,
  "filter": {
    "source": "manual",
    "category": "company"
  }
}
```

**파라미터**:

| 이름 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `query` | string | ✅ | - | 검색 쿼리 |
| `k` | integer | ❌ | 3 | 반환할 최대 결과 수 |
| `filter` | object | ❌ | null | 메타데이터 필터 |

#### 응답

**200 OK**

```json
{
  "query": "SK Hynix에 대해 알려주세요",
  "results": [
    {
      "content": "SK Hynix는 메모리 반도체를 생산하는 글로벌 기업입니다...",
      "metadata": {
        "source": "manual",
        "category": "company",
        "created_at": "2025-10-05T10:00:00Z"
      },
      "score": 0.9234
    },
    {
      "content": "SK Hynix는 DRAM과 NAND 플래시 메모리 분야의 선두주자입니다...",
      "metadata": {
        "source": "wiki",
        "category": "company"
      },
      "score": 0.8756
    }
  ],
  "count": 2
}
```

**에러 응답**:

```json
{
  "detail": "벡터 저장소가 초기화되지 않았습니다"
}
```

#### cURL 예제

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "RAG란 무엇인가요?",
    "k": 5
  }'
```

#### Python 예제

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/rag/search",
    json={
        "query": "AI 플랫폼에 대해 설명해주세요",
        "k": 3,
        "filter": {"category": "technology"}
    }
)

results = response.json()
for result in results["results"]:
    print(f"Score: {result['score']:.4f}")
    print(f"Content: {result['content']}\n")
```

---

### 2. 문서 추가

**POST** `/api/v1/rag/documents`

하나 이상의 문서를 벡터 저장소에 추가합니다.

#### 요청

```json
{
  "documents": [
    "SK Hynix는 메모리 반도체를 생산합니다.",
    "GaiA는 AI 기반 플랫폼입니다."
  ],
  "metadata": {
    "source": "manual",
    "category": "company",
    "author": "admin"
  }
}
```

**파라미터**:

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `documents` | array[string] | ✅ | 추가할 문서 리스트 |
| `metadata` | object | ❌ | 모든 문서에 적용할 메타데이터 |

#### 응답

**200 OK**

```json
{
  "count": 2,
  "message": "2개 문서가 성공적으로 추가되었습니다",
  "ids": ["doc_001", "doc_002"]
}
```

**에러 응답**:

```json
{
  "detail": "문서 리스트가 비어있습니다"
}
```

#### cURL 예제

```bash
curl -X POST "http://localhost:8000/api/v1/rag/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "첫 번째 문서 내용입니다.",
      "두 번째 문서 내용입니다."
    ],
    "metadata": {
      "source": "api",
      "timestamp": "2025-10-05"
    }
  }'
```

#### Python 예제

```python
import requests

documents = [
    "RAG는 검색 증강 생성(Retrieval Augmented Generation)의 약자입니다.",
    "LangChain은 LLM 애플리케이션을 구축하는 프레임워크입니다.",
    "Milvus는 고성능 벡터 데이터베이스입니다."
]

response = requests.post(
    "http://localhost:8000/api/v1/rag/documents",
    json={
        "documents": documents,
        "metadata": {
            "source": "knowledge_base",
            "category": "ai_ml"
        }
    }
)

print(f"추가된 문서 수: {response.json()['count']}")
```

---

### 3. 벡터 저장소 통계

**GET** `/api/v1/rag/stats`

벡터 저장소의 현재 상태와 통계 정보를 반환합니다.

#### 요청

```bash
GET /api/v1/rag/stats
```

#### 응답

**200 OK**

```json
{
  "total_documents": 1542,
  "vector_dimension": 768,
  "index_type": "IVF_FLAT",
  "embedding_model": "sentence-transformers/all-mpnet-base-v2",
  "storage_backend": "milvus",
  "last_updated": "2025-10-05T14:32:10Z"
}
```

#### cURL 예제

```bash
curl -X GET "http://localhost:8000/api/v1/rag/stats"
```

#### Python 예제

```python
import requests

response = requests.get("http://localhost:8000/api/v1/rag/stats")
stats = response.json()

print(f"총 문서 수: {stats['total_documents']}")
print(f"임베딩 차원: {stats['vector_dimension']}")
print(f"임베딩 모델: {stats['embedding_model']}")
```

---

### 4. RAG 시스템 헬스 체크

**GET** `/api/v1/rag/health`

RAG 시스템의 각 구성 요소 상태를 확인합니다.

#### 요청

```bash
GET /api/v1/rag/health
```

#### 응답

**200 OK** (모든 구성 요소 정상)

```json
{
  "status": "healthy",
  "components": {
    "vector_store": {
      "status": "healthy",
      "latency_ms": 12
    },
    "embedding_model": {
      "status": "healthy",
      "latency_ms": 45
    },
    "llm": {
      "status": "healthy",
      "latency_ms": 230
    }
  },
  "timestamp": "2025-10-05T14:35:00Z"
}
```

**503 Service Unavailable** (구성 요소 장애)

```json
{
  "status": "unhealthy",
  "components": {
    "vector_store": {
      "status": "unhealthy",
      "error": "Connection timeout to Milvus"
    },
    "embedding_model": {
      "status": "healthy",
      "latency_ms": 42
    },
    "llm": {
      "status": "healthy",
      "latency_ms": 215
    }
  },
  "timestamp": "2025-10-05T14:36:00Z"
}
```

#### cURL 예제

```bash
curl -X GET "http://localhost:8000/api/v1/rag/health"
```

---

### 5. 문서 삭제

**DELETE** `/api/v1/rag/documents/{doc_id}`

특정 문서를 벡터 저장소에서 삭제합니다.

#### 요청

```bash
DELETE /api/v1/rag/documents/doc_001
```

**경로 파라미터**:

| 이름 | 타입 | 설명 |
|------|------|------|
| `doc_id` | string | 삭제할 문서 ID |

#### 응답

**200 OK**

```json
{
  "message": "문서 doc_001이 성공적으로 삭제되었습니다",
  "deleted_id": "doc_001"
}
```

**404 Not Found**

```json
{
  "detail": "문서 doc_001을 찾을 수 없습니다"
}
```

#### cURL 예제

```bash
curl -X DELETE "http://localhost:8000/api/v1/rag/documents/doc_001"
```

#### Python 예제

```python
import requests

doc_id = "doc_001"
response = requests.delete(f"http://localhost:8000/api/v1/rag/documents/{doc_id}")

if response.status_code == 200:
    print(f"문서 {doc_id} 삭제 완료")
else:
    print(f"삭제 실패: {response.json()['detail']}")
```

---

## 시스템 엔드포인트

### 1. 헬스 체크

**GET** `/health`

전체 시스템 상태를 확인합니다.

#### 응답

**200 OK**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

#### cURL 예제

```bash
curl -X GET "http://localhost:8000/health"
```

---

### 2. 프로메테우스 메트릭

**GET** `/metrics`

프로메테우스 형식의 메트릭을 반환합니다.

#### 응답

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/rag/search"} 1523

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1234
http_request_duration_seconds_bucket{le="0.5"} 1456
```

---

## 인증 (프로덕션)

프로덕션 환경에서는 JWT 토큰 기반 인증을 사용합니다.

### 토큰 획득

**POST** `/api/v1/auth/login`

```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**응답**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 인증된 요청

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"query": "검색 쿼리", "k": 3}'
```

**Python 예제**:

```python
import requests

# 로그인
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "user@example.com", "password": "password"}
)
token = login_response.json()["access_token"]

# 인증된 요청
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/api/v1/rag/search",
    headers=headers,
    json={"query": "검색 쿼리", "k": 3}
)
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파라미터 오류) |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스를 찾을 수 없음 |
| 422 | 유효성 검증 실패 |
| 500 | 서버 내부 오류 |
| 503 | 서비스 사용 불가 (구성 요소 장애) |

### 에러 응답 형식

```json
{
  "detail": "에러 메시지",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-10-05T14:40:00Z"
}
```

---

## 속도 제한 (프로덕션)

- **인증된 사용자**: 100 요청/분
- **미인증 사용자**: 20 요청/분

**속도 제한 초과 응답**:

```json
{
  "detail": "속도 제한 초과. 60초 후 다시 시도하세요",
  "retry_after": 60
}
```

---

## 버전 관리

API 버전은 URL 경로에 포함됩니다:

- **v1**: `/api/v1/*` (현재 버전)
- **v2**: `/api/v2/*` (향후 릴리스)

이전 버전은 최소 6개월간 지원됩니다.

---

## 페이지네이션

대량의 결과를 반환하는 엔드포인트는 페이지네이션을 지원합니다.

**요청**:

```json
{
  "query": "검색어",
  "limit": 20,
  "offset": 0
}
```

**응답**:

```json
{
  "results": [...],
  "total": 153,
  "limit": 20,
  "offset": 0,
  "next": "/api/v1/rag/search?offset=20&limit=20"
}
```

---

## 웹소켓 (실시간 스트리밍)

**연결**: `ws://localhost:8000/api/v1/rag/stream`

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/rag/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    query: "RAG에 대해 설명해주세요",
    stream: true
  }));
};

ws.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  console.log(chunk.content);
};
```

---

## SDK 및 클라이언트 라이브러리

### Python 클라이언트

```python
from gaia_abiz_client import RAGClient

client = RAGClient(base_url="http://localhost:8000")

# 검색
results = client.search("검색 쿼리", k=5)

# 문서 추가
client.add_documents(["문서1", "문서2"], metadata={"source": "api"})

# 통계 조회
stats = client.get_stats()
```

### TypeScript 클라이언트

```typescript
import { RAGClient } from '@gaia-abiz/client';

const client = new RAGClient({ baseUrl: 'http://localhost:8000' });

// 검색
const results = await client.search({ query: '검색 쿼리', k: 5 });

// 문서 추가
await client.addDocuments({
  documents: ['문서1', '문서2'],
  metadata: { source: 'api' }
});
```

---

## 테스트 환경

**Base URL**: `https://staging.gaia-abiz.example.com`

테스트 계정:
- Username: `test@example.com`
- Password: `test_password_123`

---

## 지원 및 문의

- **문서**: https://docs.gaia-abiz.example.com
- **GitHub 이슈**: https://github.com/your-org/gaia-abiz-backend/issues
- **이메일**: support@gaia-abiz.example.com

---

**API 버전**: v1.0.0
**마지막 업데이트**: 2025년 10월 5일
**상태**: ✅ 프로덕션 준비 완료
