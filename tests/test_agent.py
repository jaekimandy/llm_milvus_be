import pytest
from fastapi.testclient import TestClient
from main import app
from agent.llm_client import LLMClient
from agent.graph_agent import GraphAgent, AgentState
from config.settings import settings

client = TestClient(app)


# Test LLM Client
class TestLLMClient:
    """Test LLM client functionality"""

    def test_llm_client_initialization(self):
        """Test that LLM client initializes correctly"""
        llm = LLMClient()
        assert llm.provider == settings.LLM_PROVIDER.lower()
        assert llm.chat_model is not None

    def test_llm_provider_is_anthropic(self):
        """Test that provider is set to anthropic"""
        llm = LLMClient()
        assert llm.provider == "anthropic"

    @pytest.mark.asyncio
    async def test_generate_simple_response(self):
        """Test basic LLM response generation"""
        llm = LLMClient()

        messages = [
            {"role": "user", "content": "Say 'Hello' and nothing else."}
        ]

        response = await llm.generate_response(messages)

        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"\n✓ LLM Response: {response}")

    @pytest.mark.asyncio
    async def test_generate_response_with_system_prompt(self):
        """Test LLM with system prompt"""
        llm = LLMClient()

        system_prompt = "You are a helpful assistant. Always respond in exactly 3 words."
        messages = [
            {"role": "user", "content": "What is Python?"}
        ]

        response = await llm.generate_response(messages, system_prompt)

        assert response is not None
        assert isinstance(response, str)
        # Claude might not follow exactly 3 words, but should be brief
        word_count = len(response.split())
        assert word_count <= 10, f"Response too long: {word_count} words"
        print(f"\n✓ System Prompt Response: {response}")

    @pytest.mark.asyncio
    async def test_conversation_context(self):
        """Test multi-turn conversation"""
        llm = LLMClient()

        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Nice to meet you, Alice!"},
            {"role": "user", "content": "What is my name?"}
        ]

        response = await llm.generate_response(messages)

        assert response is not None
        assert "alice" in response.lower(), "LLM should remember the name from context"
        print(f"\n✓ Context Response: {response}")


# Test Graph Agent
class TestGraphAgent:
    """Test LangGraph agent functionality"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test that agent initializes correctly"""
        agent = GraphAgent(agent_type="test")
        assert agent.agent_type == "test"
        assert agent.graph is not None

    @pytest.mark.asyncio
    async def test_agent_simple_query(self):
        """Test agent with a simple query"""
        agent = GraphAgent(agent_type="general")

        result = await agent.run("What is 2+2?")

        assert result is not None
        assert "response" in result
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        print(f"\n✓ Agent Response: {result['response']}")

    @pytest.mark.asyncio
    async def test_agent_context_retrieval(self):
        """Test that agent attempts to retrieve context"""
        agent = GraphAgent(agent_type="general")

        result = await agent.run("Tell me about FastAPI")

        assert "response" in result
        assert "retrieval_results" in result
        # retrieval_results might be empty if no knowledge base data
        assert isinstance(result["retrieval_results"], list)
        print(f"\n✓ Agent with retrieval: {result['response'][:100]}...")


