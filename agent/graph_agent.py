from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from agent.llm_client import llm_client
from agent.vector_store import vector_store
import operator


class AgentState(TypedDict):
    """State for the agent graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    context: str
    response: str
    retrieval_results: list


class GraphAgent:
    """LangGraph-based AI Agent"""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the agent workflow graph"""
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("retrieve", self.retrieve_context)
        workflow.add_node("generate", self.generate_response)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    async def retrieve_context(self, state: AgentState) -> dict:
        """Retrieve context from vector store"""
        query = state["query"]

        # Generate query embedding
        query_embedding = await llm_client.generate_embeddings(query)

        # Search vector store
        results = vector_store.search(query_embedding, top_k=5)

        # Format context
        context_parts = []
        for result in results:
            context_parts.append(result["text"])

        context = "\n\n".join(context_parts)

        return {
            "context": context,
            "retrieval_results": results
        }

    async def generate_response(self, state: AgentState) -> dict:
        """Generate response using LLM"""
        query = state["query"]
        context = state.get("context", "")

        system_prompt = f"""You are an AI assistant for the GaiA-ABiz system.
Your role is to help users with their questions using the provided context.

Context:
{context}

Please provide accurate and helpful responses based on the context above.
If the context doesn't contain relevant information, politely indicate that.
"""

        messages = [
            {"role": "user", "content": query}
        ]

        response = await llm_client.generate_response(
            messages=messages,
            system_prompt=system_prompt
        )

        return {"response": response}

    async def run(self, query: str) -> dict:
        """Run the agent"""
        initial_state = {
            "messages": [],
            "query": query,
            "context": "",
            "response": "",
            "retrieval_results": []
        }

        result = await self.graph.ainvoke(initial_state)
        return result


# Agent factory
def create_agent(agent_type: str) -> GraphAgent:
    """Create an agent based on type"""
    return GraphAgent(agent_type)
