# Milvus Vector Database Setup Guide

## Overview

Milvus is the vector database used in GaiA-ABiz for storing and searching document embeddings. It enables semantic search and powers the RAG (Retrieval Augmented Generation) functionality of the AI agent.

## Architecture

```
┌─────────────────┐
│   API Server    │
│   (FastAPI)     │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
┌────────▼────────┐ ┌──▼──────────────┐
│  Milvus Vector  │ │  Claude AI      │
│    Database     │ │  (Chat)         │
│                 │ │                 │
│  - Stores       │ │  Voyage AI      │
│    embeddings   │ │  (Embeddings)   │
│  - IVF_FLAT     │ │                 │
│  - L2 distance  │ │  1024 dims      │
└────────┬────────┘ └─────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│ ETCD  │ │ MinIO │
│(Meta) │ │(Data) │
└───────┘ └───────┘
```

## Components

### Milvus
- **Version**: v2.3.3
- **Purpose**: Vector similarity search
- **Storage**: Persistent volumes for data
- **Ports**: 19530 (gRPC), 9091 (metrics)

### ETCD
- **Purpose**: Metadata storage for Milvus
- **Port**: 2379

### MinIO
- **Purpose**: Object storage for Milvus data
- **Port**: 9000

## Configuration

### Environment Variables

```bash
# Milvus Configuration
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=gaia_embeddings
```

### Collection Schema

```python
Collection: gaia_embeddings
├── id: INT64 (primary key, auto-generated)
├── embedding: FLOAT_VECTOR (dim=1024)  # Voyage AI dimensions
├── text: VARCHAR (max_length=65535)    # Document content
└── metadata: VARCHAR (max_length=65535) # JSON metadata
```

### Index Configuration

- **Type**: IVF_FLAT
- **Metric**: L2 (Euclidean distance)
- **Parameters**: nlist=1024

## Setup Instructions

### 1. Start Services

Start all required services including Milvus:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (database)
- ETCD (Milvus metadata)
- MinIO (Milvus storage)
- Milvus (vector database)
- API (FastAPI application)

### 2. Initialize Milvus

Create the collection with the correct embedding dimensions:

```bash
docker-compose exec api python scripts/init_milvus.py
```

**Expected output:**
```
🚀 Initializing Milvus Vector Database
   Host: milvus
   Port: 19530
   Collection: gaia_embeddings

1️⃣  Connecting to Milvus...
   ✓ Connected successfully

2️⃣  Detecting embedding dimensions...
   ✓ Embedding dimension: 1024

3️⃣  Creating collection with dimension 1024...
   ✓ Collection created successfully

4️⃣  Verifying setup...
   ✓ Collection is ready

✅ Milvus initialization complete!
```

### 3. Add Sample Data

Insert sample documents to test the system:

```bash
docker-compose exec api python scripts/add_sample_data.py
```

**Expected output:**
```
📚 Adding Sample Data to Milvus
   Documents to add: 10

1️⃣  Connecting to Milvus...
   ✓ Connected

2️⃣  Loading collection...
   ✓ Collection loaded: gaia_embeddings

3️⃣  Generating embeddings...
   ✓ Generated 10 embeddings
   ✓ Embedding dimension: 1024

4️⃣  Inserting into Milvus...
   ✓ Inserted 10 documents

5️⃣  Verifying insertion...
   ✓ Total documents in collection: 10

✅ Sample data added successfully!
```

### 4. Test Search

Verify semantic search functionality:

```bash
docker-compose exec api python scripts/test_milvus.py
```

**Expected output:**
```
🧪 Testing Milvus Vector Database

1️⃣  Connecting to Milvus...
   ✓ Connected

2️⃣  Loading collection...
   ✓ Collection loaded: gaia_embeddings
   ✓ Documents in collection: 10

3️⃣  Running test queries...

🔍 Query: 'What is GaiA-ABiz?'
   ✓ Generated query embedding (dim: 1024)
   ✓ Found 3 results

   Result 1:
      Distance: 0.9966
      Text: GaiA-ABiz is a backend system...
      Source: project_overview
      Category: introduction

✅ Milvus tests complete!
```

## Usage in Code

### Connecting to Milvus

```python
from agent.vector_store import vector_store

# Connect
vector_store.connect()

# Create/load collection
vector_store.create_collection(dim=1024)
```

### Inserting Documents

```python
from agent.llm_client import llm_client

# Your documents
texts = [
    "First document content",
    "Second document content",
]
metadata = ['{"source": "doc1"}', '{"source": "doc2"}']

# Generate embeddings
embeddings = await llm_client.generate_batch_embeddings(texts)

# Insert into Milvus
vector_store.insert(
    embeddings=embeddings,
    texts=texts,
    metadata=metadata
)
```

### Searching

```python
# Generate query embedding
query = "What is the project about?"
query_embedding = await llm_client.generate_embeddings(query)

# Search
results = vector_store.search(
    query_embedding=query_embedding,
    top_k=5
)

# Process results
for result in results:
    print(f"Distance: {result['distance']}")
    print(f"Text: {result['text']}")
    print(f"Metadata: {result['metadata']}")
```

## Voyage AI Integration

### Embedding Dimensions

Voyage AI models have specific dimensions:

| Model | Dimensions |
|-------|-----------|
| voyage-3 | 1024 |
| voyage-2 | 1024 |
| voyage-large-2 | 1536 |

