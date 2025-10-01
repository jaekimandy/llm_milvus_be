# Quick Start Guide

## 빠른 시작 (5분)

### 1. Docker Compose로 실행

```bash
# 프로젝트 디렉토리로 이동
cd gaia-abiz-backend

# 모든 서비스 시작
docker-compose up -d

# 로그 확인 (API 시작 대기)
docker-compose logs -f api
```

### 2. API 문서 열기

브라우저에서 접속:
```
http://localhost:8000/docs
```

### 3. 첫 API 요청

#### 사용자 등록

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "username": "demo",
    "password": "demo123",
    "full_name": "Demo User"
  }'
```

#### 로그인

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "demo123"
  }'
```

**응답 예시**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

토큰을 복사해두세요!

#### AI Agent에 질문하기

```bash
# 위에서 받은 access_token을 사용
export TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/agent/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is FastAPI?",
    "agent_type": "general"
  }'
```

---

## 주요 엔드포인트

### 인증
- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `GET /auth/me` - 내 정보

### AI Agent
- `POST /agent/query` - AI에게 질문
- `POST /agent/sessions` - 세션 생성
- `GET /agent/sessions` - 세션 목록

### 암호화
- `POST /encryption/encrypt` - 텍스트 암호화
- `POST /encryption/decrypt` - 텍스트 복호화

### 모니터링
- `GET /monitoring/metrics` - Prometheus 메트릭
- `GET /monitoring/health` - 헬스 체크

---

## 개발 환경 설정 (선택사항)

로컬에서 Python으로 직접 실행하려면:

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 의존 서비스만 시작 (DB, Milvus)
docker-compose up -d postgres milvus etcd minio

# 4. 애플리케이션 실행
python main.py
```

---

## 중지 및 정리

```bash
# 서비스 중지 (데이터 유지)
docker-compose stop

# 서비스 제거 (데이터 포함)
docker-compose down -v
```

---

## 다음 단계

- [프로젝트 개요](./PROJECT_OVERVIEW.md) - 전체 구조 이해
- [API 문서](./API_DOCUMENTATION.md) - 모든 API 상세 설명
- [개발 가이드](./DEVELOPMENT_GUIDE.md) - 개발 방법
- [배포 가이드](./DEPLOYMENT_GUIDE.md) - 프로덕션 배포

---

## 문제 해결

### API가 시작되지 않을 때

```bash
# 로그 확인
docker-compose logs api

# 재시작
docker-compose restart api
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 상태 확인
docker-compose ps postgres

# 전체 재시작
docker-compose down && docker-compose up -d
```

### 포트 충돌

`.env` 파일에서 포트 변경:
```bash
PORT=8001
```

---

## 테스트 데이터

### 샘플 사용자

- Username: `demo`
- Password: `demo123`
- Email: `demo@example.com`

### 샘플 쿼리

```json
{
  "query": "Explain microservices architecture",
  "agent_type": "general"
}
```

```json
{
  "query": "What are the benefits of Docker?",
  "agent_type": "technical"
}
```

---

## 유용한 링크

- **API 문서**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **메트릭**: http://localhost:8000/monitoring/metrics
- **헬스 체크**: http://localhost:8000/health
