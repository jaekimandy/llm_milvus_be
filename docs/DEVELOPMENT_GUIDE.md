# Development Guide

## 개발 환경 설정

### 사전 요구사항

- Python 3.11+
- Docker Desktop
- Git
- VS Code (권장) 또는 PyCharm
- PostgreSQL Client (선택)

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd gaia-abiz-backend
```

### 2. 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 편집:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/gaia_abiz
SECRET_KEY=dev-secret-key
ENCRYPTION_KEY=dev-encryption-key-must-be-32-bytes-long
OPENAI_API_KEY=sk-your-api-key
```

### 5. Docker Compose로 서비스 시작

```bash
# PostgreSQL, Milvus 등 의존 서비스만 시작
docker-compose up -d postgres milvus etcd minio
```

### 6. 데이터베이스 초기화

```bash
# 애플리케이션 실행 시 자동으로 테이블 생성됨
# 또는 Alembic 사용
alembic upgrade head
```

### 7. 애플리케이션 실행

```bash
# 개발 모드 (auto-reload)
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. API 문서 접속

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 프로젝트 구조

```
gaia-abiz-backend/
├── auth/                   # 인증/인가 모듈
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy 모델
│   ├── schemas.py         # Pydantic 스키마
│   ├── security.py        # JWT, 암호화 유틸
│   └── routes.py          # API 엔드포인트
├── monitoring/            # 모니터링 모듈
│   ├── __init__.py
│   ├── logger.py          # 로깅 설정
│   ├── metrics.py         # Prometheus 메트릭
│   ├── models.py          # 로그 모델
│   └── routes.py          # 통계 API
├── encryption/            # 암호화 모듈
│   ├── __init__.py
│   ├── crypto.py          # 암호화 서비스
│   ├── key_manager.py     # 키 관리
│   └── routes.py          # 암호화 API
├── agent/                 # AI Agent 모듈
│   ├── __init__.py
│   ├── llm_client.py      # LLM 클라이언트
│   ├── vector_store.py    # Milvus 연동
│   ├── graph_agent.py     # LangGraph 에이전트
│   ├── models.py          # 세션/메시지 모델
│   ├── schemas.py         # 요청/응답 스키마
│   └── routes.py          # Agent API
├── common/                # 공통 모듈
│   ├── __init__.py
│   └── database.py        # DB 설정
├── config/                # 설정
│   ├── __init__.py
│   └── settings.py        # 환경 변수
├── k8s/                   # Kubernetes 매니페스트
├── docs/                  # 문서
├── tests/                 # 테스트
├── main.py                # FastAPI 앱 진입점
├── requirements.txt       # Python 패키지
├── Dockerfile            # Docker 이미지
├── docker-compose.yml    # 로컬 환경
├── .env                  # 환경 변수 (git 제외)
├── .env.example          # 환경 변수 템플릿
└── README.md             # 프로젝트 소개
```

---

## 코딩 가이드

### 1. 새로운 API 엔드포인트 추가

#### Step 1: 모델 정의 (`models.py`)

```python
from sqlalchemy import Column, Integer, String, DateTime
from common.database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Step 2: 스키마 정의 (`schemas.py`)

```python
from pydantic import BaseModel
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: int

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    created_at: datetime

    class Config:
        from_attributes = True
```

#### Step 3: API 라우트 작성 (`routes.py`)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from common.database import get_db
from auth.security import get_current_active_user
from .models import Product
from .schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

#### Step 4: 라우터 등록 (`main.py`)

```python
from products.routes import router as products_router

app.include_router(products_router)
```

### 2. 데이터베이스 마이그레이션 (Alembic)

#### 초기 설정

```bash
# Alembic 초기화 (이미 완료됨)
alembic init alembic

# alembic/env.py 수정
from common.database import Base
target_metadata = Base.metadata
```

#### 마이그레이션 생성

```bash
# 자동 마이그레이션 생성
alembic revision --autogenerate -m "Add products table"

# 수동 마이그레이션 생성
alembic revision -m "Add index to products"
```

#### 마이그레이션 적용

```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade <revision>

# 롤백
alembic downgrade -1
```

### 3. AI Agent 커스터마이징

#### 새로운 Agent 타입 추가

`agent/graph_agent.py`:

```python
class CustomAgent(GraphAgent):
    def __init__(self):
        super().__init__(agent_type="custom")

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # 커스텀 노드 추가
        workflow.add_node("analyze", self.analyze_query)
        workflow.add_node("retrieve", self.retrieve_context)
        workflow.add_node("generate", self.generate_response)

        # 엣지 정의
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    async def analyze_query(self, state: AgentState) -> dict:
        # 쿼리 분석 로직
        query_type = "technical"  # 분류 로직
        return {"query_type": query_type}
```

#### Agent 등록

`agent/routes.py`:

