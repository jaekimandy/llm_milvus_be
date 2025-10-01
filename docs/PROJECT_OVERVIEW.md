# GaiA-ABiz Backend - Project Overview

## 프로젝트 정보

**프로젝트명**: SK Hynix GaiA (AI Agent)와 A.Biz 통합 Backend 개발
**기간**: 2025.10.16 ~ 2026.4.15
**장소**: 분당(정자)
**기술스택**: Python, FastAPI, Kubernetes, Docker, PostgreSQL, Milvus, LangChain, LangGraph

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway / Ingress                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Module  │  │  Monitoring  │  │  Encryption  │      │
│  │ OAuth2/JWT   │  │  Prometheus  │  │  AES-256     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │           AI Agent Module                        │       │
│  │  LangChain + LangGraph + RAG                    │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                    │                 │
                    ▼                 ▼
         ┌──────────────────┐  ┌──────────────────┐
         │   PostgreSQL     │  │   Milvus Vector  │
         │   Database       │  │   Database       │
         └──────────────────┘  └──────────────────┘
```

## 팀 구성 및 담당 영역

### PMO Team
- **QA (1명)**: 품질 보증, 테스트 전략
- **DBA (1명)**: 데이터베이스 관리, 성능 최적화
- **AA (1명)**: 애플리케이션 아키텍처

### BE 개발 (공통) - 3명

#### 1. 인증/인가 개발 (1명)
- **기술**: Python, FastAPI, Kubernetes, Docker, OAuth2.0, JWT
- **구현 내용**:
  - `/auth` 모듈
  - 사용자 등록/로그인
  - JWT 토큰 발급 및 검증
  - Refresh Token 관리
  - OAuth2.0 통합

#### 2. 모니터링, 로그처리, 통계용 Data API 개발 (1명)
- **기술**: Python, FastAPI, SQL, Kubernetes, Docker
- **구현 내용**:
  - `/monitoring` 모듈
  - Prometheus 메트릭 수집
  - 구조화된 로깅 (Structlog)
  - API 통계 및 분석
  - 헬스 체크 엔드포인트

#### 3. 암호화 공통모듈 개발 (1명)
- **기술**: Python, 보안/암호화 라이브러리, 키 관리 솔루션
- **구현 내용**:
  - `/encryption` 모듈
  - 필드 레벨 암호화 (Fernet)
  - 파일 암호화 (AES-256)
  - 키 관리 및 로테이션
  - PBKDF2 키 유도

### BE 개발 - 9명

#### AI Agent 및 Backend 개발 (9명)
- **기술**: Python, FastAPI, LangChain, LangGraph, Milvus, Kubernetes, SQL, PostgreSQL, Docker
- **구현 내용**:
  - `/agent` 모듈
  - LangGraph 기반 AI 워크플로우
  - RAG (Retrieval-Augmented Generation) 구현
  - Milvus 벡터 데이터베이스 연동
  - OpenAI API 통합
  - 세션 및 메시지 관리
  - 지식베이스 관리

## 주요 기능

### 1. Authentication & Authorization

**위치**: `auth/`

```python
# API 엔드포인트
POST /auth/register      # 사용자 등록
POST /auth/login         # 로그인 (JWT 발급)
POST /auth/refresh       # 토큰 갱신
GET  /auth/me            # 현재 사용자 정보
POST /auth/logout        # 로그아웃
```

**특징**:
- JWT 기반 인증
- Refresh Token 자동 갱신
- OAuth2.0 Password Flow
- Bcrypt 비밀번호 해싱

### 2. Monitoring & Logging

**위치**: `monitoring/`

```python
# API 엔드포인트
GET /monitoring/metrics             # Prometheus 메트릭
GET /monitoring/api-logs/stats      # API 통계
GET /monitoring/api-logs/endpoints  # 엔드포인트별 통계
GET /monitoring/agent-logs/stats    # AI 에이전트 통계
GET /monitoring/health              # 헬스 체크
```

**메트릭**:
- `http_requests_total`: 전체 HTTP 요청 수
- `http_request_duration_seconds`: 요청 처리 시간
- `active_requests`: 활성 요청 수
- `ai_agent_requests_total`: AI 에이전트 요청 수
- `database_queries_total`: DB 쿼리 수

### 3. Encryption

**위치**: `encryption/`

```python
# API 엔드포인트
POST /encryption/encrypt        # 텍스트 암호화
POST /encryption/decrypt        # 텍스트 복호화
POST /encryption/encrypt-file   # 파일 암호화
POST /encryption/decrypt-file   # 파일 복호화
```

**암호화 방식**:
- **텍스트**: Fernet (symmetric encryption)
- **파일**: AES-256-CBC
- **키 유도**: PBKDF2-HMAC-SHA256 (100,000 iterations)

### 4. AI Agent

**위치**: `agent/`

```python
# API 엔드포인트
POST /agent/query                       # AI 에이전트 질의
POST /agent/sessions                    # 세션 생성
GET  /agent/sessions                    # 세션 목록
GET  /agent/sessions/{id}/messages      # 세션 메시지 조회
POST /agent/knowledge-base              # 지식베이스 추가
GET  /agent/knowledge-base              # 지식베이스 조회
```

**워크플로우** (LangGraph):
```
사용자 쿼리
    │
    ▼
