# Deployment Guide

## 배포 환경

- **로컬 개발**: Docker Compose
- **프로덕션**: Kubernetes (K8s)
- **클라우드**: AWS/Azure/GCP 호환

---

## 로컬 개발 환경 (Docker Compose)

### 사전 요구사항

- Docker Desktop 설치
- Docker Compose v2.0+
- 8GB+ RAM
- 20GB+ 디스크 공간

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd gaia-abiz-backend
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:
```bash
# 필수 변경 항목
DATABASE_URL=postgresql://user:password@postgres:5432/gaia_abiz
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-32-byte-encryption-key-here-change-this
OPENAI_API_KEY=sk-your-openai-api-key

# 선택 변경 항목
OAUTH2_CLIENT_ID=your-oauth2-client-id
OAUTH2_CLIENT_SECRET=your-oauth2-client-secret
```

### 3. 서비스 시작

```bash
# 백그라운드에서 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 특정 서비스만 재시작
docker-compose restart api
```

### 4. 헬스 체크

```bash
# API 상태 확인
curl http://localhost:8000/health

# 데이터베이스 연결 확인
curl http://localhost:8000/monitoring/health
```

### 5. API 문서 접속

브라우저에서 접속:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. 서비스 중지

```bash
# 모든 서비스 중지 (데이터 유지)
docker-compose stop

# 모든 서비스 제거 (데이터 포함)
docker-compose down -v
```

---

## 프로덕션 배포 (Kubernetes)

### 사전 요구사항

- Kubernetes 클러스터 (1.24+)
- kubectl CLI 도구
- Helm 3.0+ (선택사항)
- 도메인 및 SSL 인증서

### 1. Docker 이미지 빌드 및 푸시

```bash
# 이미지 빌드
docker build -t your-registry/gaia-abiz-backend:latest .

# 레지스트리에 푸시
docker push your-registry/gaia-abiz-backend:latest
```

### 2. Namespace 생성

```bash
kubectl apply -f k8s/namespace.yaml
```

**파일 내용** (`k8s/namespace.yaml`):
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gaia-abiz
  labels:
    name: gaia-abiz
```

### 3. Secrets 설정

```bash
# secrets.yaml.example 복사
cp k8s/secrets.yaml.example k8s/secrets.yaml

# secrets.yaml 편집 (실제 값으로 변경)
vi k8s/secrets.yaml

# Secrets 적용
kubectl apply -f k8s/secrets.yaml
```

**중요**: `secrets.yaml`은 git에 커밋하지 마세요!

**Secret 값 예시**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gaia-abiz-secrets
  namespace: gaia-abiz
type: Opaque
stringData:
  database-url: "postgresql://user:password@postgres-service:5432/gaia_abiz"
  secret-key: "production-secret-key-very-long-and-random"
  encryption-key: "production-encryption-key-32-bytes-minimum-length"
  openai-api-key: "sk-proj-xxxxxxxxxxxxxxxxxxxxx"
  oauth2-client-id: "your-prod-oauth2-client-id"
  oauth2-client-secret: "your-prod-oauth2-client-secret"
  oauth2-redirect-uri: "https://api.yourdomain.com/auth/callback"
```

### 4. ConfigMap 적용

```bash
kubectl apply -f k8s/configmap.yaml
```

필요시 ConfigMap 수정:
```bash
kubectl edit configmap gaia-abiz-config -n gaia-abiz
```

### 5. PostgreSQL 배포 (옵션)

**외부 PostgreSQL 사용 권장** (AWS RDS, Azure Database, Google Cloud SQL)

내부 배포시:
```bash
# Persistent Volume 생성
kubectl apply -f k8s/postgres-pv.yaml

# PostgreSQL Deployment
kubectl apply -f k8s/postgres-deployment.yaml
```

### 6. Milvus 배포

```bash
# Helm으로 Milvus 설치 (권장)
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm install milvus milvus/milvus -n gaia-abiz

# 또는 manifest 사용
kubectl apply -f k8s/milvus-deployment.yaml
```

### 7. Application 배포

