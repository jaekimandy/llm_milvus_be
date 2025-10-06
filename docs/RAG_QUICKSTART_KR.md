# RAG 시스템 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1. 의존성 설치
```bash
cd gaia-abiz-backend
pip install -r requirements.txt
```

### 2. 테스트 실행
```bash
# 모든 RAG 테스트 실행 (29개 테스트)
python -m pytest tests/test_semiconductor_embeddings.py tests/test_langchain_rag.py tests/test_langgraph_agent.py -v

# 예상 결과: 29 passed ✅
```

### 3. 빠른 예제 - 시맨틱 검색

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# 1. 임베딩 초기화
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# 2. 문서 생성
docs = [
    Document(page_content="SK Hynix는 메모리 반도체를 생산합니다."),
    Document(page_content="GaiA는 AI 플랫폼입니다."),
    Document(page_content="Python은 프로그래밍 언어입니다.")
]

# 3. 벡터 스토어 생성
vectorstore = FAISS.from_documents(docs, embeddings)

# 4. 검색!
results = vectorstore.similarity_search("SK Hynix에 대해 알려주세요", k=2)

for doc in results:
    print(doc.page_content)
```

### 4. 빠른 예제 - LangGraph 에이전트

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

# 상태 정의
class State(TypedDict):
    query: str
    response: str

# 노드 정의
def process(state: State) -> State:
    return {"response": f"처리됨: {state['query']}"}

# 그래프 구축
workflow = StateGraph(State)
workflow.add_node("process", process)
workflow.set_entry_point("process")
workflow.add_edge("process", END)

# 실행
app = workflow.compile()
result = app.invoke({"query": "안녕하세요", "response": ""})
print(result["response"])  # "처리됨: 안녕하세요"
```

---

## 📖 전체 문서

- **구현 요약**: [IMPLEMENTATION_SUMMARY_KR.md](IMPLEMENTATION_SUMMARY_KR.md)
- **테스트 문서**: [tests/TEST_SUMMARY_KR.md](tests/TEST_SUMMARY_KR.md)
- **모델 다운로드**: [scripts/MODEL_DOWNLOADS_KR.md](scripts/MODEL_DOWNLOADS_KR.md)

---

## 🏗️ 아키텍처 개요

```
사용자 쿼리
    ↓
[FastAPI 엔드포인트]
    ↓
[RAG 서비스]
    ├── 임베딩 (HuggingFace)
    ├── 벡터 스토어 (FAISS/Milvus)
    └── LLM (Qwen 2.5)
    ↓
[LangGraph 에이전트]
    ├── 검색 노드
    ├── 처리 노드
    └── 생성 노드
    ↓
응답
```

---

## 🔥 주요 기능

✅ **다국어** - 한국어, 영어, 50개 이상 언어
✅ **시맨틱 검색** - 의미로 관련 문서 찾기
✅ **상태 기반 에이전트** - 메모리 및 대화 추적
✅ **프로덕션 준비** - Milvus, FastAPI, Docker
✅ **테스트 완료** - 29/29 테스트 통과

---

## 📞 도움이 필요하신가요?

- [IMPLEMENTATION_SUMMARY_KR.md](IMPLEMENTATION_SUMMARY_KR.md)에서 자세한 정보 확인
- 작동 예제는 [tests/](tests/) 참조
- 서비스는 [docker-compose.yml](docker-compose.yml) 검토

---

**상태**: ✅ 프로덕션 준비 | **테스트**: 29/29 통과 | **날짜**: 2025년 10월
