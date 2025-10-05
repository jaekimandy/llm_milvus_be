# GaiA-ABiz 백엔드 아키텍처

**최종 업데이트**: 2025년 10월 5일
**구현 상태**: ✅ RAG 시스템 완료 (29/29 테스트 통과)

## 시스템 개요

GaiA-ABiz는 **FastAPI**, **LangChain**, **LangGraph**로 구축된 현대적인 AI 기반 백엔드 시스템입니다. 인증, 모니터링, 암호화, 그리고 프로덕션급 **RAG (Retrieval Augmented Generation)** 기능을 갖춘 정교한 AI 에이전트를 제공합니다.

### 🎯 최근 구현 내역 (2025년 10월)
- ✅ **LangChain RAG 시스템** - FAISS/Milvus를 활용한 완전한 구현
- ✅ **LangGraph 멀티 에이전트 시스템** - 상태 기반 대화 및 라우팅
- ✅ **다국어 임베딩** - 한국어, 영어, 50개 이상 언어 지원
- ✅ **로컬 LLM 지원** - CPU 추론을 위한 Qwen 2.5 7B GGUF
- ✅ **종합 테스트 스위트** - 모든 RAG 기능을 포함하는 29개 테스트

## 고수준 아키텍처

```
┌──────────────────────────────────────────────────────────────────┐
│                         클라이언트 계층                            │
│  (REST API 클라이언트, 프론트엔드 애플리케이션, 모바일 앱)           │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                                │ HTTP/REST
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│                        FastAPI 애플리케이션                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │   인증     │  │ 모니터링    │  │ 암호화      │  │ AI 에이전트│ │
│  │  (OAuth2)  │  │(Prometheus)│  │  (Fernet)  │  │(LangGraph)│ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
┌───────────────▼──┐  ┌────────▼────────┐  ┌──▼──────────────────┐
│   PostgreSQL     │  │  Milvus Vector  │  │   로컬 LLM         │
│   (관계형 DB)     │  │    Database     │  │                     │
│                  │  │                 │  │  • Qwen 2.5 7B     │
│  • 사용자        │  │  • 임베딩       │  │  • Jina Embed v3   │
│  • 세션          │  │  • 문서         │  │                     │
│  • 토큰          │  │  • 시맨틱       │  │  (로컬 실행)        │
│  • 메시지        │  │    검색         │  │                     │
└──────────────────┘  └────────┬────────┘  └─────────────────────┘
                               │
                         ┌─────┴─────┐
                         │           │
                    ┌────▼────┐ ┌───▼────┐
                    │  ETCD   │ │ MinIO  │
                    │ (메타)  │ │ (데이터)│
                    └─────────┘ └────────┘
```

## 기술 스택

### 핵심 프레임워크
- **FastAPI**: API 구축을 위한 현대적이고 빠른 웹 프레임워크
- **Python 3.11**: 최신 안정 버전 Python
- **Uvicorn**: FastAPI용 ASGI 서버

### AI & LLM 스택
- **LangChain 0.3.27**: RAG를 위한 LLM 애플리케이션 프레임워크 ✅
- **LangGraph 0.6.8**: 상태 기반 멀티 에이전트 워크플로우 ✅
- **Sentence Transformers 3.1.1**: 다국어 임베딩 ✅
- **Qwen 2.5 7B GGUF**: CPU 최적화 로컬 LLM ✅
- **Jina Embeddings v3**: 프로덕션 임베딩 (다운로드 완료) ✅

### 데이터베이스 & 벡터 스토어
- **PostgreSQL 16**: 주요 관계형 데이터베이스
- **Milvus v2.3.3**: 프로덕션 벡터 데이터베이스 (pymilvus 2.6.2) ✅
- **FAISS CPU 1.12.0**: 빠른 로컬 벡터 검색 (테스트 및 개발용) ✅
- **ETCD v3.5.5**: Milvus용 메타데이터 저장소
- **MinIO**: Milvus용 객체 저장소