[Retrieve Context]  ← Milvus Vector DB
    │
    ▼
[Generate Response] ← OpenAI GPT-4
    │
    ▼
응답 반환
```

## 데이터베이스 스키마

**주요 테이블**:
- `users`, `refresh_tokens` - 인증/인가
- `agent_sessions`, `agent_messages`, `knowledge_base` - AI Agent
- `api_logs`, `agent_logs` - 모니터링

**Milvus Collections**:
- `gaia_embeddings` - 벡터 임베딩 (1024 dimensions for Voyage AI)

📚 **상세 스키마**: [ARCHITECTURE.md](./ARCHITECTURE.md)의 "Database Schemas" 섹션 참고

## 환경 변수

주요 설정:
- Database: PostgreSQL connection
- LLM: Claude AI (Anthropic) + Voyage AI embeddings
- Milvus: Vector database
- Security: JWT, encryption keys

📚 **상세 설정**: [LLM_CONFIGURATION.md](./LLM_CONFIGURATION.md) 참고

## 배포 환경

### 로컬 개발
```bash
docker-compose up -d
```

### 프로덕션
- Kubernetes with auto-scaling (3-10 replicas)
- PostgreSQL, Milvus, ETCD, MinIO

📚 **상세 가이드**:
- [QUICK_START.md](./QUICK_START.md) - 빠른 시작
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - 프로덕션 배포

## 성능 고려사항

### Database
- Connection Pool: 20 connections
- Max Overflow: 10
- Pool Pre-ping: Enabled

### AI Agent
- Token limit: 2000
- Temperature: 0.7
- Embedding model: text-embedding-ada-002
- Vector search: Top-K = 5

### Monitoring
- Metrics export: Prometheus format
- Log format: JSON
- Log level: INFO

## 보안 고려사항

1. **인증**: JWT with 30분 만료
2. **암호화**:
   - Password: Bcrypt
   - Data: Fernet/AES-256
   - Key derivation: PBKDF2 (100K iterations)
3. **키 관리**: 90일마다 키 로테이션
4. **네트워크**: HTTPS only (Ingress)
5. **Secrets**: Kubernetes Secrets 사용

## API 성능 지표

- 평균 응답 시간: < 200ms (API)
- AI Agent 응답: < 5s
- 동시 접속: 100+ connections
- 처리량: 1000+ req/sec

## 확장 계획

### Phase 1 (현재)
- 기본 인증/인가
- AI Agent RAG
- 모니터링 대시보드

### Phase 2 (예정)
- 다중 LLM 지원
- 고급 RAG (Hybrid Search)
- 캐싱 레이어 (Redis)
- 비동기 작업 큐 (Celery)

### Phase 3 (예정)
- 멀티테넌시
- A/B 테스팅
- 고급 분석 대시보드
- 자동 스케일링 최적화
