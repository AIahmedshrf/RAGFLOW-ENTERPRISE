# 🔧 دليل استكشاف الأخطاء وإصلاحها - RAGFlow Enterprise

## 📋 جدول المحتويات

1. [مشاكل TEI (Text Embeddings Inference)](#مشاكل-tei)
2. [مشاكل Elasticsearch](#مشاكل-elasticsearch)
3. [مشاكل Rerank](#مشاكل-rerank)
4. [مشاكل Docker Compose Profiles](#مشاكل-docker-compose-profiles)
5. [مشاكل متغيرات البيئة](#مشاكل-متغيرات-البيئة)
6. [نصائح عامة](#نصائح-عامة)

---

## 🔍 مشاكل TEI

### المشكلة 1: خدمة TEI غير معرّفة

**الخطأ:**
```
service "ragflow-cpu" depends on undefined service "tei-cpu": invalid compose project
```

**السبب:**
- خدمة `tei-cpu` مُعرّفة في `docker-compose-base.yml` لكن الـ profile الخاص بها لا يتطابق مع profile الخدمة الرئيسية.
- في الإصدار الأصلي، كان profile خدمة TEI هو `tei-cpu` بينما RAGFlow يستخدم profile `cpu`.

**الحل:**
تعديل `docker-compose-base.yml` لتوحيد الـ profiles:

```yaml
# قبل التعديل:
tei-cpu:
  profiles: [ tei-cpu ]
  
# بعد التعديل:
tei-cpu:
  profiles: [ cpu ]
```

**الأمر:**
```bash
# في docker-compose-base.yml
# غيّر profile من tei-cpu إلى cpu
# غيّر profile من tei-gpu إلى gpu
```

---

### المشكلة 2: TEI يفشل في تحميل النموذج

**الخطأ:**
```
Model not found in /data/multilingual-e5-large
```

**السبب:**
- النموذج غير موجود في المسار المحدد `/srv/models/hf/`
- أو صلاحيات المجلد غير صحيحة

**الحل:**

1. **تحقق من وجود النموذج:**
```bash
ls -lh /srv/models/hf/multilingual-e5-large/
```

2. **إذا لم يكن موجوداً، قم بتحميله:**
```bash
pip install -U "huggingface_hub[cli]"
mkdir -p /srv/models/hf
cd /srv/models/hf
huggingface-cli download intfloat/multilingual-e5-large --local-dir multilingual-e5-large
```

3. **إصلاح الصلاحيات:**
```bash
sudo chown -R $(whoami):$(whoami) /srv/models/hf/
chmod -R 755 /srv/models/hf/
```

4. **تحديث `.env`:**
```bash
HF_CACHE=/srv/models/hf
TEI_MODEL=/data/multilingual-e5-large
```

---

### المشكلة 3: TEI healthcheck يفشل

**الخطأ:**
```
Container tei-cpu is unhealthy
```

**السبب:**
بعض إصدارات TEI لا تدعم endpoint `/ready` أو `/health`

**الحل:**
تعديل healthcheck في `docker-compose-base.yml`:

```yaml
# قبل:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80/health"]
  
# بعد:
healthcheck:
  test: ["CMD-SHELL", "curl -s http://localhost:80/ >/dev/null || exit 1"]
  interval: 15s
  timeout: 5s
  retries: 30
```

---

## 🔍 مشاكل Elasticsearch

### المشكلة 1: فشل المصادقة

**الخطأ:**
```
AuthenticationException(401, 'security_exception', 'unable to authenticate user [elastic]')
```

**السبب:**
- كلمة مرور Elasticsearch في `.env` تحتوي على رموز خاصة تُفسر بشكل خاطئ
- أو كلمة المرور في `service_conf.yaml.template` صُلبة (hard-coded) ولا تستخدم متغيرات البيئة

**الحل 1: تبسيط كلمة المرور**

في `docker/.env`:
```bash
# قبل:
ELASTIC_PASSWORD=ragflow_es_ChangeMe_!23

# بعد (استخدم كلمة مرور بدون رموز خاصة):
ELASTIC_PASSWORD=ragflow_es_password123
```

**الحل 2: تحديث service_conf.yaml.template**

في `docker/service_conf.yaml.template`:
```yaml
# قبل (كلمة مرور صُلبة):
es:
  hosts: "http://elastic:ragflow_es_ChangeMe_!23@es01:9200"
  username: "elastic"
  password: "ragflow_es_ChangeMe_!23"

# بعد (استخدام متغيرات البيئة):
es:
  hosts: "http://elastic:${ELASTIC_PASSWORD:-ragflow_es_password123}@es01:9200"
  username: "elastic"
  password: "${ELASTIC_PASSWORD:-ragflow_es_password123}"
```

**الحل 3: إعادة إنشاء Elasticsearch**
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu down es01
docker volume rm docker_esdata01
docker compose --profile cpu up -d es01
```

---

### المشكلة 2: Elasticsearch healthcheck يفشل

**الخطأ:**
```
Container es01 is unhealthy
```

**السبب:**
healthcheck لا يستخدم المصادقة

**الحل:**
تحديث healthcheck في `docker-compose-base.yml`:

```yaml
# قبل:
healthcheck:
  test: ["CMD-SHELL", "curl -sf http://localhost:9200 >/dev/null || exit 1"]

# بعد:
healthcheck:
  test: ["CMD-SHELL", "curl -u elastic:${ELASTIC_PASSWORD} -sf http://localhost:9200 >/dev/null || exit 1"]
  interval: 10s
  timeout: 10s
  retries: 120
```

---

## 🔍 مشاكل Rerank

### المشكلة: خطأ hf_transfer

**الخطأ:**
```
ValueError: Fast download using 'hf_transfer' is enabled but 'hf_transfer' package is not available
```

**السبب:**
متغير البيئة `HF_HUB_ENABLE_HF_TRANSFER=1` مُفعّل لكن المكتبة `hf_transfer` غير مثبتة

**الحل:**

1. **إزالة المتغير من Dockerfile:**

في `docker/rerank/Dockerfile`:
```dockerfile
# قبل:
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 HF_HUB_ENABLE_HF_TRANSFER=1

# بعد:
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
```

2. **إزالة المتغير من docker-compose-base.yml:**

```yaml
# قبل:
rerank:
  environment:
    - RERANK_MODEL=${RERANK_MODEL_ID}
    - HF_HUB_ENABLE_HF_TRANSFER=1

# بعد:
rerank:
  environment:
    - RERANK_MODEL=${RERANK_MODEL_ID}
```

3. **إعادة البناء والتشغيل:**
```bash
docker compose --profile cpu stop rerank
docker compose --profile cpu rm -f rerank
docker compose --profile cpu build rerank
docker compose --profile cpu up -d rerank
```

---

## 🔍 مشاكل Docker Compose Profiles

### المشكلة: الخدمات الأساسية غير متاحة

**الخطأ:**
```
service "ragflow-cpu" depends on undefined service "mysql": invalid compose project
```

**السبب:**
الخدمات الأساسية (MySQL, Redis, Elasticsearch, MinIO) ليس لديها profiles مناسبة

**الحل:**
إضافة profiles لجميع الخدمات الأساسية في `docker-compose-base.yml`:

```yaml
mysql:
  profiles: [ cpu, gpu ]
  image: mysql:8.0.39
  # ...

redis:
  profiles: [ cpu, gpu ]
  image: valkey/valkey:8
  # ...

minio:
  profiles: [ cpu, gpu ]
  image: quay.io/minio/minio:...
  # ...

es01:
  profiles: [ cpu, gpu, elasticsearch ]
  image: elasticsearch:${STACK_VERSION}
  # ...

rerank:
  profiles: [ cpu, gpu ]
  build:
    context: ./rerank
  # ...

tei-cpu:
  profiles: [ cpu ]
  # ...

tei-gpu:
  profiles: [ gpu ]
  # ...
```

---

## 🔍 مشاكل متغيرات البيئة

### المشكلة: COMPOSE_PROFILES غير محدد

**الخطأ:**
لا تظهر الخدمات عند تشغيل `docker compose ps`

**السبب:**
متغير `COMPOSE_PROFILES` غير محدد في `.env`

**الحل:**
إضافة في `docker/.env`:

```bash
# في أول الملف أو بعد RAGFLOW_IMAGE
COMPOSE_PROFILES=cpu
```

للتشغيل على GPU:
```bash
COMPOSE_PROFILES=gpu
```

---

### المشكلة: كلمات المرور غير متطابقة

**الخطأ:**
```
Access denied for user 'root'@'...'
```

**السبب:**
كلمات المرور في `.env` لا تتطابق مع تلك المُعرّفة في `service_conf.yaml.template`

**الحل:**
استخدام متغيرات البيئة في جميع ملفات التكوين:

**في `service_conf.yaml.template`:**
```yaml
mysql:
  password: '${MYSQL_PASSWORD:-ragflow_root_ChangeMe_!23}'

minio:
  password: "${MINIO_PASSWORD:-ragflow_minio_ChangeMe_!23}"

es:
  password: "${ELASTIC_PASSWORD:-ragflow_es_password123}"

redis:
  password: "${REDIS_PASSWORD:-ragflow_redis_ChangeMe_123}"
```

**في `docker/.env`:**
```bash
MYSQL_PASSWORD=ragflow_root_ChangeMe_!23
MINIO_PASSWORD=ragflow_minio_ChangeMe_!23
ELASTIC_PASSWORD=ragflow_es_password123
REDIS_PASSWORD=ragflow_redis_ChangeMe_123
```

---

## 🔍 نصائح عامة

### 1. التحقق من حالة الخدمات

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu ps
```

### 2. عرض السجلات

```bash
# سجلات خدمة معينة
docker logs docker-ragflow-cpu-1 -f

# آخر 100 سطر
docker logs docker-ragflow-cpu-1 --tail 100

# سجلات مع الطوابع الزمنية
docker logs docker-ragflow-cpu-1 --timestamps
```

### 3. إعادة تشغيل خدمة معينة

```bash
docker compose --profile cpu restart ragflow-cpu
```

### 4. إعادة بناء الصور

```bash
# إعادة بناء صورة معينة
docker compose --profile cpu build rerank

# إعادة بناء جميع الصور
docker compose --profile cpu build --no-cache
```

### 5. تنظيف النظام

```bash
# إيقاف وإزالة جميع الحاويات
docker compose --profile cpu down

# إزالة volumes أيضاً (احذر - سيحذف البيانات!)
docker compose --profile cpu down -v

# تنظيف الموارد غير المستخدمة
docker system prune -f
```

### 6. اختبار الاتصال

```bash
# اختبار TEI
curl -X POST http://localhost:6380/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test"}'

# اختبار Elasticsearch
curl -u elastic:ragflow_es_password123 http://localhost:1200

# اختبار RAGFlow
curl http://localhost:8080
```

### 7. مراقبة استخدام الموارد

```bash
# عرض استخدام الموارد
docker stats

# مراقبة مستمرة
watch -n 2 docker stats --no-stream
```

### 8. التحقق من التكوين

```bash
# عرض التكوين النهائي
docker compose --profile cpu config

# حفظه في ملف
docker compose --profile cpu config > /tmp/final-config.yml
```

---

## 📊 جدول الأخطاء الشائعة وحلولها السريعة

| الخطأ | الحل السريع |
|-------|-------------|
| `service depends on undefined service` | أضف profiles للخدمات في docker-compose-base.yml |
| `Authentication failed` | تحقق من كلمات المرور في .env و service_conf.yaml.template |
| `Container is unhealthy` | راجع healthcheck في docker-compose-base.yml |
| `Model not found` | تحقق من HF_CACHE و TEI_MODEL في .env |
| `hf_transfer not available` | أزل HF_HUB_ENABLE_HF_TRANSFER من Dockerfile |
| `Port already in use` | غيّر المنفذ في .env أو أوقف الخدمة المتعارضة |
| `No space left on device` | نظّف Docker: `docker system prune -af --volumes` |
| `Unable to resolve host` | تحقق من أسماء الخدمات في docker-compose.yml |

---

## 🎯 خطوات التشخيص المنهجية

عند مواجهة مشكلة، اتبع هذه الخطوات:

1. **تحقق من حالة الحاويات:**
   ```bash
   docker compose --profile cpu ps
   ```

2. **اقرأ السجلات:**
   ```bash
   docker logs <container-name> --tail 100
   ```

3. **تحقق من healthcheck:**
   ```bash
   docker inspect <container-name> | grep -A 10 Health
   ```

4. **اختبر الاتصال الداخلي:**
   ```bash
   docker exec <container-name> curl -v http://target-service:port
   ```

5. **تحقق من متغيرات البيئة:**
   ```bash
   docker exec <container-name> env | grep VARIABLE_NAME
   ```

6. **راجع التكوين:**
   ```bash
   docker compose --profile cpu config | grep -A 5 service-name
   ```

---

## 📝 ملاحظات مهمة

1. **كلمات المرور:** لا تستخدم رموزاً خاصة معقدة في البيئة الإنتاجية إلا مع escape صحيح
2. **Profiles:** تأكد من تطابق profiles بين docker-compose.yml و docker-compose-base.yml
3. **Volumes:** احذر من حذف volumes لأنها تحتوي على البيانات
4. **النماذج:** تأكد من تحميل النماذج قبل التشغيل لتوفير الوقت
5. **الذاكرة:** راقب استخدام الذاكرة، خصوصاً مع Elasticsearch و TEI

---

## 🔗 موارد إضافية

- **مستودع RAGFlow الأصلي:** https://github.com/infiniflow/ragflow
- **توثيق TEI:** https://github.com/huggingface/text-embeddings-inference
- **توثيق Docker Compose:** https://docs.docker.com/compose/
- **Elasticsearch Troubleshooting:** https://www.elastic.co/guide/en/elasticsearch/reference/current/troubleshooting.html

---

**تاريخ التحديث:** 2025-11-17  
**الإصدار:** RAGFlow v0.21.1-slim  
**المساهم:** AI Development Team
