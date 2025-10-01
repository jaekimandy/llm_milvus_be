# Documentation Index

GaiA-ABiz Backend 프로젝트 문서 모음

## 📚 문서 목록

### 1. [Quick Start Guide](./QUICK_START.md)
**5분 만에 시작하기**

- Docker Compose로 빠른 실행
- 첫 API 요청 보내기
- 샘플 데이터 테스트

**대상**: 처음 프로젝트를 접하는 모든 분

---

### 2. [Architecture Overview](./ARCHITECTURE.md) ⭐ NEW
**시스템 아키텍처 상세**

- 전체 시스템 구조
- 모듈별 설계 및 데이터 플로우
- 기술 스택 상세
- 보안 아키텍처
- 확장성 및 배포 전략

**대상**: 아키텍처 이해가 필요한 개발자

---

### 3. [Project Overview](./PROJECT_OVERVIEW.md)
**프로젝트 전체 개요**

- 시스템 아키텍처
- 팀 구성 및 담당 영역
- 주요 기능 설명
- 데이터베이스 스키마
- 기술 스택

**대상**: 프로젝트 이해가 필요한 모든 팀원

---

### 4. [LLM Configuration](./LLM_CONFIGURATION.md) ⭐ NEW
**LLM & 임베딩 설정 가이드**

- Claude AI 설정 (Anthropic)
- Voyage AI 임베딩 설정
- OpenAI 대안 설정
- 비용 비교 및 최적화
- 문제 해결

**대상**: AI Agent 개발자, 시스템 관리자

---

### 5. [Milvus Vector Database Setup](./MILVUS_SETUP.md) ⭐ NEW
**Milvus 벡터 DB 설정 및 운영**

- Milvus 초기 설정
- 컬렉션 생성 및 관리
- 임베딩 저장 및 검색
- 성능 튜닝
- 백업 및 복구
- 문제 해결

**대상**: AI Agent 개발자, DBA

---

### 6. [API Documentation](./API_DOCUMENTATION.md)
**API 상세 문서**

- 모든 엔드포인트 설명
- 요청/응답 예시
- 에러 코드
- 인증 방법

**대상**: API를 사용하는 개발자, QA 엔지니어

---

### 7. [Development Guide](./DEVELOPMENT_GUIDE.md)
**개발 가이드**

- 개발 환경 설정
- 코딩 컨벤션
- 새 기능 추가 방법
- 테스트 작성
- 디버깅 팁

**대상**: 백엔드 개발자 (공통 3명 + AI Agent 9명)

---

### 8. [Deployment Guide](./DEPLOYMENT_GUIDE.md)
**배포 가이드**

- Docker Compose 배포
- Kubernetes 배포
- CI/CD 파이프라인
- 모니터링 설정
- 트러블슈팅

**대상**: DevOps, AA, DBA

---

## 🎯 역할별 추천 문서

### PMO Team

#### QA (Quality Assurance)
1. ✅ [Quick Start](./QUICK_START.md) - 환경 구축
2. ✅ [API Documentation](./API_DOCUMENTATION.md) - API 테스트
3. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md) - 테스트 작성 섹션

#### DBA (Database Administrator)
1. ✅ [Project Overview](./PROJECT_OVERVIEW.md) - DB 스키마
2. ✅ [Deployment Guide](./DEPLOYMENT_GUIDE.md) - DB 백업/복구
3. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md) - 마이그레이션

#### AA (Application Architect)
1. ✅ [Project Overview](./PROJECT_OVERVIEW.md) - 아키텍처
2. ✅ [Deployment Guide](./DEPLOYMENT_GUIDE.md) - 인프라
3. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md) - 구조 설계

---

### BE 개발 (공통) - 3명

#### 인증/인가 개발자
1. ✅ [Quick Start](./QUICK_START.md)
2. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md)
3. 📂 `auth/` 모듈 소스 코드
4. ✅ [API Documentation](./API_DOCUMENTATION.md) - Authentication 섹션

**핵심 파일**:
- `auth/models.py` - User, RefreshToken 모델
- `auth/security.py` - JWT, OAuth2 로직
- `auth/routes.py` - 인증 API

#### 모니터링/로그 개발자
1. ✅ [Quick Start](./QUICK_START.md)
2. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md)
3. 📂 `monitoring/` 모듈 소스 코드
4. ✅ [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Prometheus/Grafana 섹션

**핵심 파일**:
- `monitoring/metrics.py` - Prometheus 메트릭
- `monitoring/logger.py` - 구조화된 로깅
- `monitoring/routes.py` - 통계 API

#### 암호화 개발자
1. ✅ [Quick Start](./QUICK_START.md)
2. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md)
3. 📂 `encryption/` 모듈 소스 코드
4. ✅ [API Documentation](./API_DOCUMENTATION.md) - Encryption 섹션