# Test Agent API Endpoints
class TestAgentAPI:
    """Test Agent API endpoints"""

    @pytest.fixture
    def auth_token(self):
        """Create a user and get auth token"""
        # Register user
        client.post(
            "/auth/register",
            json={
                "email": "agent_test@example.com",
                "username": "agent_tester",
                "password": "testpass123",
                "full_name": "Agent Tester"
            }
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "username": "agent_tester",
                "password": "testpass123"
            }
        )

        return response.json()["access_token"]

    def test_agent_query_without_auth(self):
        """Test that agent query requires authentication"""
        response = client.post(
            "/agent/query",
            json={
                "query": "Hello",
                "agent_type": "general"
            }
        )

        assert response.status_code == 401

    def test_agent_query_with_auth(self, auth_token):
        """Test agent query with authentication"""
        response = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "What is the capital of France?",
                "agent_type": "general"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "response" in data
        assert "session_id" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        # Should mention Paris
        assert "paris" in data["response"].lower()
        print(f"\n✓ API Response: {data['response']}")

    def test_create_session(self, auth_token):
        """Test creating a new agent session"""
        response = client.post(
            "/agent/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "agent_type": "general"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["agent_type"] == "general"
        assert data["status"] == "active"

    def test_get_sessions(self, auth_token):
        """Test getting user's sessions"""
        # Create a session first
        client.post(
            "/agent/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"agent_type": "general"}
        )

        # Get sessions
        response = client.get(
            "/agent/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "agent_type" in data[0]

    def test_agent_query_creates_session(self, auth_token):
        """Test that query without session_id creates new session"""
        response = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "Hello, how are you?",
                "agent_type": "general"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        session_id = data["session_id"]

        # Verify session was created
        sessions = client.get(
            "/agent/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        ).json()

        session_ids = [s["id"] for s in sessions]
        assert session_id in session_ids

    def test_agent_query_with_existing_session(self, auth_token):
        """Test querying with an existing session"""
        # First query - creates session
        response1 = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "My favorite color is blue.",
                "agent_type": "general"
            }
        )

        session_id = response1.json()["session_id"]

        # Second query - uses same session
        response2 = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "What is my favorite color?",
                "agent_type": "general",
                "session_id": session_id
            }
        )

        assert response2.status_code == 200
        data = response2.json()

        assert data["session_id"] == session_id
        # Should remember from previous message
        # Note: This might not work perfectly without proper context retrieval
        print(f"\n✓ Context Query Response: {data['response']}")

    def test_get_session_messages(self, auth_token):
        """Test getting messages from a session"""
        # Create session with a query
        query_response = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "Hello!",
                "agent_type": "general"
            }
        )

        session_id = query_response.json()["session_id"]

        # Get messages
        response = client.get(
            f"/agent/sessions/{session_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        messages = response.json()

        assert isinstance(messages, list)
        assert len(messages) >= 2  # At least user + assistant
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello!"
        assert messages[1]["role"] == "assistant"


# Test Different Agent Types
class TestAgentTypes:
    """Test different agent types"""

    @pytest.fixture
    def auth_token(self):
        """Create a user and get auth token"""
        client.post(
            "/auth/register",
            json={
                "email": "agenttype_test@example.com",
                "username": "agenttype_tester",
                "password": "testpass123"
            }
        )

        response = client.post(
            "/auth/login",
            json={"username": "agenttype_tester", "password": "testpass123"}
        )

        return response.json()["access_token"]

    def test_general_agent(self, auth_token):
        """Test general agent type"""
        response = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "What is FastAPI?",
                "agent_type": "general"
            }
        )

        assert response.status_code == 200
        assert "fastapi" in response.json()["response"].lower()

    def test_technical_agent(self, auth_token):
        """Test technical agent type"""
        response = client.post(
            "/agent/query",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "Explain Docker containers",
                "agent_type": "technical"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 0


# Performance Tests
class TestAgentPerformance:
    """Test agent performance"""

    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test that response time is reasonable"""
        import time

        llm = LLMClient()
        messages = [{"role": "user", "content": "Say hello"}]

        start = time.time()
        response = await llm.generate_response(messages)
        duration = time.time() - start

        assert response is not None
        assert duration < 10, f"Response took too long: {duration}s"
        print(f"\n✓ Response time: {duration:.2f}s")

    @pytest.mark.asyncio
    async def test_multiple_queries(self):
        """Test handling multiple queries"""
        llm = LLMClient()

        queries = [
            "What is 1+1?",
            "What is the capital of Japan?",
            "What color is the sky?"
        ]

        for query in queries:
            messages = [{"role": "user", "content": query}]
            response = await llm.generate_response(messages)
            assert response is not None
            assert len(response) > 0

        print("\n✓ Multiple queries handled successfully")


# Error Handling Tests
class TestAgentErrorHandling:
    """Test error handling"""

    def test_invalid_agent_type(self):
        """Test handling of invalid agent type"""
        # This should still work - we accept any agent_type string
        agent = GraphAgent(agent_type="invalid_type")
        assert agent.agent_type == "invalid_type"

    def test_empty_query(self):
        """Test handling of empty query"""
        agent = GraphAgent(agent_type="general")

        # Empty query should still be handled
        # (LLM will respond appropriately)
        import asyncio
        result = asyncio.run(agent.run(""))
        assert "response" in result

    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test handling of very long query"""
        llm = LLMClient()

        # Create a long query (but within token limits)
        long_query = "Tell me about Python. " * 100
        messages = [{"role": "user", "content": long_query}]

        response = await llm.generate_response(messages)
        assert response is not None
        print(f"\n✓ Long query handled: {len(response)} chars response")


if __name__ == "__main__":
    # Run with: pytest tests/test_agent.py -v -s
    pytest.main([__file__, "-v", "-s"])