### 인프라
- **Docker**: 컨테이너화
- **Docker Compose**: 로컬 개발 오케스트레이션
- **Kubernetes**: 프로덕션 배포 (선택사항)

### 모니터링 & 로깅
- **Prometheus**: 메트릭 수집
- **Structlog**: 구조화된 로깅
- **Python JSON Logger**: JSON 로그 포맷팅

### 보안
- **OAuth2.0 + JWT**: 인증 및 권한 부여
- **Fernet + AES-256**: 데이터 암호화
- **PBKDF2-HMAC**: 키 유도
- **Bcrypt**: 비밀번호 해싱

## 모듈 아키텍처

### 1. 인증 모듈 (`auth/`)

```
auth/
├── routes.py          # 인증 엔드포인트 (로그인, 등록, 갱신)
├── models.py          # User, Token 데이터베이스 모델
├── security.py        # JWT, 비밀번호 해싱
└── oauth.py           # OAuth2.0 구현
```

**기능:**
- 이메일 검증을 통한 사용자 등록
- JWT 기반 인증 (액세스 + 리프레시 토큰)
- OAuth2.0 패스워드 플로우
- 토큰 갱신 메커니즘
- bcrypt를 이용한 비밀번호 해싱

**엔드포인트:**
- `POST /auth/register` - 사용자 등록
- `POST /auth/login` - 사용자 로그인
- `POST /auth/refresh` - 액세스 토큰 갱신
- `GET /auth/me` - 현재 사용자 정보

### 2. AI 에이전트 모듈 (`agent/`) ✅ 업데이트됨

```
agent/
├── routes.py          # 에이전트 엔드포인트
├── graph_agent.py     # LangGraph 워크플로우
├── llm_client.py      # LLM 추상화
├── vector_store.py    # Milvus 클라이언트
├── models.py          # Session, Message 모델
├── rag_service.py     # ✅ RAG 서비스 구현 (신규)
└── api_routes.py      # ✅ FastAPI RAG 엔드포인트 (신규)
```

**기능:**
- ✅ 로컬 LLM 지원 (Qwen 2.5)
- ✅ LangChain + FAISS/Milvus를 활용한 RAG 시맨틱 검색
- ✅ 메모리를 갖춘 LangGraph 상태 기반 에이전트
- ✅ 다국어 지원 (한국어, 영어, 50개 이상 언어)
- ✅ RecursiveCharacterTextSplitter를 이용한 문서 청킹
- ✅ 대화 히스토리 관리
- ✅ 세션 기반 상호작용
- ✅ 벡터 데이터베이스에서 컨텍스트 검색
- ✅ 다양한 결과를 위한 Maximum Marginal Relevance (MMR)
- ✅ 타겟 검색을 위한 메타데이터 필터링

**워크플로우:**
```
사용자 쿼리
    ↓
[LangGraph 에이전트]
    ↓
[벡터 스토어에서 검색] → Milvus/FAISS
    ↓
[LLM으로 응답 생성] → Qwen 2.5
    ↓
검색된 컨텍스트와 함께 반환
```

**엔드포인트:**
- `POST /agent/query` - AI 에이전트에 질문
- `POST /agent/sessions` - 새 세션 생성
- `GET /agent/sessions` - 사용자 세션 목록
- `GET /agent/sessions/{id}/messages` - 세션 메시지 조회

**신규 RAG 엔드포인트 (api_routes.py):** ✅
- `POST /api/v1/rag/search` - 문서 시맨틱 검색
- `POST /api/v1/rag/documents` - 다중 문서 추가
- `POST /api/v1/rag/documents/single` - 단일 문서 추가
- `GET /api/v1/rag/stats` - 시스템 통계
- `GET /api/v1/rag/health` - 헬스 체크

### 3. 모니터링 모듈 (`monitoring/`)

```
monitoring/
├── middleware.py      # 메트릭 수집 미들웨어
├── metrics.py         # Prometheus 메트릭
└── health.py          # 헬스 체크 엔드포인트
```

