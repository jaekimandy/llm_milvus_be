# 개발 가이드

**GaiA-ABiz 백엔드 개발자를 위한 종합 가이드**

---

## 목차

1. [개발 환경 설정](#개발-환경-설정)
2. [프로젝트 구조](#프로젝트-구조)
3. [코딩 표준](#코딩-표준)
4. [테스트 작성](#테스트-작성)
5. [API 개발](#api-개발)
6. [RAG 시스템 확장](#rag-시스템-확장)
7. [디버깅](#디버깅)
8. [성능 최적화](#성능-최적화)
9. [기여 가이드](#기여-가이드)

---

## 개발 환경 설정

### 필수 도구

- **Python 3.10+**: 최신 언어 기능 활용
- **Git**: 버전 관리
- **Docker & Docker Compose**: 서비스 오케스트레이션
- **IDE**: VSCode 또는 PyCharm 권장
- **최소 사양**: 16GB RAM, 4코어 CPU

### 초기 설정

```bash
# 1. 저장소 클론
cd gaia-abiz-backend

# 2. 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 개발 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구

# 4. Pre-commit 훅 설치
pre-commit install

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### IDE 설정

#### VSCode

`.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. 가상 환경 선택 (`venv/`)
3. Tools → Black → Enable on save
4. Run → Edit Configurations → Add pytest configuration

---

## 프로젝트 구조

```
gaia-abiz-backend/
├── agent/                    # 핵심 AI/RAG 로직
│   ├── llm_client.py        # LLM 클라이언트 (Qwen 2.5)
│   ├── vector_store.py      # 벡터 저장소 (Milvus/FAISS)
│   ├── rag_service.py       # RAG 서비스
│   └── api_routes.py        # FastAPI 라우터
├── config/                   # 설정 관리
│   ├── settings.py          # Pydantic 설정
│   └── logging_config.py    # 로깅 설정
├── core/                     # 핵심 비즈니스 로직
│   ├── models.py            # 데이터 모델
│   └── database.py          # DB 연결
├── tests/                    # 테스트 스위트
│   ├── test_semiconductor_embeddings.py  # 임베딩 테스트 (10개)
│   ├── test_langchain_rag.py       # RAG 테스트 (12개)
│   ├── test_langgraph_agent.py     # 에이전트 테스트 (7개)
│   └── test_langchain_milvus.py    # Milvus 테스트
├── scripts/                  # 유틸리티 스크립트
│   ├── download_mpnet_embeddings.py
│   ├── download_qwen2.5.py
│   ├── init_milvus.py
│   └── models/              # 다운로드된 모델
├── docs/                     # 문서
├── main.py                   # FastAPI 앱 엔트리포인트
├── requirements.txt          # 프로덕션 의존성
├── docker-compose.yml        # 개발 환경
└── .env                      # 환경 변수
```

### 모듈별 책임

| 모듈 | 책임 |
|------|------|
| `agent/` | RAG, LLM, 벡터 저장소 통합 |
| `config/` | 환경 변수, 설정 관리 |
| `core/` | 데이터베이스, 비즈니스 로직 |
| `tests/` | 유닛/통합 테스트 |
| `scripts/` | 일회성 작업, 모델 다운로드 |

---

## 코딩 표준

### Python 스타일 가이드

- **PEP 8** 준수
- **Black** 포매터 사용 (line length: 100)
- **isort**로 import 정리
- **Type hints** 필수

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DocumentRequest(BaseModel):
    """문서 추가 요청 모델"""
    documents: List[str]
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "documents": ["문서 내용1", "문서 내용2"],
                "metadata": {"source": "manual"}
            }
        }

async def add_documents(request: DocumentRequest) -> Dict[str, Any]:
    """
    문서를 벡터 저장소에 추가합니다.

    Args:
        request: 문서 추가 요청

    Returns:
        추가된 문서 수와 메시지

    Raises:
        ValueError: 문서가 비어있는 경우
    """
    if not request.documents:
        raise ValueError("문서 리스트가 비어있습니다")

    # 구현...
    return {"count": len(request.documents), "message": "성공"}
```

### 네이밍 규칙

- **변수/함수**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

```python
# Good
MAX_RETRIES = 3
embedding_model = SentenceTransformer("model-name")

class RAGService:
    def __init__(self):
        self._vectorstore = None

    def semantic_search(self, query: str) -> List[Document]:
        pass
```

### Docstring 형식

Google Style Docstrings 사용:

```python
def similarity_search(
    query: str,
    k: int = 3,
    filter_dict: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    의미적 유사도 기반 문서 검색을 수행합니다.

    Args:
        query: 검색 쿼리 문자열
        k: 반환할 최대 결과 수 (기본값: 3)
        filter_dict: 메타데이터 필터 딕셔너리 (선택사항)

    Returns:
        검색 결과 리스트. 각 항목은 다음을 포함:
            - content: 문서 내용
            - metadata: 문서 메타데이터
            - score: 유사도 점수

    Raises:
        ValueError: 벡터 저장소가 초기화되지 않은 경우

    Example:
        >>> results = rag_service.similarity_search("RAG란?", k=5)
        >>> print(results[0]["content"])
        "RAG는 검색 증강 생성입니다..."
    """
    pass
```

---

## 테스트 작성

### 테스트 구조

```
tests/
├── conftest.py              # 공유 fixtures
├── test_semiconductor_embeddings.py  # 임베딩 유닛 테스트
├── test_langchain_rag.py    # RAG 통합 테스트
├── test_langgraph_agent.py  # 에이전트 테스트
└── test_api_routes.py       # API 엔드투엔드 테스트
```

### Pytest Fixtures

`conftest.py`:

```python
import pytest
from sentence_transformers import SentenceTransformer
from agent.rag_service import RAGService

@pytest.fixture(scope="session")
def embedding_model():
    """세션 전체에서 공유되는 임베딩 모델"""
    return SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

@pytest.fixture(scope="function")
def rag_service(embedding_model):
    """각 테스트마다 새로운 RAG 서비스"""
    service = RAGService(embedding_model)
    yield service
    # Teardown
    if service.vectorstore:
        service.vectorstore = None
```

### 테스트 작성 예제

```python
import pytest
from fastapi.testclient import TestClient
from main import app

class TestRAGEndpoints:
    """RAG API 엔드포인트 테스트"""

    @pytest.fixture(scope="class")
    def client(self):
        return TestClient(app)

    def test_add_documents(self, client):
        """문서 추가 API 테스트"""
        response = client.post(
            "/api/v1/rag/documents",
            json={
                "documents": [
                    "SK Hynix는 메모리 반도체를 생산합니다.",
                    "GaiA는 AI 플랫폼입니다."
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert "성공" in data["message"]

    def test_semantic_search(self, client):
        """의미적 검색 API 테스트"""
        # 먼저 문서 추가
        client.post(
            "/api/v1/rag/documents",
            json={"documents": ["테스트 문서 내용"]}
        )

        # 검색 수행
        response = client.post(
            "/api/v1/rag/search",
            json={"query": "테스트", "k": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) > 0
        assert "content" in data["results"][0]
```

### 테스트 실행

```bash
# 전체 테스트 실행
pytest tests/ -v

# 특정 파일 테스트
pytest tests/test_langchain_rag.py -v

# 커버리지와 함께 실행
pytest tests/ --cov=agent --cov-report=html

# 마커로 필터링
pytest tests/ -m "not slow" -v

# 병렬 실행
pytest tests/ -n auto
```

---

## API 개발

### 새 엔드포인트 추가

1. **agent/api_routes.py**에 라우터 함수 추가:

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class SummarizeRequest(BaseModel):
    documents: List[str]
    max_length: int = 500

@router.post("/summarize")
async def summarize_documents(request: SummarizeRequest):
    """
    여러 문서를 요약합니다.

    - **documents**: 요약할 문서 리스트
    - **max_length**: 최대 요약 길이
    """
    try:
        # 요약 로직 구현
        summary = "요약된 내용..."
        return {
            "summary": summary,
            "original_count": len(request.documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **테스트 작성**:

```python
def test_summarize_documents(client):
    response = client.post(
        "/api/v1/rag/summarize",
        json={
            "documents": ["문서1", "문서2"],
            "max_length": 300
        }
    )
    assert response.status_code == 200
    assert "summary" in response.json()
```

3. **문서화**: FastAPI가 자동으로 생성 (http://localhost:8000/docs)

### 에러 처리

```python
from fastapi import HTTPException, status

@router.post("/search")
async def search(query: str):
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="쿼리가 비어있습니다"
        )

    try:
        results = rag_service.search(query)
        return {"results": results}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="검색 중 오류 발생"
        )
```

---

## RAG 시스템 확장

### 새 임베딩 모델 추가

`agent/llm_client.py`:

```python
from sentence_transformers import SentenceTransformer
from config.settings import settings

class EmbeddingProvider:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        if settings.EMBEDDINGS_PROVIDER == "mpnet":
            return SentenceTransformer(
                "sentence-transformers/all-mpnet-base-v2"
            )
        elif settings.EMBEDDINGS_PROVIDER == "local":
            return SentenceTransformer(
                "sentence-transformers/all-mpnet-base-v2"
            )
        else:
            raise ValueError(f"Unknown provider: {settings.EMBEDDINGS_PROVIDER}")

    async def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

### 커스텀 Retriever 구현

```python
from langchain.schema import BaseRetriever, Document
from typing import List

class HybridRetriever(BaseRetriever):
    """키워드 + 의미적 검색을 결합한 하이브리드 검색기"""

    def __init__(self, vectorstore, keyword_index):
        self.vectorstore = vectorstore
        self.keyword_index = keyword_index

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # 1. 벡터 검색
        vector_results = self.vectorstore.similarity_search(query, k=5)

        # 2. 키워드 검색 (BM25)
        keyword_results = self.keyword_index.search(query, k=5)

        # 3. 결과 병합 및 재순위화
        combined = self._rerank(vector_results, keyword_results)
        return combined[:3]

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)
```

---

## 디버깅

### 로깅 설정

`config/logging_config.py`:

```python
import logging
from config.settings import settings

def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log")
        ]
    )

# 사용
logger = logging.getLogger(__name__)
logger.info("RAG 검색 시작: %s", query)
logger.error("임베딩 생성 실패", exc_info=True)
```

### 디버깅 팁

```python
# 1. 임베딩 디버깅
embeddings = await llm_client.generate_embeddings("테스트")
print(f"임베딩 차원: {len(embeddings)}")
print(f"첫 5개 값: {embeddings[:5]}")

# 2. 벡터 저장소 상태 확인
print(f"문서 수: {vectorstore._collection.num_entities}")
print(f"인덱스 타입: {vectorstore._index_params}")

# 3. API 요청/응답 로깅
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
    return response
```

---

## 성능 최적화

### 벡터 저장소 최적화

```python
# Milvus 인덱스 최적화
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}

# 배치 임베딩 생성
async def batch_embed(texts: List[str], batch_size: int = 32):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_emb = embedding_model.encode(batch)
        embeddings.extend(batch_emb)
    return embeddings
```

### 캐싱 전략

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_search(query_hash: str, k: int):
    # 쿼리 해시 기반 캐싱
    return vector_store.similarity_search(query_hash, k=k)

def search_with_cache(query: str, k: int = 3):
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return cached_search(query_hash, k)
```

---

## 기여 가이드

### Git 워크플로우

```bash
# 1. 새 기능 브랜치 생성
git checkout -b feature/new-rag-feature

# 2. 변경 사항 커밋
git add .
git commit -m "feat: RAG 하이브리드 검색 추가"

# 3. 테스트 실행
pytest tests/ -v

# 4. 푸시 및 PR 생성
git push origin feature/new-rag-feature
```

### 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅 (기능 변경 없음)
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스, 의존성 업데이트
```

### PR 체크리스트

- [ ] 모든 테스트 통과
- [ ] 새 기능에 대한 테스트 추가
- [ ] 문서 업데이트
- [ ] 코드 리뷰 요청
- [ ] 커밋 메시지 규칙 준수

---

## 유용한 명령어

```bash
# 코드 포맷팅
black . --line-length 100
isort .

# 린팅
flake8 . --max-line-length=100
pylint agent/

# 타입 체크
mypy agent/ --ignore-missing-imports

# 보안 스캔
bandit -r agent/

# 의존성 업데이트
pip list --outdated
pip install -U package_name
```

---

**업데이트**: 2025년 10월 5일
**테스트 상태**: ✅ 29/29 통과
**문서 상태**: 완료