**핵심 파일**:
- `encryption/crypto.py` - 암호화 서비스
- `encryption/key_manager.py` - 키 관리
- `encryption/routes.py` - 암호화 API

---

### BE 개발 - 9명 (AI Agent)

1. ✅ [Quick Start](./QUICK_START.md)
2. ✅ [Development Guide](./DEVELOPMENT_GUIDE.md) - AI Agent 커스터마이징
3. 📂 `agent/` 모듈 소스 코드
4. ✅ [API Documentation](./API_DOCUMENTATION.md) - AI Agent 섹션

**핵심 파일**:
- `agent/graph_agent.py` - LangGraph 워크플로우
- `agent/llm_client.py` - OpenAI 연동
- `agent/vector_store.py` - Milvus 벡터 DB
- `agent/routes.py` - Agent API

**외부 문서**:
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)
- [Milvus Documentation](https://milvus.io/docs)

---

## 🔧 기술 스택별 학습 자료

### FastAPI
- **공식 문서**: https://fastapi.tiangolo.com/
- **튜토리얼**: https://fastapi.tiangolo.com/tutorial/
- **예제**: `auth/routes.py`, `agent/routes.py`

### SQLAlchemy
- **공식 문서**: https://docs.sqlalchemy.org/
- **ORM Tutorial**: https://docs.sqlalchemy.org/en/20/orm/tutorial.html
- **예제**: `auth/models.py`, `common/database.py`

### LangChain & LangGraph
- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **예제**: `agent/graph_agent.py`

### Milvus
- **공식 문서**: https://milvus.io/docs
- **Python SDK**: https://milvus.io/api-reference/pymilvus/v2.3.x/About.md
- **예제**: `agent/vector_store.py`

### Prometheus
- **공식 문서**: https://prometheus.io/docs/
- **Python Client**: https://github.com/prometheus/client_python
- **예제**: `monitoring/metrics.py`

### Kubernetes
- **공식 문서**: https://kubernetes.io/docs/
- **Tutorials**: https://kubernetes.io/docs/tutorials/
- **예제**: `k8s/` 디렉토리

---

## 📋 체크리스트

### 첫 날 (신규 개발자)
- [ ] [Quick Start](./QUICK_START.md) 따라하기
- [ ] 로컬 환경 구축 완료
- [ ] API 문서 둘러보기
- [ ] 샘플 요청 테스트

### 첫 주
- [ ] [Project Overview](./PROJECT_OVERVIEW.md) 읽기
- [ ] [Development Guide](./DEVELOPMENT_GUIDE.md) 숙지
- [ ] 담당 모듈 소스 코드 리뷰
- [ ] 테스트 코드 작성 연습

### 첫 달
- [ ] 첫 기능 개발 완료
- [ ] PR 생성 및 리뷰 받기
- [ ] [Deployment Guide](./DEPLOYMENT_GUIDE.md) 이해
- [ ] 모니터링 대시보드 확인

---

## 🔍 FAQ

### Q1. OpenAI API 키가 없으면 어떻게 하나요?
**A**: `.env` 파일의 `OPENAI_API_KEY`를 임시 값으로 설정하고, AI Agent 관련 기능만 제외하고 나머지는 정상 동작합니다.

### Q2. Docker 없이 실행할 수 있나요?
**A**: 가능합니다. [Development Guide](./DEVELOPMENT_GUIDE.md)의 "개발 환경 설정" 섹션 참고.

### Q3. 데이터베이스 스키마를 변경하려면?
**A**: [Development Guide](./DEVELOPMENT_GUIDE.md)의 "데이터베이스 마이그레이션" 섹션에서 Alembic 사용법 확인.

### Q4. 새로운 모듈을 추가하려면?
**A**: [Development Guide](./DEVELOPMENT_GUIDE.md)의 "새로운 API 엔드포인트 추가" 섹션 참고.

### Q5. 프로덕션 배포는 어떻게 하나요?
**A**: [Deployment Guide](./DEPLOYMENT_GUIDE.md)의 "프로덕션 배포 (Kubernetes)" 섹션 참고.

---

## 📞 지원

### 문서 피드백
문서 개선 제안이나 오류 발견 시:
- GitHub Issue 생성
- 팀 채널에 메시지
- 직접 PR 제출

### 기술 지원
- **일반 문의**: 팀 채널
- **긴급 이슈**: AA/DBA 직접 연락
- **보안 이슈**: 보안 담당자 즉시 연락

---

## 📝 문서 업데이트

**마지막 업데이트**: 2025-10-01

**버전**: 1.0.0

**작성자**: Backend Development Team

**변경 이력**:
- 2025-10-01: 초기 문서 작성
