"""
Streamlit UI for GaiA-ABiz RAG System
Simple interface to test semantic search and document management
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.rag_service import RAGService
from langchain_community.embeddings import HuggingFaceEmbeddings

# Page configuration
st.set_page_config(
    page_title="GaiA-ABiz RAG 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Korean fonts
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .result-box {
        background-color: #ffffff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize RAG service
@st.cache_resource
def load_rag_service():
    """Load RAG service (cached)"""
    with st.spinner("임베딩 모델 로딩 중... (최초 1회만 소요됩니다)"):
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        service = RAGService(embeddings=embeddings)
        return service

# Header
st.markdown('<div class="main-header">🤖 GaiA-ABiz RAG 시스템</div>', unsafe_allow_html=True)
st.markdown("**로컬 LLM 기반 의미적 검색 시스템** | Qwen 2.5 + Jina Embeddings")

# Sidebar
with st.sidebar:
    st.header("⚙️ 설정")

    # Mode selection
    mode = st.radio(
        "모드 선택",
        ["🔍 검색", "📄 문서 추가", "📊 통계"],
        index=0
    )

    st.divider()

    # Search settings
    if mode == "🔍 검색":
        st.subheader("검색 설정")
        k_results = st.slider("검색 결과 수 (k)", 1, 10, 3)
        show_scores = st.checkbox("유사도 점수 표시", value=True)

    st.divider()

    # Info
    st.info("""
    **사용 방법:**
    1. 문서 추가 탭에서 문서를 입력
    2. 검색 탭에서 질문 입력
    3. 의미적으로 유사한 문서 확인
    """)

    st.caption("💡 한국어와 영어 모두 지원합니다")

# Load RAG service
rag_service = load_rag_service()

# Main content area
if mode == "🔍 검색":
    st.header("🔍 의미적 검색")

    # Query input
    query = st.text_input(
        "질문을 입력하세요:",
        placeholder="예: SK Hynix에 대해 알려주세요",
        help="질문과 의미적으로 유사한 문서를 검색합니다"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 검색", type="primary", use_container_width=True)

    if search_button and query:
        with st.spinner("검색 중..."):
            try:
                results = rag_service.semantic_search(query, k=k_results)

                if results:
                    st.success(f"✅ {len(results)}개의 결과를 찾았습니다")

                    for i, result in enumerate(results, 1):
                        score = result.get('score', 0)
                        content = result.get('content', '')
                        metadata = result.get('metadata', {})

                        # Result card
                        with st.container():
                            st.markdown(f'<div class="result-box">', unsafe_allow_html=True)

                            # Header with rank and score
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.markdown(f"**📄 결과 #{i}**")
                            with col_b:
                                if show_scores:
                                    score_color = "green" if score > 0.8 else "orange" if score > 0.6 else "red"
                                    st.markdown(f"<span style='color:{score_color}'>⭐ {score:.4f}</span>", unsafe_allow_html=True)

                            # Content
                            st.markdown(content)

                            # Metadata
                            if metadata:
                                with st.expander("📋 메타데이터"):
                                    for key, value in metadata.items():
                                        st.text(f"{key}: {value}")

                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ 검색 결과가 없습니다. 먼저 문서를 추가해주세요.")

            except Exception as e:
                st.error(f"❌ 검색 중 오류 발생: {str(e)}")

    elif search_button and not query:
        st.warning("⚠️ 검색어를 입력해주세요")

elif mode == "📄 문서 추가":
    st.header("📄 문서 추가")

    tab1, tab2 = st.tabs(["단일 문서", "다중 문서"])

    with tab1:
        st.subheader("단일 문서 추가")

        single_doc = st.text_area(
            "문서 내용:",
            height=200,
            placeholder="예: SK Hynix는 메모리 반도체를 생산하는 글로벌 기업입니다.",
            help="추가할 문서의 내용을 입력하세요"
        )

        # Metadata inputs
        with st.expander("🏷️ 메타데이터 (선택사항)"):
            col1, col2 = st.columns(2)
            with col1:
                source = st.text_input("출처", placeholder="예: 회사 소개서")
            with col2:
                category = st.text_input("카테고리", placeholder="예: company")

        if st.button("➕ 문서 추가", type="primary"):
            if single_doc:
                try:
                    metadata = {}
                    if source:
                        metadata['source'] = source
                    if category:
                        metadata['category'] = category

                    count = rag_service.add_documents([single_doc], [metadata] if metadata else None)
                    st.success(f"✅ 문서가 성공적으로 추가되었습니다! (청크 수: {count})")

                except Exception as e:
                    st.error(f"❌ 문서 추가 중 오류: {str(e)}")
            else:
                st.warning("⚠️ 문서 내용을 입력해주세요")

    with tab2:
        st.subheader("다중 문서 추가")

        multi_docs = st.text_area(
            "문서 목록 (한 줄에 하나씩):",
            height=300,
            placeholder="""SK Hynix는 메모리 반도체를 생산합니다.
GaiA는 AI 기반 플랫폼입니다.
FastAPI는 Python 웹 프레임워크입니다.""",
            help="각 줄이 하나의 문서로 처리됩니다"
        )

        if st.button("➕ 모든 문서 추가", type="primary"):
            if multi_docs:
                try:
                    # Split by newlines and filter empty lines
                    docs = [line.strip() for line in multi_docs.split('\n') if line.strip()]

                    if docs:
                        count = rag_service.add_documents(docs)
                        st.success(f"✅ {len(docs)}개 문서가 성공적으로 추가되었습니다! (총 청크 수: {count})")
                    else:
                        st.warning("⚠️ 유효한 문서가 없습니다")

                except Exception as e:
                    st.error(f"❌ 문서 추가 중 오류: {str(e)}")
            else:
                st.warning("⚠️ 문서를 입력해주세요")

elif mode == "📊 통계":
    st.header("📊 시스템 통계")

    try:
        stats = rag_service.get_stats()

        # Main stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📄 총 문서 수",
                value=stats.get('document_count', 0)
            )

        with col2:
            st.metric(
                label="🔧 초기화 상태",
                value="완료" if stats.get('initialized', False) else "미완료"
            )

        with col3:
            st.metric(
                label="🧮 임베딩 차원",
                value=stats.get('embedding_dimension', 384)
            )

        st.divider()

        # Detailed info
        st.subheader("📋 상세 정보")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.markdown('<div class="stats-box">', unsafe_allow_html=True)
            st.markdown("**임베딩 모델**")
            st.code(stats.get('embedding_model', 'N/A'))
            st.markdown('</div>', unsafe_allow_html=True)

        with info_col2:
            st.markdown('<div class="stats-box">', unsafe_allow_html=True)
            st.markdown("**벡터 저장소**")
            st.code(stats.get('vector_store_type', 'FAISS (Local)'))
            st.markdown('</div>', unsafe_allow_html=True)

        # System info
        st.divider()
        st.subheader("⚙️ 시스템 정보")

        system_info = {
            "LLM 제공자": "Local (Qwen 2.5)",
            "임베딩 제공자": "Local (HuggingFace)",
            "벡터 DB": "FAISS (개발) / Milvus (프로덕션)",
            "다국어 지원": "✅ 한국어, 영어"
        }

        for key, value in system_info.items():
            st.text(f"{key}: {value}")

        # Refresh button
        if st.button("🔄 통계 새로고침"):
            st.rerun()

    except Exception as e:
        st.error(f"❌ 통계 조회 중 오류: {str(e)}")

# Footer
st.divider()
st.caption("🤖 GaiA-ABiz Backend | Powered by Streamlit & Local LLM | 완전 로컬 실행 (API 비용 제로)")
