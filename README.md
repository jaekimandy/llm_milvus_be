# GaiA-ABiz Backend

SK Hynix GaiA (AI Agent)와 A.Biz 통합 Backend 개발 프로젝트

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes)](https://kubernetes.io/)

## 📚 Documentation

**전체 문서 목록**: [docs/README.md](./docs/README.md)

- 🚀 [Quick Start Guide](./docs/QUICK_START.md) - 5분 만에 시작하기
- 🤖 [LLM Configuration](./docs/LLM_CONFIGURATION.md) - Claude/OpenAI 설정 (Claude 권장!)
- 📖 [Project Overview](./docs/PROJECT_OVERVIEW.md) - 프로젝트 전체 개요
- 🔌 [API Documentation](./docs/API_DOCUMENTATION.md) - API 상세 문서
- 💻 [Development Guide](./docs/DEVELOPMENT_GUIDE.md) - 개발 가이드
- 🚢 [Deployment Guide](./docs/DEPLOYMENT_GUIDE.md) - 배포 가이드

## 프로젝트 개요

이 프로젝트는 SK Hynix의 GaiA AI Agent와 A.Biz 시스템을 통합하는 백엔드 서비스입니다.

**기간**: 2025.10.16 ~ 2026.4.15
**장소**: 분당(정자)
**팀 구성**: PMO 3명 + BE개발(공통) 3명 + BE개발 9명

### 주요 기능

- **인증/인가 (Authentication/Authorization)**: OAuth2.0 및 JWT 기반 보안
- **모니터링 및 로깅**: Prometheus 메트릭, 구조화된 로깅, API 통계
- **암호화**: 필드 레벨 암호화, 파일 암호화, 키 관리
- **AI Agent**: LangChain/LangGraph 기반 AI 에이전트, RAG (Retrieval-Augmented Generation)

## 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **AI/LLM**: LangChain, LangGraph, OpenAI
- **Vector DB**: Milvus
- **Authentication**: OAuth2.0, JWT
- **Monitoring**: Prometheus, Structlog
- **Encryption**: Cryptography, PyCryptodome
- **Container**: Docker, Kubernetes

## 프로젝트 구조

```
gaia-abiz-backend/
├── auth/                   # 인증/인가 모듈
│   ├── models.py          # User, RefreshToken 모델
│   ├── schemas.py         # Pydantic 스키마
│   ├── security.py        # JWT, OAuth2 보안
│   └── routes.py          # 인증 API 엔드포인트
├── monitoring/            # 모니터링 모듈
│   ├── logger.py          # 구조화된 로깅
│   ├── metrics.py         # Prometheus 메트릭
│   ├── models.py          # 로그 데이터 모델
│   └── routes.py          # 모니터링 API
├── encryption/            # 암호화 모듈
│   ├── crypto.py          # 암호화 서비스
│   ├── key_manager.py     # 키 관리
│   └── routes.py          # 암호화 API
├── agent/                 # AI Agent 모듈
│   ├── llm_client.py      # LLM 클라이언트
│   ├── vector_store.py    # Milvus 벡터 스토어
│   ├── graph_agent.py     # LangGraph 에이전트
│   ├── models.py          # 에이전트 데이터 모델
│   ├── schemas.py         # Pydantic 스키마
│   └── routes.py          # 에이전트 API
├── common/                # 공통 모듈
│   └── database.py        # 데이터베이스 설정
├── config/                # 설정
│   └── settings.py        # 환경 변수 설정
├── k8s/                   # Kubernetes 설정
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secrets.yaml.example
├── main.py                # FastAPI 애플리케이션
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 이미지 빌드
└── docker-compose.yml    # 로컬 개발 환경
```

## 시작하기

### 사전 요구사항

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+
- OpenAI API Key

### 로컬 개발 환경 설정

1. **저장소 클론**

```bash
cd gaia-abiz-backend
```

2. **환경 변수 설정**

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

3. **Docker Compose로 실행**

```bash
docker-compose up -d
```

4. **또는 직접 실행**

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
# (자동으로 테이블이 생성됩니다)

# 애플리케이션 실행
python main.py
```

5. **API 문서 접속**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Prometheus Metrics: http://localhost:9090/metrics

## API 엔드포인트

### 인증 (Authentication)

- `POST /auth/register` - 사용자 등록
- `POST /auth/login` - 로그인 (JWT 토큰 발급)
- `POST /auth/refresh` - 토큰 갱신
- `GET /auth/me` - 현재 사용자 정보
- `POST /auth/logout` - 로그아웃

### AI Agent

- `POST /agent/query` - AI 에이전트에 질의
- `POST /agent/sessions` - 새 세션 생성
- `GET /agent/sessions` - 세션 목록 조회
- `GET /agent/sessions/{id}/messages` - 세션 메시지 조회
- `POST /agent/knowledge-base` - 지식베이스에 문서 추가
- `GET /agent/knowledge-base` - 지식베이스 조회

### 모니터링 (Monitoring)

- `GET /monitoring/metrics` - Prometheus 메트릭
- `GET /monitoring/api-logs/stats` - API 통계
- `GET /monitoring/api-logs/endpoints` - 엔드포인트별 통계
- `GET /monitoring/agent-logs/stats` - AI 에이전트 통계
- `GET /monitoring/health` - 헬스 체크

### 암호화 (Encryption)

- `POST /encryption/encrypt` - 텍스트 암호화
- `POST /encryption/decrypt` - 텍스트 복호화
- `POST /encryption/encrypt-file` - 파일 암호화
- `POST /encryption/decrypt-file` - 파일 복호화

## Kubernetes 배포

### 1. Namespace 생성

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Secrets 생성

```bash
# secrets.yaml.example을 복사하여 실제 값으로 수정
cp k8s/secrets.yaml.example k8s/secrets.yaml
# secrets.yaml 편집 후
kubectl apply -f k8s/secrets.yaml
```

### 3. ConfigMap 적용

```bash
kubectl apply -f k8s/configmap.yaml
```

### 4. Deployment 배포

```bash
kubectl apply -f k8s/deployment.yaml
```

### 5. HPA (Horizontal Pod Autoscaler) 설정

```bash
kubectl apply -f k8s/hpa.yaml
```

### 6. Ingress 설정 (선택사항)

```bash
kubectl apply -f k8s/ingress.yaml
```

### 배포 확인

```bash
kubectl get pods -n gaia-abiz
kubectl get svc -n gaia-abiz
kubectl logs -f deployment/gaia-abiz-backend -n gaia-abiz
```

## 개발 가이드

### 새로운 API 엔드포인트 추가

1. `models.py`에 데이터 모델 정의
2. `schemas.py`에 Pydantic 스키마 정의
3. `routes.py`에 API 엔드포인트 구현
4. `main.py`에 라우터 등록

### AI Agent 커스터마이징

`agent/graph_agent.py`의 `GraphAgent` 클래스를 수정하여 에이전트 워크플로우를 커스터마이징할 수 있습니다.

### 암호화 설정

환경 변수 `ENCRYPTION_KEY`를 32바이트 이상의 안전한 키로 설정하세요. 프로덕션 환경에서는 키 관리 시스템(KMS)을 사용하는 것을 권장합니다.

## 모니터링

### Prometheus 메트릭

- `http_requests_total`: 전체 HTTP 요청 수
- `http_request_duration_seconds`: HTTP 요청 처리 시간
- `active_requests`: 활성 요청 수
- `ai_agent_requests_total`: AI 에이전트 요청 수
- `database_queries_total`: 데이터베이스 쿼리 수

### 로그

구조화된 JSON 로그가 stdout으로 출력됩니다. 프로덕션 환경에서는 ELK 스택이나 Datadog 등으로 수집할 수 있습니다.

## 보안

- JWT 토큰 기반 인증
- OAuth2.0 지원
- 필드 레벨 암호화
- HTTPS 권장 (Ingress에서 설정)
- 환경 변수로 민감 정보 관리
- Kubernetes Secrets 사용

## 테스트

```bash
pytest
```

## 라이센스

Private - SK Hynix

## 팀

- PMO: QA, DBA, AA
- BE 개발(공통): 인증/인가, 모니터링, 암호화
- BE 개발: AI Agent 및 Backend

## 연락처

프로젝트 관련 문의: [이메일 주소]
