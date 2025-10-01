# LLM Configuration Guide

## Supported LLM Providers

The project supports **two LLM providers**:

1. **Anthropic Claude** (Recommended) ✅
2. **OpenAI GPT**

## Supported Embedding Providers

For vector database and RAG features:

1. **Voyage AI** (Recommended - Anthropic's partner) ✅
2. **OpenAI Embeddings**

## Why Claude + Voyage is Recommended

- **You're already paying for Claude** - No additional costs for LLM!
- **Better performance** - Claude Sonnet 4 is state-of-the-art
- **Anthropic recommended** - Voyage AI is Anthropic's official embeddings partner
- **Cost effective** - Cheaper than OpenAI for both chat and embeddings
- **Superior quality** - Voyage embeddings optimized for Claude workflows

---

## Quick Setup: Using Claude + Voyage (Recommended)

### 1. Get Your Anthropic API Key

1. Go to https://console.anthropic.com/
2. Navigate to **API Keys**
3. Create a new API key
4. Copy the key (starts with `sk-ant-`)

### 2. Get Your Voyage AI API Key

1. Go to https://www.voyageai.com/
2. Sign up for an account
3. Navigate to **API Keys**
4. Create a new API key
5. Copy the key (starts with `pa-`)

### 3. Update `.env` File

```bash
# LLM Configuration
LLM_PROVIDER=anthropic

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Embeddings Configuration - Voyage AI (Anthropic's recommended partner)
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-your-voyage-key-here
VOYAGE_MODEL=voyage-3

# Common LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

### 4. Restart the Application

```bash
docker-compose restart api
```

That's it! Your AI Agent now uses Claude + Voyage AI! 🎉

---

## Available Claude Models

### Recommended Models:

**Claude Sonnet 4** (Recommended - Latest!)

```bash
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

- Latest and most capable model
- Best balance of intelligence, speed, and cost
- 200K context window
- Excellent for complex reasoning

**Claude 3.5 Sonnet**

```bash
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

- Previous generation, still excellent
- 200K context window
- Slightly cheaper than Sonnet 4

**Claude 3 Opus**

```bash
ANTHROPIC_MODEL=claude-3-opus-20240229
```

- Highest intelligence (previous gen)
- Best for complex analysis
- More expensive

**Claude 3 Haiku**

```bash
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

- Fastest, most affordable
- Good for simple queries
- Lower latency

---

## Available Voyage Models

**Voyage 3** (Recommended)

```bash
VOYAGE_MODEL=voyage-3
```

- Latest generation embeddings
- Optimized for Claude workflows
- Best quality

**Voyage 2**

```bash
VOYAGE_MODEL=voyage-2
```

- Previous generation
- Still excellent quality
- Slightly cheaper

---

## Using OpenAI Instead

If you prefer to use OpenAI:

### 1. Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Navigate to **API Keys**
3. Create a new key
4. Copy the key

### 2. Update `.env` File

```bash
# LLM Configuration
LLM_PROVIDER=openai

# Anthropic (not needed)
ANTHROPIC_API_KEY=

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4

# Common LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

### Available OpenAI Models:

```bash
OPENAI_MODEL=gpt-4                    # Most capable
OPENAI_MODEL=gpt-4-turbo             # Faster, cheaper
OPENAI_MODEL=gpt-3.5-turbo           # Fastest, cheapest
```

---

## Important Note: Embeddings

**Anthropic (Claude) does NOT provide embeddings API.**

For the vector database (Milvus) and RAG features to work, you need embeddings. Options:

### Option 1: Use Voyage AI for Embeddings (Recommended ✅)

**Anthropic's official recommendation!** Voyage AI is optimized for Claude:

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-your-voyage-key
VOYAGE_MODEL=voyage-3
```

**Benefits:**
- Optimized for Claude workflows
- Superior embedding quality
- Cost-effective ($0.12 per 1M tokens)
- Officially recommended by Anthropic

### Option 2: Use OpenAI for Embeddings

If you prefer OpenAI embeddings:

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
```

**Benefits:**
- Familiar API
- Good quality embeddings
- More expensive ($0.13 per 1M tokens)

---

## Configuration Examples

### Example 1: Claude + Voyage AI (Recommended ✅)

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-xxxxx
VOYAGE_MODEL=voyage-3
```

**Usage**:

- Chat: Claude Sonnet 4 (latest!)
- Embeddings: Voyage AI voyage-3
- Cost: ~$3/1M tokens for chat, ~$0.12/1M tokens for embeddings
- **Best quality** - Anthropic's recommended stack!

### Example 2: Claude + OpenAI Embeddings

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
```

**Usage**:

- Chat: Claude Sonnet 4
- Embeddings: OpenAI text-embedding-3-small
- Cost: ~$3/1M tokens for chat, ~$0.13/1M tokens for embeddings

### Example 3: OpenAI Only

```bash
LLM_PROVIDER=openai
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4-turbo
```

**Usage**:

- Chat: GPT-4 Turbo
- Embeddings: OpenAI text-embedding-3-small
- Cost: ~$10/1M tokens for chat

---

## Switching Between Providers

You can switch anytime by changing configuration variables:

```bash
# Use Claude + Voyage (Recommended)
LLM_PROVIDER=anthropic
EMBEDDINGS_PROVIDER=voyage

# Use Claude + OpenAI embeddings
LLM_PROVIDER=anthropic
EMBEDDINGS_PROVIDER=openai

# Use OpenAI for everything
LLM_PROVIDER=openai
EMBEDDINGS_PROVIDER=openai
```

Restart the application:

```bash
docker-compose restart api
```

No code changes needed! 🚀

---

## Testing Your Configuration

### Test Chat Functionality

```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hello! Which AI model are you?",
    "agent_type": "general"
  }'
