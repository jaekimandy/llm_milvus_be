"""
Tests for LangGraph Agents - Stateful Multi-Agent Applications
LangGraph enables building conversational AI agents with memory and state management
"""
import pytest
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import operator


# Define agent state
class AgentState(TypedDict):
    """State for the RAG agent"""
    messages: Annotated[list[BaseMessage], operator.add]
    context: str
    query: str


@pytest.fixture(scope="module")
def knowledge_base():
    """Create a simple knowledge base for RAG"""
    documents = [
        Document(
            page_content="SK Hynix is a South Korean memory semiconductor supplier founded in 1983.",
            metadata={"topic": "company"}
        ),
        Document(
            page_content="SK Hynix produces DRAM, NAND flash memory, and CMOS image sensors.",
            metadata={"topic": "products"}
        ),
        Document(
            page_content="GaiA is SK Hynix's AI assistant platform for enterprise applications.",
            metadata={"topic": "gaia"}
        ),
        Document(
            page_content="A.Biz provides business intelligence and analytics solutions.",
            metadata={"topic": "abiz"}
        ),
    ]

    embeddings = HuggingFaceEmbeddings(
        model_name="paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'}
    )

    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore


class TestLangGraphAgent:
    """Test suite for LangGraph agents"""

    def test_simple_state_graph(self):
        """Test creating a simple state graph"""

        # Define state
        class State(TypedDict):
            counter: int
            message: str

        # Define nodes
        def increment(state: State) -> State:
            return {"counter": state["counter"] + 1, "message": "incremented"}

        def double(state: State) -> State:
            return {"counter": state["counter"] * 2, "message": "doubled"}

        # Build graph
        workflow = StateGraph(State)
        workflow.add_node("increment", increment)
        workflow.add_node("double", double)

        # Add edges
        workflow.set_entry_point("increment")
        workflow.add_edge("increment", "double")
        workflow.add_edge("double", END)

        # Compile
        app = workflow.compile()

        # Run
        result = app.invoke({"counter": 1, "message": "start"})

        print(f"\nSimple graph result: {result}")
        assert result["counter"] == 4  # (1 + 1) * 2
        assert result["message"] == "doubled"

    def test_conditional_routing(self):
        """Test conditional routing in state graph"""

        class State(TypedDict):
            value: int
            path: str

        def check_value(state: State) -> str:
            """Route based on value"""
            if state["value"] > 10:
                return "high"
            else:
                return "low"

        def process_high(state: State) -> State:
            return {"value": state["value"] * 2, "path": "high_path"}

        def process_low(state: State) -> State:
            return {"value": state["value"] + 10, "path": "low_path"}

        # Build graph
        workflow = StateGraph(State)
        workflow.add_node("process_high", process_high)
        workflow.add_node("process_low", process_low)

        # Set entry point with conditional routing
        workflow.set_conditional_entry_point(
            check_value,
            {
                "high": "process_high",
                "low": "process_low"
            }
        )

        workflow.add_edge("process_high", END)
        workflow.add_edge("process_low", END)

        app = workflow.compile()

        # Test high value
        result_high = app.invoke({"value": 15, "path": ""})
        print(f"\nHigh value result: {result_high}")
        assert result_high["value"] == 30
        assert result_high["path"] == "high_path"

        # Test low value
        result_low = app.invoke({"value": 5, "path": ""})
        print(f"\nLow value result: {result_low}")
        assert result_low["value"] == 15
        assert result_low["path"] == "low_path"

    def test_conversation_state(self):
        """Test maintaining conversation state"""

        class ConversationState(TypedDict):
            messages: Annotated[list[BaseMessage], operator.add]
            user_name: str

        def greet(state: ConversationState) -> ConversationState:
            return {
                "messages": [AIMessage(content=f"Hello {state['user_name']}! How can I help you?")]
            }

        def respond(state: ConversationState) -> ConversationState:
            # Get the first human message
            human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
            if human_messages:
                user_query = human_messages[0].content
                response = f"I understand you said: '{user_query}'"
            else:
                response = "How can I help you?"
            return {
                "messages": [AIMessage(content=response)]
            }

        # Build graph
        workflow = StateGraph(ConversationState)
        workflow.add_node("greet", greet)
        workflow.add_node("respond", respond)

        workflow.set_entry_point("greet")
        workflow.add_edge("greet", "respond")
        workflow.add_edge("respond", END)

        app = workflow.compile()

        # Run conversation
        result = app.invoke({
            "messages": [HumanMessage(content="I need help")],
            "user_name": "Alice"
        })

        print(f"\nConversation messages:")
        for msg in result["messages"]:
            print(f"  {msg.__class__.__name__}: {msg.content}")

        assert len(result["messages"]) == 3  # Human + AI greeting + AI response
        assert "Alice" in result["messages"][1].content
        assert "I need help" in result["messages"][2].content

    def test_memory_checkpointing(self):
        """Test state persistence with checkpointing"""

        class State(TypedDict):
            count: int
            history: Annotated[list[str], operator.add]

        def add_one(state: State) -> State:
            new_count = state["count"] + 1
            return {
                "count": new_count,
                "history": [f"Count: {new_count}"]
            }

        # Build graph with memory
        workflow = StateGraph(State)
        workflow.add_node("add", add_one)
        workflow.set_entry_point("add")
        workflow.add_edge("add", END)

        # Add checkpointer
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)

        # Create a thread
        config = {"configurable": {"thread_id": "test_thread_1"}}

        # First invocation
        result1 = app.invoke({"count": 0, "history": []}, config)
        print(f"\nFirst call: {result1}")
        assert result1["count"] == 1

        # Second invocation (should remember state)
        result2 = app.invoke({"count": result1["count"], "history": result1["history"]}, config)
        print(f"Second call: {result2}")
        assert result2["count"] == 2
        # History accumulates: initial + first call + second call
        assert len(result2["history"]) >= 2

    def test_rag_agent_workflow(self, knowledge_base):
        """Test RAG agent with retrieval and response generation"""

        class RAGState(TypedDict):
            query: str
            context: str
            messages: Annotated[list[BaseMessage], operator.add]

        def retrieve(state: RAGState) -> RAGState:
            """Retrieve relevant documents"""
            query = state["query"]
            docs = knowledge_base.similarity_search(query, k=2)
            context = "\n".join([doc.page_content for doc in docs])

            return {
                "context": context,
                "messages": [SystemMessage(content=f"Retrieved context: {context[:100]}...")]
            }

        def generate(state: RAGState) -> RAGState:
            """Generate response using context"""
            context = state["context"]
            query = state["query"]

            # Simple rule-based response (in production, use LLM)
            if "SK Hynix" in context or "memory" in context:
                response = f"Based on the context, {context.split('.')[0]}."
            else:
                response = f"I found information about: {context[:50]}..."

            return {
                "messages": [AIMessage(content=response)]
            }

        # Build RAG workflow
        workflow = StateGraph(RAGState)
        workflow.add_node("retrieve", retrieve)
        workflow.add_node("generate", generate)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        app = workflow.compile()

        # Test RAG
        result = app.invoke({
            "query": "What does SK Hynix produce?",
            "context": "",
            "messages": []
        })

        print(f"\nRAG Agent Query: What does SK Hynix produce?")
        print(f"Context: {result['context'][:100]}...")
        print(f"Response: {result['messages'][-1].content}")

        assert "context" in result
        assert len(result["messages"]) >= 2
        assert any("SK Hynix" in msg.content or "memory" in msg.content.lower()
                  for msg in result["messages"])

    def test_multi_agent_handoff(self):
        """Test handoff between multiple agents"""

        class MultiAgentState(TypedDict):
            task: str
            agent: str
            result: str
            messages: Annotated[list[BaseMessage], operator.add]

        def router(state: MultiAgentState) -> str:
            """Route to appropriate agent"""
            task = state["task"].lower()
            if "search" in task or "find" in task:
                return "search_agent"
            elif "analyze" in task or "calculate" in task:
                return "analysis_agent"
            else:
                return "general_agent"

        def search_agent(state: MultiAgentState) -> MultiAgentState:
            return {
                "agent": "search",
                "result": f"Search completed for: {state['task']}",
                "messages": [AIMessage(content="Search agent: I found relevant information.")]
            }

        def analysis_agent(state: MultiAgentState) -> MultiAgentState:
            return {
                "agent": "analysis",
                "result": f"Analysis completed for: {state['task']}",
                "messages": [AIMessage(content="Analysis agent: I completed the analysis.")]
            }

        def general_agent(state: MultiAgentState) -> MultiAgentState:
            return {
                "agent": "general",
                "result": f"Processed: {state['task']}",
                "messages": [AIMessage(content="General agent: Task processed.")]
            }

        # Build multi-agent workflow
        workflow = StateGraph(MultiAgentState)
        workflow.add_node("search_agent", search_agent)
        workflow.add_node("analysis_agent", analysis_agent)
        workflow.add_node("general_agent", general_agent)

        workflow.set_conditional_entry_point(
            router,
            {
                "search_agent": "search_agent",
                "analysis_agent": "analysis_agent",
                "general_agent": "general_agent"
            }
        )

        workflow.add_edge("search_agent", END)
        workflow.add_edge("analysis_agent", END)
        workflow.add_edge("general_agent", END)

        app = workflow.compile()

        # Test different tasks
        search_result = app.invoke({
            "task": "Search for SK Hynix products",
            "agent": "",
            "result": "",
            "messages": []
        })
        print(f"\nSearch task routed to: {search_result['agent']}")
        assert search_result["agent"] == "search"

        analysis_result = app.invoke({
            "task": "Analyze memory performance",
            "agent": "",
            "result": "",
            "messages": []
        })
        print(f"Analysis task routed to: {analysis_result['agent']}")
        assert analysis_result["agent"] == "analysis"

    def test_graph_visualization(self):
        """Test graph structure and visualization"""

        class State(TypedDict):
            value: int

        def node_a(state: State) -> State:
            return {"value": state["value"] + 1}

        def node_b(state: State) -> State:
            return {"value": state["value"] * 2}

        workflow = StateGraph(State)
        workflow.add_node("a", node_a)
        workflow.add_node("b", node_b)
        workflow.set_entry_point("a")
        workflow.add_edge("a", "b")
        workflow.add_edge("b", END)

        app = workflow.compile()

        # Get graph structure
        graph_dict = app.get_graph().to_json()
        print(f"\nGraph structure: {graph_dict['nodes']}")

        assert "a" in str(graph_dict)
        assert "b" in str(graph_dict)