```bash
# Deployment 적용
kubectl apply -f k8s/deployment.yaml

# 배포 상태 확인
kubectl rollout status deployment/gaia-abiz-backend -n gaia-abiz

# Pod 상태 확인
kubectl get pods -n gaia-abiz

# 로그 확인
kubectl logs -f deployment/gaia-abiz-backend -n gaia-abiz
```

### 8. Service 배포

```bash
kubectl apply -f k8s/service.yaml

# Service 확인
kubectl get svc -n gaia-abiz
```

### 9. Ingress 설정

```bash
# Ingress Controller 설치 (NGINX)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Ingress 적용
kubectl apply -f k8s/ingress.yaml

# Ingress 상태 확인
kubectl get ingress -n gaia-abiz
```

**도메인 설정**: Ingress의 External IP를 도메인에 연결

### 10. HPA (Auto Scaling) 설정

```bash
# Metrics Server 설치 (없는 경우)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# HPA 적용
kubectl apply -f k8s/hpa.yaml

# HPA 상태 확인
kubectl get hpa -n gaia-abiz
```

### 11. SSL 인증서 설정 (Let's Encrypt)

```bash
# cert-manager 설치
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# ClusterIssuer 생성
kubectl apply -f k8s/cert-issuer.yaml

# Ingress에 자동으로 인증서 발급됨
```

---

## 배포 확인

### 1. Pod 상태 확인

```bash
kubectl get pods -n gaia-abiz
```

예상 출력:
```
NAME                                  READY   STATUS    RESTARTS   AGE
gaia-abiz-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
gaia-abiz-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
gaia-abiz-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          5m
```

### 2. Service 확인

```bash
kubectl get svc -n gaia-abiz
```

### 3. Ingress 확인

```bash
kubectl describe ingress gaia-abiz-ingress -n gaia-abiz
```

### 4. 로그 확인

```bash
# 실시간 로그
kubectl logs -f deployment/gaia-abiz-backend -n gaia-abiz

# 최근 100줄
kubectl logs --tail=100 deployment/gaia-abiz-backend -n gaia-abiz

# 에러만 필터링
kubectl logs deployment/gaia-abiz-backend -n gaia-abiz | grep ERROR
```

### 5. API 테스트

```bash
# Health check
curl https://api.yourdomain.com/health

# API 문서
curl https://api.yourdomain.com/docs
```

---

## 롤링 업데이트

### 1. 새 이미지 빌드 및 푸시

```bash
# 이미지 빌드 (새 버전)
docker build -t your-registry/gaia-abiz-backend:v1.1.0 .

# 푸시
docker push your-registry/gaia-abiz-backend:v1.1.0
```

### 2. Deployment 업데이트

```bash
# 이미지 업데이트
kubectl set image deployment/gaia-abiz-backend \
  api=your-registry/gaia-abiz-backend:v1.1.0 \
  -n gaia-abiz

# 롤아웃 상태 확인
kubectl rollout status deployment/gaia-abiz-backend -n gaia-abiz
```

### 3. 롤백 (필요시)

```bash
# 이전 버전으로 롤백
kubectl rollout undo deployment/gaia-abiz-backend -n gaia-abiz

# 특정 revision으로 롤백
kubectl rollout undo deployment/gaia-abiz-backend --to-revision=2 -n gaia-abiz

# Rollout 히스토리 확인
kubectl rollout history deployment/gaia-abiz-backend -n gaia-abiz
```

---

## 모니터링 설정

### Prometheus & Grafana

#### 1. Prometheus Operator 설치

```bash
# Helm으로 설치
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

#### 2. ServiceMonitor 생성

```bash
kubectl apply -f k8s/servicemonitor.yaml
```

**파일 내용** (`k8s/servicemonitor.yaml`):
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: gaia-abiz-backend
  namespace: gaia-abiz
spec:
  selector:
    matchLabels:
      app: gaia-abiz-backend
  endpoints:
  - port: metrics
    interval: 30s
```

#### 3. Grafana 대시보드 접속