```

**Expected Response (Claude)**:

```json
{
  "response": "I'm Claude, an AI assistant made by Anthropic..."
}
```

**Expected Response (OpenAI)**:

```json
{
  "response": "I'm ChatGPT, a large language model by OpenAI..."
}
```

### Check Logs

```bash
docker-compose logs api | grep -i "llm"
```

You should see which provider is initialized.

---

## Cost Comparison

### LLM Costs

**Claude Sonnet 4** (Recommended)
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- Context: 200K tokens

**GPT-4 Turbo**
- Input: $10 per 1M tokens
- Output: $30 per 1M tokens
- Context: 128K tokens

**GPT-3.5 Turbo**
- Input: $0.50 per 1M tokens
- Output: $1.50 per 1M tokens
- Context: 16K tokens

### Embeddings Costs

**Voyage AI** (Recommended)
- $0.12 per 1M tokens
- Optimized for Claude

**OpenAI Embeddings**
- $0.13 per 1M tokens
- text-embedding-3-small

### Total Cost Comparison

**For typical usage (1000 queries/day, avg 500 tokens each):**

- **Claude + Voyage**: ~$5-10/month (Recommended ✅)
- Claude + OpenAI: ~$5-10/month
- GPT-4 + OpenAI: ~$15-30/month
- GPT-3.5 + OpenAI: ~$1-2/month

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY is required"

**Solution**: Add your Anthropic API key to `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Error: "Embeddings provider not configured"

**Solution**: Add Voyage AI or OpenAI API key for embeddings:

```bash
# Option 1: Voyage AI (Recommended)
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-your-voyage-key

# Option 2: OpenAI
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-openai-key
```

### Error: "Unsupported LLM_PROVIDER"

**Solution**: Use only `anthropic` or `openai`:

```bash
LLM_PROVIDER=anthropic  # or openai
```

### Chat works but knowledge base doesn't

**Issue**: No embeddings configured

**Solution**: Set up embeddings provider:

```bash
# Recommended: Voyage AI
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-your-key

# Alternative: OpenAI
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

---

## Best Practices

### For Development:

- Use **Claude Sonnet 4** (latest, best balance)
- Use **Voyage AI** embeddings (Anthropic recommended)
- This is the optimal stack!

### For Production:

- Use **Claude Sonnet 4** for most queries
- Use **Claude Haiku** for simple/frequent queries
- Use **Voyage AI** for embeddings (superior quality)
- Monitor costs with API usage dashboards

### For Testing:

- Use **GPT-3.5 Turbo** (cheapest LLM)
- Or use **Claude Haiku** (cheap + good quality)

---

## Summary

**Recommended Setup (Anthropic Stack):**

```bash
# LLM Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Embeddings Configuration
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-xxxxx
VOYAGE_MODEL=voyage-3

# Common Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

This gives you:

- ✅ **Claude Sonnet 4** for chat (latest & most capable!)
- ✅ **Voyage AI** for embeddings (Anthropic's recommendation)
- ✅ **Best performance** and quality
- ✅ **Full RAG functionality**
- ✅ **Cost effective** (~$3/1M tokens + $0.12/1M embeddings)
- ✅ **No OpenAI dependency** needed!

Happy coding! 🎉

---

## Reference Links

- **Anthropic Console**: https://console.anthropic.com/
- **Voyage AI**: https://www.voyageai.com/
- **Claude Models**: https://docs.anthropic.com/claude/docs/models-overview
- **Voyage Embeddings**: https://docs.voyageai.com/
- **Why Voyage for Claude**: https://docs.claude.com/en/docs/build-with-claude/embeddings
