# Milvus 설정 가이드

**Milvus 벡터 데이터베이스 설정 및 최적화**

---

## 개요

Milvus는 GaiA-ABiz 백엔드의 프로덕션 벡터 저장소로 사용됩니다. 이 가이드는 Milvus 설치, 구성, 최적화 방법을 다룹니다.

**주요 특징**:
- 대규모 벡터 검색 (수백만~수십억 벡터)
- 다양한 인덱스 타입 지원 (IVF, HNSW, ANNOY 등)
- 수평 확장 가능
- 클라우드 네이티브 아키텍처
- GPU 가속 지원

---

## 목차

1. [빠른 시작 (Docker)](#빠른-시작-docker)
2. [Milvus 아키텍처](#milvus-아키텍처)
3. [설정 및 최적화](#설정-및-최적화)
4. [컬렉션 관리](#컬렉션-관리)
5. [인덱싱 전략](#인덱싱-전략)
6. [검색 최적화](#검색-최적화)
7. [모니터링](#모니터링)
8. [백업 및 복구](#백업-및-복구)
9. [문제 해결](#문제-해결)

---

## 빠른 시작 (Docker)

### 1. Docker Compose로 시작

프로젝트 루트의 `docker-compose.yml`에 Milvus가 포함되어 있습니다.

```bash
# Milvus 및 의존성 서비스 시작
docker-compose up -d milvus etcd minio

# 로그 확인
docker-compose logs -f milvus

# 상태 확인
docker-compose ps milvus
```

**서비스 구성**:
- **Milvus**: 벡터 데이터베이스 (포트 19530, 9091)
- **etcd**: 메타데이터 저장소
- **MinIO**: 벡터 및 로그 파일 저장소

### 2. Milvus 초기화

```bash
# 컬렉션 생성 및 인덱스 설정
python scripts/init_milvus.py
```

**예상 출력**:
```
🚀 Initializing Milvus Vector Database
   Host: localhost
   Port: 19530
   Collection: documents

1️⃣  Connecting to Milvus...
   ✓ Connected successfully

2️⃣  Detecting embedding dimensions...
   📊 Detecting embedding dimensions for provider: local
   ✓ Embedding dimension: 768

3️⃣  Creating collection with dimension 768...
   ✓ Collection created successfully

4️⃣  Verifying setup...
   ✓ Collection is ready
   ✓ Collection name: documents
   ✓ Collection schema: <Schema>

✅ Milvus initialization complete!
```

### 3. 연결 테스트

```python
from pymilvus import connections, utility

# Milvus에 연결
connections.connect(host="localhost", port="19530")

# 버전 확인
print(f"Milvus 버전: {utility.get_server_version()}")

# 컬렉션 목록
collections = utility.list_collections()
print(f"컬렉션: {collections}")
```

---

## Milvus 아키텍처

### Standalone 모드 (개발/소규모)

```
┌─────────────────────────────────────┐
│         Milvus Standalone          │
│  ┌──────────┐  ┌─────────────────┐ │
│  │  Query   │  │   Data Node     │ │
│  │  Node    │  │  (Insert/Index) │ │
│  └──────────┘  └─────────────────┘ │
└─────────────────────────────────────┘
         │                  │
    ┌────┴────┐        ┌────┴─────┐
    │  etcd   │        │  MinIO   │
    │(메타데이터)│        │(벡터 데이터)│
    └─────────┘        └──────────┘
```

**장점**:
- 간단한 배포
- 낮은 리소스 요구사항
- 빠른 시작

**제한사항**:
- 단일 노드 (확장 불가)
- 중간 규모 데이터 (<100만 벡터)

### Cluster 모드 (프로덕션)

```
                ┌──────────────┐
                │ Load Balancer│
                └──────┬───────┘
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ Query   │   │ Query   │   │ Query   │
    │ Node 1  │   │ Node 2  │   │ Node 3  │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
         └─────────────┼─────────────┘
                  ┌────┴────┐
                  │ Coord   │
                  │ Nodes   │
                  └────┬────┘
              ┌────────┼────────┐
         ┌────┴────┐       ┌────┴────┐
         │  Data   │       │  Index  │
         │  Nodes  │       │  Nodes  │
         └────┬────┘       └────┬────┘
              │                 │
         ┌────┴─────────────────┴────┐
         │   etcd + MinIO Cluster    │
         └───────────────────────────┘
```

**장점**:
- 수평 확장 가능
- 고가용성
- 대규모 데이터 지원 (수십억 벡터)

---

## 설정 및 최적화

### Docker Compose 설정

`docker-compose.yml`:

```yaml
milvus:
  image: milvusdb/milvus:v2.3.3
  command: ["milvus", "run", "standalone"]
  environment:
    ETCD_ENDPOINTS: etcd:2379
    MINIO_ADDRESS: minio:9000
    COMMON_STORAGETYPE: minio
  ports:
    - "19530:19530"  # gRPC
    - "9091:9091"    # HTTP/메트릭
  volumes:
    - milvus_data:/var/lib/milvus
    - ./milvus.yaml:/milvus/configs/milvus.yaml  # 커스텀 설정
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Milvus 설정 파일

`milvus.yaml` (커스텀 설정):

```yaml
# 데이터 노드 설정
dataNode:
  flush:
    # 플러시 간격 (초)
    interval: 1
  # 삽입 버퍼 크기 (MB)
  insertBuffer:
    size: 512

# 쿼리 노드 설정
queryNode:
  # 캐시 크기 (GB)
  cacheSize: 4
  # 검색 결과 캐시 활성화
  enableDiskCache: true

# 인덱스 노드 설정
indexNode:
  # 인덱스 빌드 스레드 수
  buildParallel: 2

# 로그 설정
log:
  level: info
  file:
    maxSize: 100  # MB
    maxAge: 7     # days
```

### 환경 변수

`.env`:

```bash
# Milvus 연결
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=documents

# 성능 튜닝
MILVUS_CACHE_SIZE=4  # GB
MILVUS_INSERT_BUFFER_SIZE=512  # MB
MILVUS_BUILD_INDEX_PARALLEL=2
```

---

## 컬렉션 관리

### 컬렉션 생성

```python
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType

# 스키마 정의
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="metadata", dtype=DataType.JSON),
    FieldSchema(name="timestamp", dtype=DataType.INT64)
]

schema = CollectionSchema(
    fields=fields,
    description="문서 임베딩 컬렉션",
    enable_dynamic_field=True
)

# 컬렉션 생성
collection = Collection(
    name="documents",
    schema=schema,
    using="default"
)

print(f"컬렉션 '{collection.name}' 생성 완료")
```

### 컬렉션 정보 조회

```python
from pymilvus import Collection, utility

collection = Collection("documents")

# 통계
print(f"엔티티 수: {collection.num_entities}")
print(f"인덱스 정보: {collection.indexes}")

# 상세 정보
print(f"스키마: {collection.schema}")
print(f"설명: {collection.description}")

# 모든 컬렉션 목록
all_collections = utility.list_collections()
print(f"전체 컬렉션: {all_collections}")
```

### 컬렉션 삭제

```python
from pymilvus import utility

# 컬렉션 삭제
utility.drop_collection("old_collection")

# 확인
print(f"남은 컬렉션: {utility.list_collections()}")
```

---

## 인덱싱 전략

### 인덱스 타입 비교

| 인덱스 타입 | 검색 속도 | 정확도 | 메모리 | 빌드 시간 | 권장 사용 |
|------------|----------|--------|--------|----------|-----------|
| **FLAT** | 느림 | 100% | 높음 | 빠름 | <10K 벡터 |
| **IVF_FLAT** | 중간 | 98%+ | 중간 | 중간 | 10K-100만 |
| **IVF_SQ8** | 빠름 | 95%+ | 낮음 | 중간 | 100만-1000만 |
| **IVF_PQ** | 매우 빠름 | 90%+ | 매우 낮음 | 느림 | >1000만 |
| **HNSW** | 매우 빠름 | 99%+ | 높음 | 느림 | 실시간 검색 |

### IVF_FLAT 인덱스 (권장)

**중간 규모 데이터셋에 최적 (10K-100만 벡터)**

```python
from pymilvus import Collection

collection = Collection("documents")

# IVF_FLAT 인덱스 생성
index_params = {
    "metric_type": "L2",  # 또는 "IP" (Inner Product)
    "index_type": "IVF_FLAT",
    "params": {
        "nlist": 1024  # 클러스터 수 (√N ~ 4√N 권장)
    }
}

collection.create_index(
    field_name="embedding",
    index_params=index_params
)

print("IVF_FLAT 인덱스 생성 완료")
```

**파라미터 튜닝**:
- `nlist`: 클러스터 수 (데이터 크기에 따라 조정)
  - 10K 벡터: nlist=128
  - 100K 벡터: nlist=512
  - 1M 벡터: nlist=2048

### HNSW 인덱스 (고성능)

**실시간 검색이 중요한 경우**

```python
index_params = {
    "metric_type": "L2",
    "index_type": "HNSW",
    "params": {
        "M": 16,         # 그래프 연결 수 (4-64)
        "efConstruction": 200  # 빌드 품질 (100-500)
    }
}

collection.create_index(
    field_name="embedding",
    index_params=index_params
)
```

**파라미터 튜닝**:
- `M`: 그래프 밀도 (높을수록 정확도↑, 메모리↑)
- `efConstruction`: 빌드 품질 (높을수록 정확도↑, 빌드 시간↑)

### 인덱스 로드

```python
# 메모리에 인덱스 로드 (검색 전 필수)
collection.load()

print(f"컬렉션 로드 상태: {utility.load_state('documents')}")
```

---

## 검색 최적화

### 기본 검색

```python
from pymilvus import Collection

collection = Collection("documents")
collection.load()

# 쿼리 임베딩
query_embedding = [[0.1, 0.2, ..., 0.768]]  # 768차원

# 검색 수행
results = collection.search(
    data=query_embedding,
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"nprobe": 16}},
    limit=5,
    output_fields=["content", "metadata"]
)

for hits in results:
    for hit in hits:
        print(f"ID: {hit.id}, Distance: {hit.distance}")
        print(f"Content: {hit.entity.get('content')}")
```

### 검색 파라미터 최적화

```python
# nprobe: 검색할 클러스터 수 (높을수록 정확도↑, 속도↓)
search_params = {
    "metric_type": "L2",
    "params": {
        "nprobe": 32  # nlist의 5-10% 권장
    }
}

results = collection.search(
    data=query_embedding,
    anns_field="embedding",
    param=search_params,
    limit=10
)
```

**nprobe 가이드**:
- 빠른 검색: nprobe = nlist * 0.05 (5%)
- 균형: nprobe = nlist * 0.1 (10%)
- 정확도 우선: nprobe = nlist * 0.2 (20%)

### 메타데이터 필터링

```python
# 필터 표현식
filter_expr = 'metadata["category"] == "technology" and timestamp > 1696500000'

results = collection.search(
    data=query_embedding,
    anns_field="embedding",
    param=search_params,
    limit=10,
    expr=filter_expr,  # 메타데이터 필터
    output_fields=["content", "metadata", "timestamp"]
)
```

**필터 표현식 예시**:
```python
# 범위 필터
expr = "timestamp >= 1696500000 and timestamp <= 1699178400"

# 배열 포함 확인
expr = 'metadata["tags"] in ["AI", "ML", "RAG"]'

# 문자열 매칭
expr = 'content like "%RAG%"'

# 복합 조건
expr = '(category == "tech" or category == "science") and score > 0.8'
```

### 배치 검색

```python
# 여러 쿼리 동시 검색
query_embeddings = [
    [0.1, 0.2, ..., 0.768],
    [0.3, 0.4, ..., 0.768],
    [0.5, 0.6, ..., 0.768]
]

results = collection.search(
    data=query_embeddings,
    anns_field="embedding",
    param=search_params,
    limit=5
)

for idx, hits in enumerate(results):
    print(f"\n쿼리 {idx+1} 결과:")
    for hit in hits:
        print(f"  - {hit.entity.get('content')}")
```

---

## 모니터링

### Prometheus 메트릭

Milvus는 `:9091/metrics`에서 Prometheus 메트릭을 노출합니다.

```bash
# 메트릭 확인
curl http://localhost:9091/metrics
```

**주요 메트릭**:
- `milvus_querynode_sq_req_count`: 검색 요청 수
- `milvus_querynode_sq_req_latency`: 검색 지연시간
- `milvus_datanode_flush_buffer_op_count`: 플러시 작업 수
- `milvus_rootcoord_collection_num`: 컬렉션 수

### 헬스 체크

```bash
# HTTP 헬스 체크
curl http://localhost:9091/healthz
```

**응답**:
```json
{
  "status": "healthy"
}
```

### Python 모니터링

```python
from pymilvus import utility, Collection

# 서버 버전
print(f"Milvus 버전: {utility.get_server_version()}")

# 컬렉션 통계
collection = Collection("documents")
print(f"엔티티 수: {collection.num_entities}")

# 인덱스 진행률
index_info = collection.index()
print(f"인덱스 정보: {index_info.params}")

# 로드 상태
load_state = utility.load_state("documents")
print(f"로드 상태: {load_state}")
```

---

## 백업 및 복구

### 데이터 백업

```bash
#!/bin/bash
# backup_milvus.sh

BACKUP_DIR="/backups/milvus"
DATE=$(date +%Y%m%d_%H%M%S)

# Milvus 데이터 디렉토리 백업
docker-compose exec -T milvus tar czf - /var/lib/milvus \
  > $BACKUP_DIR/milvus_data_$DATE.tar.gz

# etcd 백업 (메타데이터)
docker-compose exec -T etcd etcdctl snapshot save /tmp/etcd_snapshot.db
docker-compose exec -T etcd cat /tmp/etcd_snapshot.db \
  > $BACKUP_DIR/etcd_snapshot_$DATE.db

# MinIO 백업 (벡터 파일)
docker-compose exec -T minio tar czf - /minio_data \
  > $BACKUP_DIR/minio_data_$DATE.tar.gz

echo "백업 완료: $BACKUP_DIR"
```

### 데이터 복구

```bash
#!/bin/bash
# restore_milvus.sh

BACKUP_FILE="milvus_data_20251005_140000.tar.gz"

# 서비스 중지
docker-compose stop milvus

# 데이터 복원
docker-compose exec -T milvus tar xzf - -C / < /backups/milvus/$BACKUP_FILE

# 서비스 시작
docker-compose start milvus

echo "복구 완료"
```

### 자동 백업 (Cron)

```bash
# /etc/cron.d/milvus-backup
0 2 * * * /path/to/backup_milvus.sh >> /var/log/milvus_backup.log 2>&1
```

---

## 문제 해결

### 연결 실패

**증상**: `Cannot connect to Milvus`

**해결**:
```bash
# 1. Milvus 서비스 확인
docker-compose ps milvus

# 2. 로그 확인
docker-compose logs milvus

# 3. 포트 확인
netstat -an | grep 19530

# 4. etcd/MinIO 확인
docker-compose ps etcd minio

# 5. 재시작
docker-compose restart milvus etcd minio
```

### 검색 속도 느림

**원인**: 인덱스 미생성 또는 nprobe 값 과다

**해결**:
```python
# 인덱스 확인
collection = Collection("documents")
print(collection.indexes)

# 인덱스가 없으면 생성
if not collection.indexes:
    collection.create_index(
        field_name="embedding",
        index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}}
    )

# nprobe 감소
search_params = {"metric_type": "L2", "params": {"nprobe": 16}}  # 32에서 16으로
```

### 메모리 부족

**증상**: `Out of memory`

**해결**:
```yaml
# docker-compose.yml
milvus:
  deploy:
    resources:
      limits:
        memory: 16G  # 8G에서 16G로 증가
```

또는 캐시 크기 감소:
```yaml
# milvus.yaml
queryNode:
  cacheSize: 2  # 4에서 2로 감소
```

### 삽입 실패

**증상**: `Insert failed: dimension mismatch`

**원인**: 임베딩 차원 불일치

**해결**:
```python
# 컬렉션 스키마 확인
collection = Collection("documents")
for field in collection.schema.fields:
    if field.name == "embedding":
        print(f"예상 차원: {field.params['dim']}")

# 임베딩 차원 확인
embedding = model.encode("test")
print(f"실제 차원: {len(embedding)}")

# 차원이 다르면 컬렉션 재생성 필요
```

---

## 성능 벤치마크

### 테스트 환경
- CPU: 8 코어
- RAM: 16GB
- 벡터 수: 100만
- 차원: 768
- 인덱스: IVF_FLAT (nlist=2048)

### 결과

| 작업 | 처리량 | 평균 지연시간 |
|------|--------|--------------|
| 삽입 | 10,000 벡터/초 | 100ms |
| 검색 (nprobe=16) | 500 쿼리/초 | 20ms |
| 검색 (nprobe=64) | 200 쿼리/초 | 50ms |

---

## 추가 리소스

- **공식 문서**: https://milvus.io/docs
- **API 레퍼런스**: https://milvus.io/api-reference/pymilvus/v2.3.x/About.md
- **커뮤니티**: https://github.com/milvus-io/milvus/discussions
- **Slack**: https://milvusio.slack.com

---

**버전**: Milvus 2.3.3
**마지막 업데이트**: 2025년 10월 5일
**상태**: ✅ 프로덕션 검증 완료