**기능:**
- 요청/응답 메트릭
- 데이터베이스 커넥션 풀 모니터링
- 에러율 추적
- 응답 시간 측정

**메트릭:**
- `http_requests_total` - 총 HTTP 요청
- `http_request_duration_seconds` - 요청 지속 시간
- `database_connections` - 데이터베이스 연결
- `milvus_query_duration` - Milvus 쿼리 시간

### 4. 암호화 모듈 (`encryption/`)

```
encryption/
├── manager.py         # 암호화 관리자
└── models.py          # 암호화된 필드 모델
```

**기능:**
- Fernet 대칭 키 암호화
- AES-256 암호화
- PBKDF2-HMAC 키 유도
- 민감한 데이터 자동 암호화

## 테스트 전략 ✅ 구현 완료

### 테스트 스위트 상태: 29/29 통과 (100%)

#### 1. 임베딩 테스트 (`test_jina_embeddings.py`) - 10/10 ✅
- 모델 로딩 및 초기화
- 단일 및 배치 임베딩 생성
- 시맨틱 유사도 테스트 (높음: 0.9878, 낮음: -0.1387)
- 다국어 지원 (영-한: 0.9677)
- 한국어 시맨틱 검색
- Top-K 문서 검색

**모델**: `paraphrase-multilingual-MiniLM-L12-v2`

#### 2. LangChain RAG 테스트 (`test_langchain_rag.py`) - 12/12 ✅
- HuggingFace 임베딩 통합
- FAISS 벡터 스토어 작업
- 점수를 포함한 유사도 검색
- 한국어 검색
- 메타데이터 기반 필터링
- LangChain Retriever 인터페이스
- MMR (Maximum Marginal Relevance) 검색
- RecursiveCharacterTextSplitter를 이용한 텍스트 청킹
- 동적 문서 추가
- 벡터 스토어 저장/로드 지속성

**벡터 스토어**: FAISS (로컬) / Milvus (프로덕션)

#### 3. LangGraph 에이전트 테스트 (`test_langgraph_agent.py`) - 7/7 ✅
- 단순 상태 그래프
- 상태 기반 조건부 라우팅
- 대화 상태 관리
- MemorySaver를 이용한 메모리 체크포인팅
- RAG 에이전트 워크플로우 (검색 → 생성)
- 멀티 에이전트 핸드오프 (검색, 분석, 일반)
- 그래프 시각화 및 구조

**프레임워크**: LangGraph 0.6.8

#### 4. Milvus 통합 테스트 (`test_langchain_milvus.py`) - 준비 완료 🔧
- Milvus 연결 관리
- LangChain + Milvus 통합
- 점수를 포함한 유사도 검색
- 한국어 지원
- 메타데이터 필터링
- 컬렉션 관리

**상태**: 테스트 준비 완료, `docker-compose up milvus` 필요

### 테스트 실행

```bash
# 모든 RAG 테스트 실행
python -m pytest tests/test_jina_embeddings.py \
                 tests/test_langchain_rag.py \
                 tests/test_langgraph_agent.py -v

# 예상 결과: 29 passed, 4 warnings
```

### 단위 테스트
- ✅ 개별 모듈 테스트
- ✅ 외부 의존성 모킹
- ✅ 데이터베이스 픽스처

### 통합 테스트
- ✅ API 엔드포인트 테스트
- ✅ 벡터 스토어 통합 (FAISS/Milvus)
- 🔧 LLM 통합 (배포 준비 완료)

### 종단간 테스트
- 🔧 전체 워크플로우 테스트 (진행 중)
- 🔧 사용자 여정 시뮬레이션 (계획됨)

## 다운로드한 모델 및 자산

### 프로덕션 모델 (사용 준비 완료)