```bash
# Grafana 포트 포워딩
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 브라우저에서 접속
# http://localhost:3000
# 기본 로그인: admin / prom-operator
```

### ELK Stack (로그 수집)

#### 1. Elasticsearch & Kibana 설치

```bash
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n logging --create-namespace
helm install kibana elastic/kibana -n logging
```

#### 2. Filebeat 설정

```bash
kubectl apply -f k8s/filebeat-daemonset.yaml
```

---

## 백업 및 복구

### 데이터베이스 백업

```bash
# PostgreSQL 백업
kubectl exec -n gaia-abiz <postgres-pod> -- \
  pg_dump -U user gaia_abiz > backup_$(date +%Y%m%d).sql

# 복구
kubectl exec -i -n gaia-abiz <postgres-pod> -- \
  psql -U user gaia_abiz < backup_20251001.sql
```

### Milvus 백업

```bash
# Milvus 데이터는 PVC에 저장됨
# PVC 스냅샷 생성
kubectl get pvc -n gaia-abiz
```

---

## 트러블슈팅

### Pod가 시작되지 않을 때

```bash
# Pod 상태 확인
kubectl describe pod <pod-name> -n gaia-abiz

# 이벤트 확인
kubectl get events -n gaia-abiz --sort-by='.lastTimestamp'

# 로그 확인
kubectl logs <pod-name> -n gaia-abiz
```

### 데이터베이스 연결 실패

```bash
# Secret 확인
kubectl get secret gaia-abiz-secrets -n gaia-abiz -o yaml

# Service DNS 테스트
kubectl run -it --rm debug --image=busybox --restart=Never -n gaia-abiz -- \
  nslookup postgres-service
```

### 메모리 부족

```bash
# 리소스 사용량 확인
kubectl top pods -n gaia-abiz

# Limits 증가
kubectl edit deployment gaia-abiz-backend -n gaia-abiz
# resources.limits.memory 값 증가
```

### 이미지 Pull 실패

```bash
# ImagePullSecrets 생성
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry> \
  --docker-username=<username> \
  --docker-password=<password> \
  -n gaia-abiz

# Deployment에 추가
kubectl patch deployment gaia-abiz-backend -n gaia-abiz \
  -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"regcred"}]}}}}'
```

---

## 보안 권장사항

### 1. Network Policies

```bash
kubectl apply -f k8s/network-policy.yaml
```

### 2. Pod Security Standards

```yaml
# Deployment에 추가
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
      - ALL
```

### 3. RBAC 설정

```bash
kubectl apply -f k8s/rbac.yaml
```

### 4. Secrets 암호화

Kubernetes Secrets는 기본적으로 base64 인코딩만 됨.
추가 암호화 필요시:
- AWS KMS
- Azure Key Vault
- Google Cloud KMS
- HashiCorp Vault

---

## 성능 최적화

### 1. Resource Limits 최적화

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### 2. HPA 설정 최적화

```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 3. Connection Pool 튜닝

`.env` 파일:
```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

---

## CI/CD 파이프라인

### GitHub Actions 예시

`.github/workflows/deploy.yml`:
```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t ${{ secrets.DOCKER_REGISTRY }}/gaia-abiz-backend:${{ github.sha }} .

      - name: Push to registry
        run: docker push ${{ secrets.DOCKER_REGISTRY }}/gaia-abiz-backend:${{ github.sha }}

      - name: Deploy to K8s
        run: |
          kubectl set image deployment/gaia-abiz-backend \
            api=${{ secrets.DOCKER_REGISTRY }}/gaia-abiz-backend:${{ github.sha }} \
            -n gaia-abiz
```

---

## 체크리스트

배포 전 확인사항:

- [ ] 환경 변수 모두 설정됨
- [ ] Secrets 생성 및 적용
- [ ] 데이터베이스 마이그레이션 완료
- [ ] SSL 인증서 설정
- [ ] 도메인 DNS 설정
- [ ] 모니터링 설정
- [ ] 백업 전략 수립
- [ ] 롤백 계획 수립
- [ ] 로드 테스트 완료
- [ ] 보안 점검 완료