The initialization script automatically detects the correct dimensions based on your configured model.

### Configuration

```bash
# In .env file
EMBEDDINGS_PROVIDER=voyage
VOYAGE_API_KEY=pa-your-key-here
VOYAGE_MODEL=voyage-3
```

## Troubleshooting

### Connection Failed

**Error:**
```
✗ Connection failed: Fail connecting to server on milvus:19530
```

**Solution:**
1. Check if Milvus is running:
   ```bash
   docker-compose ps milvus
   ```

2. Restart Milvus:
   ```bash
   docker-compose restart milvus
   docker-compose restart etcd
   docker-compose restart minio
   ```

3. Check logs:
   ```bash
   docker-compose logs milvus
   ```

### Collection Already Exists

**Error:**
```
Collection already exists
```

**Solution:**
This is normal. The script will load the existing collection. To recreate:

```python
# In Python shell
from pymilvus import connections, utility
connections.connect(host="milvus", port=19530)
utility.drop_collection("gaia_embeddings")
```

Then re-run `init_milvus.py`.

### Dimension Mismatch

**Error:**
```
Dimension mismatch: expected 1024, got 1536
```

**Solution:**
You changed the embedding model. Drop the collection and recreate:

```bash
docker-compose exec api python scripts/init_milvus.py
```

### Rate Limiting (Voyage AI)

**Error:**
```
You have not yet added your payment method... rate limits of 3 RPM
```

**Solution:**
Voyage AI free tier has 3 requests per minute. Options:

1. **Add payment method** (recommended):
   - Go to https://dashboard.voyageai.com/
   - Add payment method in billing
   - Get 200M free tokens + higher rate limits

2. **Wait between requests**:
   ```python
   import time
   time.sleep(20)  # Wait 20 seconds between requests
   ```

3. **Use batch operations**:
   ```python
   # Instead of multiple single calls
   embeddings = await llm_client.generate_batch_embeddings(texts)
   ```

### ETCD Connection Issues

**Error:**
```
Failed to connect to etcd
```

**Solution:**
```bash
# Restart ETCD
docker-compose restart etcd

# Wait for it to be ready
sleep 5

# Restart Milvus
docker-compose restart milvus
```

## Performance Tuning

### Index Parameters

For better search performance, adjust index parameters:

```python
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {
        "nlist": 2048  # Increase for larger datasets
    }
}
```

### Search Parameters

```python
search_params = {
    "metric_type": "L2",
    "params": {
        "nprobe": 20  # Increase for better accuracy
    }
}
```

### Batch Operations

Always use batch operations for better performance:

```python
# Good - batch insert
embeddings = await llm_client.generate_batch_embeddings(many_texts)
vector_store.insert(embeddings, many_texts, metadata_list)

# Bad - individual inserts
for text in many_texts:
    embedding = await llm_client.generate_embeddings(text)
    vector_store.insert([embedding], [text], [metadata])
```

## Monitoring

### Check Collection Stats

```bash
docker-compose exec api python -c "
from pymilvus import connections, Collection
connections.connect(host='milvus', port=19530)
collection = Collection('gaia_embeddings')
print(f'Documents: {collection.num_entities}')
"
```

### Milvus Metrics

Milvus exposes Prometheus metrics on port 9091:

```bash
curl http://localhost:9091/metrics
```

### Storage Usage

```bash
# Check volume sizes
docker system df -v | grep milvus
```

## Backup and Restore

### Backup

```bash
# Backup Milvus data
docker cp gaia-abiz-backend-milvus-1:/var/lib/milvus ./milvus_backup

# Backup ETCD data
docker cp gaia-abiz-backend-etcd-1:/etcd ./etcd_backup
```

### Restore

```bash
# Stop services
docker-compose down

# Restore data
docker cp ./milvus_backup/. gaia-abiz-backend-milvus-1:/var/lib/milvus
docker cp ./etcd_backup/. gaia-abiz-backend-etcd-1:/etcd

# Start services
docker-compose up -d
```

## Best Practices

1. **Use batch operations** for multiple documents
2. **Monitor rate limits** (Voyage AI: 3 RPM free tier)
3. **Regular backups** of Milvus data
4. **Index tuning** based on dataset size
5. **Connection pooling** for production use

## Production Considerations

### Scaling

For production deployments:

1. **Distributed Milvus**: Use Milvus cluster mode
2. **Separate ETCD cluster**: For high availability
3. **S3 instead of MinIO**: For cloud deployments
4. **Load balancing**: Multiple Milvus instances

### Security

1. **Enable authentication** in Milvus
2. **Network isolation** for internal services
3. **TLS encryption** for connections
4. **API key rotation** for Voyage AI

### Monitoring

1. Set up Prometheus + Grafana
2. Monitor query latency
3. Track embedding generation time
4. Alert on connection failures

## Reference

- **Milvus Docs**: https://milvus.io/docs
- **Voyage AI Docs**: https://docs.voyageai.com/
- **Python SDK**: https://milvus.io/docs/install-pymilvus.md

## Summary

Your Milvus setup is now complete with:

- ✅ Vector database running
- ✅ Voyage AI embeddings (1024 dimensions)
- ✅ Sample data loaded
- ✅ Semantic search working
- ✅ Ready for RAG applications

For adding your own documents, see the [RAG_USAGE.md](RAG_USAGE.md) guide.