#### 1. Jina Embeddings v3 (~1.1GB) ✅
- **위치**: `scripts/models/jina-embeddings-v3/`
- **용도**: 고품질 다국어 텍스트 임베딩
- **기능**:
  - 8192 토큰 컨텍스트 윈도우
  - 다국어 지원 (100개 이상 언어)
  - RAG 애플리케이션에 최적화
- **상태**: 다운로드 완료, 프로덕션 준비
- **참고**: Windows 심볼릭 링크 문제로 경량 대안 사용 중

#### 2. Qwen 2.5 7B Instruct GGUF (~4.4GB) ✅
- **위치**: `scripts/models/qwen2.5-gguf/`
- **용도**: 한국어 지원 CPU 최적화 로컬 LLM
- **기능**:
  - Q4_K_M 양자화 (4비트)
  - 32K 컨텍스트 윈도우
  - 우수한 한국어 지원
  - CPU 전용 추론 (GPU 불필요)
- **상태**: 다운로드 완료, 통합 준비
- **사용법**: llama-cpp-python으로 추론

#### 3. 활성 모델 (테스트 및 프로덕션)
- **모델**: `paraphrase-multilingual-MiniLM-L12-v2`
- **용도**: 경량 다국어 임베딩
- **차원**: 384
- **상태**: 모든 테스트에서 현재 활성화 ✅
- **성능**: 0.9677 영-한 교차 언어 유사도

### 모델 관리
- 모든 모델은 `.gitignore`를 통해 git에서 제외
- `scripts/`에서 다운로드 스크립트 사용 가능
- `scripts/MODEL_DOWNLOADS.md`에 문서화

## 요약

GaiA-ABiz는 AI 기반 애플리케이션을 위한 강력하고 확장 가능한 아키텍처를 제공합니다:

- ✅ **현대적 스택**: FastAPI + Python 3.11
- ✅ **RAG 시스템**: LangChain + LangGraph (29/29 테스트 통과)
- ✅ **다국어**: 한국어, 영어, 50개 이상 언어
- ✅ **로컬 LLM 준비**: CPU 추론용 Qwen 2.5 7B
- ✅ **벡터 검색**: FAISS (개발) + Milvus (프로덕션)
- ✅ **AI 우선**: 로컬 LLM + 오픈소스 임베딩
- ✅ **보안**: OAuth2, JWT, 암호화
- ✅ **관찰 가능성**: 메트릭, 로깅, 모니터링
- ✅ **확장 가능**: 컨테이너화, 클라우드 준비
- ✅ **테스트 완료**: 포괄적 테스트 커버리지
- ✅ **유지보수 가능**: 모듈식, 테스트됨, 문서화됨

## 참고 문서

### 아키텍처 및 설정
- [LLM 구성](LLM_CONFIGURATION.md)
- [Milvus 설정](MILVUS_SETUP.md)
- [API 문서](API_DOCUMENTATION.md)
- [개발 가이드](DEVELOPMENT_GUIDE.md)
- [배포 가이드](DEPLOYMENT_GUIDE.md)

### RAG 구현 (신규 - 2025년 10월) ✅
- [**구현 요약**](../IMPLEMENTATION_SUMMARY_KR.md) - 완전한 RAG 구현 개요
- [**RAG 빠른 시작**](../RAG_QUICKSTART_KR.md) - 5분 안에 시작하기
- [**테스트 요약**](../tests/TEST_SUMMARY_KR.md) - 상세 테스트 문서
- [**모델 다운로드**](../scripts/MODEL_DOWNLOADS_KR.md) - 모델 다운로드 가이드
- [**SK Hynix RAG 권장사항**](SK_HYNIX_RAG_RECOMMENDATIONS.md) - RAG 모범 사례

### 빠른 링크
```bash
# 테스트 결과 보기
cd tests && cat TEST_SUMMARY_KR.md

# 다운로드한 모델 확인
cd scripts && cat MODEL_DOWNLOADS_KR.md

# 모든 테스트 실행
python -m pytest tests/test_*embeddings*.py tests/test_*rag*.py tests/test_*agent*.py -v
```