```python
from agent.graph_agent import CustomAgent

def create_agent(agent_type: str):
    if agent_type == "custom":
        return CustomAgent()
    return GraphAgent(agent_type)
```

### 4. 테스트 작성

#### 단위 테스트

`tests/test_auth.py`:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_login():
    # 먼저 사용자 등록
    client.post("/auth/register", json={...})

    # 로그인 테스트
    response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 파일만
pytest tests/test_auth.py

# 커버리지 확인
pytest --cov=. --cov-report=html
```

---

## 디버깅

### VS Code 설정

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### 로깅 활용

```python
from monitoring.logger import get_logger

logger = get_logger(__name__)

@router.post("/test")
async def test_endpoint():
    logger.info("Test endpoint called", extra={"user_id": 123})
    logger.error("Error occurred", exc_info=True)
```

---

## 성능 최적화

### 1. 데이터베이스 쿼리 최적화

```python
# Bad: N+1 쿼리
users = db.query(User).all()
for user in users:
    print(user.profile.bio)  # 각 user마다 추가 쿼리

# Good: Eager Loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(
    joinedload(User.profile)
).all()
```

### 2. 캐싱 (향후 추가)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_data(key: str):
    # 비용이 큰 연산
    return result
```

### 3. 비동기 작업

```python
import asyncio

# 병렬 실행
results = await asyncio.gather(
    async_function_1(),
    async_function_2(),
    async_function_3()
)
```

---

## Git 워크플로우

### 브랜치 전략

```
main (production)
  └── develop (staging)
        ├── feature/auth-improvements
        ├── feature/ai-agent-enhancement
        └── bugfix/login-error
```

### 커밋 메시지 규칙

```bash
# 형식
<type>: <subject>

<body>

# 예시
feat: Add user profile endpoint

Implement GET /users/{id}/profile endpoint
with authentication required

fix: Fix JWT token expiration issue

The token was expiring too early due to
timezone conversion bug

docs: Update API documentation

Add examples for encryption endpoints
```

**타입**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `refactor`: 리팩토링
- `test`: 테스트 추가
- `chore`: 빌드/설정 변경

### Pull Request

```bash
# 1. 브랜치 생성
git checkout -b feature/new-feature

# 2. 변경사항 커밋
git add .
git commit -m "feat: Add new feature"

# 3. 푸시
git push origin feature/new-feature

# 4. PR 생성 (GitHub/GitLab)
```

---

## 코드 품질

### Linting

```bash
# Ruff (빠른 linter)
pip install ruff
ruff check .

# Black (formatter)
pip install black
black .
```

### Type Checking

```bash
pip install mypy
mypy .
```

### Pre-commit Hooks

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
```

설치:
```bash
pip install pre-commit
pre-commit install
```

---

## 환경별 설정

### 개발 환경

```python
# config/settings.py
class DevSettings(Settings):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
```

### 스테이징 환경

```python
class StagingSettings(Settings):
    DEBUG = False
    LOG_LEVEL = "INFO"
```

### 프로덕션 환경

```python
class ProdSettings(Settings):
    DEBUG = False
    LOG_LEVEL = "WARNING"
```

환경 전환:
```bash
export ENVIRONMENT=production
```

---

## 트러블슈팅

### 일반적인 문제

#### 1. Import Error

```bash
# 가상환경 활성화 확인
which python  # macOS/Linux
where python  # Windows

# 패키지 재설치
pip install -r requirements.txt --force-reinstall
```

#### 2. Database Connection Error

```bash
# PostgreSQL 실행 확인
docker-compose ps postgres

# 연결 테스트
psql -h localhost -U user -d gaia_abiz
```

#### 3. Milvus Connection Error

```bash
# Milvus 상태 확인
docker-compose logs milvus

# 재시작
docker-compose restart milvus etcd minio
```

---

## 유용한 명령어

### Docker

```bash
# 로그 실시간 확인
docker-compose logs -f api

# 컨테이너 접속
docker-compose exec api bash

# 데이터베이스 초기화
docker-compose down -v && docker-compose up -d
```

### Database

```bash
# PostgreSQL 접속
docker-compose exec postgres psql -U user -d gaia_abiz

# 테이블 목록
\dt

# 쿼리 실행
SELECT * FROM users;
```

### Python

```bash
# 대화형 셸
python
>>> from common.database import SessionLocal
>>> db = SessionLocal()
>>> from auth.models import User
>>> users = db.query(User).all()
```

---

## 리소스

### 공식 문서

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [LangChain](https://python.langchain.com/)
- [Milvus](https://milvus.io/docs)

### 내부 문서

- [프로젝트 개요](./PROJECT_OVERVIEW.md)
- [API 문서](./API_DOCUMENTATION.md)
- [배포 가이드](./DEPLOYMENT_GUIDE.md)

### 팀 연락처

- **QA**: qa@example.com
- **DBA**: dba@example.com
- **AA**: architect@example.com
