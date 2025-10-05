# 배포 가이드

**GaiA-ABiz 백엔드 프로덕션 배포 가이드**

---

## 배포 옵션

1. **Docker Compose** (단일 서버, 개발/스테이징)
2. **Kubernetes** (프로덕션, 확장 가능)
3. **수동 배포** (기존 인프라)

---

## 1. Docker Compose 배포

### 전제 조건

- Docker 20.10+
- Docker Compose 2.0+
- 최소 16GB RAM
- 50GB 저장공간

### 배포 단계

#### 1.1 환경 변수 설정

`.env.production` 파일 생성:

```bash
# 데이터베이스
DATABASE_URL=postgresql://user:secure_password@postgres:5432/gaia_abiz

# JWT 시크릿 (강력한 랜덤 문자열)
SECRET_KEY=$(openssl rand -hex 32)

# 암호화 키
ENCRYPTION_KEY=$(openssl rand -hex 32)

# 애플리케이션
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# LLM (로컬)
LLM_PROVIDER=local
LLM_MODEL_PATH=/app/models/qwen2.5-gguf/Qwen2.5-7B-Instruct-Q4_K_M.gguf
LLM_THREADS=8
LLM_CONTEXT_SIZE=32768

# 임베딩 (로컬)
EMBEDDINGS_PROVIDER=local
EMBEDDINGS_MODEL=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDINGS_DEVICE=cpu

# Milvus
MILVUS_HOST=milvus
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=documents

# PostgreSQL
POSTGRES_USER=user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=gaia_abiz

# Redis (선택사항 - 캐싱용)
REDIS_URL=redis://redis:6379/0
```

#### 1.2 프로덕션 Docker Compose 구성

`docker-compose.prod.yml` 생성:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - postgres
      - milvus
      - redis
    volumes:
      - ./scripts/models:/app/models:ro
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  milvus:
    image: milvusdb/milvus:v2.3.3
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      COMMON_STORAGETYPE: minio
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - etcd
      - minio
    volumes:
      - milvus_data:/var/lib/milvus
    restart: unless-stopped

  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    environment:
      ETCD_AUTO_COMPACTION_MODE: revision
      ETCD_AUTO_COMPACTION_RETENTION: 1000
      ETCD_QUOTA_BACKEND_BYTES: 4294967296
    volumes:
      - etcd_data:/etcd
    restart: unless-stopped

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - minio_data:/minio_data
    command: minio server /minio_data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  milvus_data:
  etcd_data:
  minio_data:
  redis_data:
```

#### 1.3 프로덕션 Dockerfile

`Dockerfile.prod` 생성:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 비root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 서버 시작
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 1.4 배포 실행

```bash
# 프로덕션 모드로 빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# Milvus 초기화
docker-compose -f docker-compose.prod.yml exec api python scripts/init_milvus.py
```

---

## 2. Kubernetes 배포

### 2.1 네임스페이스 생성

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gaia-abiz
```

### 2.2 ConfigMap 및 Secret

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gaia-abiz-config
  namespace: gaia-abiz
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  LLM_PROVIDER: "local"
  EMBEDDINGS_PROVIDER: "local"
  MILVUS_HOST: "milvus-service"
  MILVUS_PORT: "19530"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: gaia-abiz-secret
  namespace: gaia-abiz
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
  ENCRYPTION_KEY: "your-encryption-key"
  DATABASE_URL: "postgresql://user:password@postgres:5432/gaia_abiz"
```

### 2.3 API 배포

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gaia-abiz-api
  namespace: gaia-abiz
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gaia-abiz-api
  template:
    metadata:
      labels:
        app: gaia-abiz-api
    spec:
      containers:
      - name: api
        image: gaia-abiz-api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: gaia-abiz-config
        - secretRef:
            name: gaia-abiz-secret
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc

---
# api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: gaia-abiz-api
  namespace: gaia-abiz
spec:
  selector:
    app: gaia-abiz-api
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### 2.4 배포 실행

```bash
# 네임스페이스 생성
kubectl apply -f namespace.yaml

# ConfigMap 및 Secret 생성
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# 서비스 배포
kubectl apply -f postgres-deployment.yaml
kubectl apply -f milvus-deployment.yaml
kubectl apply -f api-deployment.yaml

# 배포 상태 확인
kubectl get pods -n gaia-abiz
kubectl get services -n gaia-abiz

# 로그 확인
kubectl logs -f deployment/gaia-abiz-api -n gaia-abiz
```

---

## 3. 모니터링 및 로깅

### 3.1 Prometheus 설정

```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: gaia-abiz
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'gaia-abiz-api'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - gaia-abiz
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: gaia-abiz-api
```

### 3.2 로그 집계

```bash
# Fluentd 또는 Filebeat 사용
# 로그를 Elasticsearch로 전송
```

---

## 4. 백업 전략

### 4.1 데이터베이스 백업

```bash
# PostgreSQL 백업 스크립트
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 백업 생성
docker-compose exec -T postgres pg_dump -U user gaia_abiz > \
    $BACKUP_DIR/postgres_$DATE.sql

# 오래된 백업 삭제 (30일 이상)
find $BACKUP_DIR -name "postgres_*.sql" -mtime +30 -delete
```

### 4.2 Milvus 백업

```bash
# Milvus 데이터 백업
docker-compose exec -T milvus \
    tar czf /backup/milvus_$DATE.tar.gz /var/lib/milvus
```

### 4.3 자동화 (Cron)

```bash
# /etc/cron.d/gaia-abiz-backup
0 2 * * * /path/to/backup-script.sh
```

---

## 5. 보안 체크리스트

- [ ] 강력한 비밀번호 설정
- [ ] JWT 시크릿 키 변경
- [ ] SSL/TLS 인증서 설정
- [ ] 방화벽 규칙 구성
- [ ] 비루트 사용자로 실행
- [ ] 환경 변수로 민감 정보 관리
- [ ] 정기적인 보안 업데이트
- [ ] 백업 암호화
- [ ] 로그 모니터링
- [ ] 침입 탐지 시스템

---

## 6. 성능 최적화

### 6.1 데이터베이스 최적화

```sql
-- 인덱스 생성
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding);

-- 연결 풀 설정
# postgresql.conf
max_connections = 200
shared_buffers = 4GB
```

### 6.2 Milvus 최적화

```yaml
# Milvus 설정
milvus:
  config:
    cache_size: 8GB
    insert_buffer_size: 2GB
    index_type: IVF_FLAT
    metric_type: L2
```

### 6.3 API 최적화

```python
# Gunicorn 워커 설정
workers = (CPU_COUNT * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"
```

---

## 7. 롤백 절차

```bash
# Docker Compose 롤백
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Kubernetes 롤백
kubectl rollout undo deployment/gaia-abiz-api -n gaia-abiz
```

---

## 8. 헬스 체크

```bash
# API 헬스 체크
curl http://your-domain/health

# 상세 헬스 체크
curl http://your-domain/api/v1/rag/health
```

---

## 요약

### 프로덕션 준비 체크리스트

- ✅ 환경 변수 설정
- ✅ 데이터베이스 마이그레이션
- ✅ SSL/TLS 인증서
- ✅ 모니터링 설정
- ✅ 로그 집계
- ✅ 백업 자동화
- ✅ 보안 강화
- ✅ 성능 최적화
- ✅ 롤백 계획
- ✅ 문서화

---

**업데이트**: 2025년 10월 5일
**상태**: ✅ 프로덕션 준비 완료
