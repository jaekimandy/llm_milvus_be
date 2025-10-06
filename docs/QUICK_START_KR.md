# 빠른 시작 가이드

**GaiA-ABiz 백엔드를 5분 안에 시작하세요**

---

## 전제 조건

- Python 3.10 이상
- Docker & Docker Compose (선택사항)
- 8GB 이상 RAM
- 10GB 이상 저장공간

---

## 1단계: 저장소 클론

```bash
cd gaia-abiz-backend
```

---

## 2단계: 가상 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 활성화 (Linux/Mac)
source venv/bin/activate
```

---

## 3단계: 의존성 설치

```bash
# 모든 의존성 설치
pip install -r requirements.txt
```

**주요 패키지:**
- FastAPI 0.118.0
- LangChain 0.3.27
- LangGraph 0.6.8
- Sentence Transformers 3.1.1
- FAISS-CPU 1.12.0
- Pytest 8.4.2

---

## 4단계: 환경 변수 설정

`.env` 파일 생성:

```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/gaia_abiz

# JWT 시크릿 (랜덤 문자열)
SECRET_KEY=your-super-secret-key-change-this

# 암호화 키
ENCRYPTION_KEY=your-encryption-key-change-this

# LLM 설정 (로컬)
LLM_PROVIDER=local
LLM_MODEL_PATH=scripts/models/qwen2.5-gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf
LLM_THREADS=8

# 임베딩 설정 (로컬)
EMBEDDINGS_PROVIDER=local
EMBEDDINGS_MODEL=sentence-transformers/all-mpnet-base-v2

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=documents
```

---

## 5단계: 테스트 실행

```bash
# RAG 시스템 테스트 (29개 테스트)
python -m pytest tests/test_semiconductor_embeddings.py \
                 tests/test_langchain_rag.py \
                 tests/test_langgraph_agent.py -v

# 예상 결과: 29 passed ✅
```

---

## 6단계: Docker 서비스 시작 (선택사항)

```bash
# PostgreSQL, Milvus, etcd, MinIO 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# Milvus 초기화
python scripts/init_milvus.py
```

---

## 7단계: 개발 서버 시작

```bash
# FastAPI 서버 시작
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면:
- **API 문서**: http://localhost:8000/docs
- **대체 문서**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

---

## 빠른 테스트

### 1. 헬스 체크

```bash
curl http://localhost:8000/health
```

### 2. RAG 엔드포인트 테스트

```python
import requests

# 문서 추가
response = requests.post(
    "http://localhost:8000/api/v1/rag/documents",
    json={
        "documents": [
            "SK Hynix는 메모리 반도체를 생산합니다.",
            "GaiA는 AI 플랫폼입니다."
        ]
    }
)
print(response.json())

# 검색
response = requests.post(
    "http://localhost:8000/api/v1/rag/search",
    json={
        "query": "SK Hynix에 대해 알려주세요",
        "k": 2
    }
)
print(response.json())
```

---

## 일반적인 명령어

### 개발

```bash
# 개발 서버 시작
uvicorn main:app --reload

# 테스트 실행
pytest tests/ -v

# 코드 포맷팅
black .

# 린팅
flake8 .
```

### Docker

```bash
# 서비스 시작
docker-compose up -d

# 로그 보기
docker-compose logs -f api

# 서비스 중지
docker-compose down

# 데이터 포함 완전 제거
docker-compose down -v
```

### 데이터베이스

```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

---

## 다음 단계

1. **문서 읽기**: [ARCHITECTURE_KR.md](ARCHITECTURE_KR.md)에서 시스템 아키텍처 이해
2. **RAG 탐색**: [RAG_QUICKSTART_KR.md](RAG_QUICKSTART_KR.md)에서 RAG 기능 학습
3. **API 테스트**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)에서 모든 엔드포인트 확인
4. **개발**: [DEVELOPMENT_GUIDE_KR.md](DEVELOPMENT_GUIDE_KR.md)에서 개발 가이드 읽기
5. **배포**: [DEPLOYMENT_GUIDE_KR.md](DEPLOYMENT_GUIDE_KR.md)에서 프로덕션 배포 계획

---

## 문제 해결

### "모듈을 찾을 수 없음" 오류

```bash
# 가상 환경 활성화 확인
which python  # Linux/Mac
where python  # Windows

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL이 실행 중인지 확인
docker-compose ps

# 데이터베이스 재시작
docker-compose restart postgres
```

### Milvus 연결 오류

```bash
# Milvus 서비스 확인
docker-compose ps milvus

# Milvus 로그 확인
docker-compose logs milvus

# Milvus 재시작
docker-compose restart milvus etcd minio
```

---

## 도움말

- **전체 문서**: [docs/](.)
- **테스트 예제**: [../tests/](../tests/)
- **API 엔드포인트**: http://localhost:8000/docs
- **문제 보고**: GitHub Issues

---

**시작 시간**: ~5분
**테스트 상태**: ✅ 29/29 통과
**문서**: 한국어 완료
