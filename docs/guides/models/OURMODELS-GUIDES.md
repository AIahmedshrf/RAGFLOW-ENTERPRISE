# دليل النماذج المحلية - RAGFlow Enterprise

## 📋 نظرة عامة

تم تكوين RAGFlow Enterprise للعمل مع نماذج محلية بدون الحاجة لخدمات سحابية خارجية. يشمل هذا:

1. **نماذج التضمين (Embedding Models)** - لتحويل النصوص إلى vectors
2. **نماذج المحادثة (Chat/LLM Models)** - للإجابة على الأسئلة
3. **نماذج إعادة الترتيب (Rerank Models)** - لتحسين دقة نتائج البحث

---

## 🎯 النماذج المُكونة

### 1. نماذج التضمين (Embedding Models)

#### 🟣 multilingual-e5-large (عبر TEI)

**الوصف:** نموذج تضمين متعدد اللغات يدعم 100+ لغة بما فيها العربية والإنجليزية

**المواصفات:**
- **Max Tokens:** 512
- **حجم Vector:** 1024 dimension
- **الخدمة:** Text Embeddings Inference (TEI) من HuggingFace
- **البروتوكول:** OpenAI-API-Compatible
- **المنفذ:** 6380

**كيف تم التكوين:**
1. تم إضافة خدمة TEI في `docker-compose-base.yml`:
   ```yaml
   tei:
     profiles: [ cpu, gpu ]
     image: ghcr.io/huggingface/text-embeddings-inference:cpu-1.7.2
     command: --model-id /data/multilingual-e5-large --port 80
     ports:
       - "6380:80"
     volumes:
       - ${HF_CACHE}:/data
   ```

2. تم تنزيل النموذج محلياً في `/srv/models/hf/multilingual-e5-large`

3. تم تكوينه في RAGFlow عبر الواجهة:
   - **Provider:** OpenAI-API-Compatible
   - **Model name:** multilingual-e5-large
   - **Base URL:** http://tei:80
   - **API Key:** dummy
   - **Model Type:** TEXT_EMBEDDING
   - **Max Tokens:** 512

**الاستخدام:**
- ممتاز للمستندات متعددة اللغات (عربي + إنجليزي)
- يقوم RAGFlow تلقائياً بتقسيم النصوص الطويلة إلى chunks أصغر من 512 token
- يُستخدم تلقائياً عند إنشاء Knowledge Base

---

#### 🟢 bge-m3 (عبر Ollama)

**الوصف:** نموذج تضمين صيني متقدم يدعم اللغات المتعددة

**المواصفات:**
- **Max Tokens:** 8192
- **حجم Vector:** 1024 dimension
- **الخدمة:** Ollama
- **الحجم:** 1.2 GB

**كيف تم التكوين:**
1. تم تنزيل النموذج عبر Ollama:
   ```bash
   ollama pull bge-m3
   ```

2. تم إضافته في RAGFlow عبر الواجهة:
   - **Provider:** Ollama
   - **Model name:** bge-m3
   - **Model Type:** TEXT_EMBEDDING
   - **Max Tokens:** 8192

**الاستخدام:**
- يدعم نصوص أطول (8192 token)
- ممتاز للمستندات الطويلة
- أداء جيد مع اللغة الصينية والعربية

---

#### 🔵 nomic-embed-text (عبر Ollama)

**الوصف:** نموذج تضمين خفيف وسريع

**المواصفات:**
- **Max Tokens:** 8192
- **حجم Vector:** 768 dimension
- **الخدمة:** Ollama
- **الحجم:** 274 MB

**كيف تم التكوين:**
1. تم تنزيله عبر Ollama:
   ```bash
   ollama pull nomic-embed-text
   ```

2. تم إضافته في RAGFlow عبر الواجهة:
   - **Provider:** Ollama
   - **Model name:** nomic-embed-text
   - **Model Type:** TEXT_EMBEDDING
   - **Max Tokens:** 8192

**الاستخدام:**
- سريع وخفيف على الموارد
- جيد للنصوص الإنجليزية
- أداء متوسط مع اللغة العربية

---

### 2. نماذج المحادثة (Chat Models)

#### 🔴 qwen2:7b-instruct (عبر Ollama)

**الوصف:** نموذج محادثة صيني متقدم من Alibaba

**المواصفات:**
- **Context Window:** 32768 tokens
- **Max Output Tokens:** 4096 (موصى به)
- **الخدمة:** Ollama
- **الحجم:** 4.4 GB
- **Parameters:** 7 billion

**كيف تم التكوين:**
1. تم تنزيله عبر Ollama:
   ```bash
   ollama pull qwen2:7b-instruct
   ```

2. تم إضافته في RAGFlow:
   - **Provider:** Ollama
   - **Model name:** qwen2:7b-instruct
   - **Model Type:** CHAT
   - **Max Tokens:** 4096

**الاستخدام:**
- ممتاز للإجابة على الأسئلة المعقدة
- يدعم العربية والإنجليزية والصينية
- context window كبير (32K) يتيح استخدام معلومات كثيرة من المستندات

---

#### 🟠 llama3:8b (عبر Ollama)

**الوصف:** نموذج Meta الشهير للمحادثة

**المواصفات:**
- **Context Window:** 8192 tokens
- **Max Output Tokens:** 2048 (موصى به)
- **الخدمة:** Ollama
- **الحجم:** 4.7 GB
- **Parameters:** 8 billion

**كيف تم التكوين:**
1. تم تنزيله مسبقاً:
   ```bash
   ollama pull llama3:8b
   ```

2. يمكن إضافته في RAGFlow:
   - **Provider:** Ollama
   - **Model name:** llama3:8b
   - **Model Type:** CHAT
   - **Max Tokens:** 2048

**الاستخدام:**
- أداء ممتاز مع اللغة الإنجليزية
- أداء جيد مع اللغة العربية
- موثوق وسريع

---

#### 🟡 qwen2.5:0.5b (عبر Ollama)

**الوصف:** نموذج محادثة صغير وسريع جداً

**المواصفات:**
- **Context Window:** 32768 tokens
- **Max Output Tokens:** 2048 (موصى به)
- **الخدمة:** Ollama
- **الحجم:** 397 MB
- **Parameters:** 500 million

**الاستخدام:**
- خفيف جداً على الموارد
- سريع في الاستجابة
- مناسب للأسئلة البسيطة

---

### 3. نماذج إعادة الترتيب (Rerank Models)

#### 🟣 BAAI/bge-reranker-v2-m3 (محلي)

**الوصف:** نموذج إعادة ترتيب متقدم لتحسين دقة نتائج البحث

**المواصفات:**
- **Max Tokens:** 8192
- **الخدمة:** Python FastAPI محلي
- **المنفذ:** 8000
- **البروتوكول:** OpenAI-compatible

**كيف تم التكوين:**

#### 🔧 الخطوات التقنية:

**1. إنشاء Dockerfile للخدمة:**

تم إنشاء `docker/rerank/Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install torch transformers sentence-transformers fastapi uvicorn
COPY app.py /app/
ENV RERANK_MODEL=BAAI/bge-reranker-v2-m3
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. إنشاء API Server:**

تم إنشاء `docker/rerank/app.py` مع endpoints:
- `GET /v1/health` - للتحقق من صحة الخدمة
- `POST /v1/rerank` - لإعادة ترتيب النتائج

**3. إضافة الخدمة في docker-compose-base.yml:**

```yaml
rerank:
  profiles: [ cpu, gpu ]
  build:
    context: ./rerank
  image: local-reranker:latest
  container_name: docker-rerank-1
  ports:
    - "8000:8000"  # ← تم إضافة هذا لنشر المنفذ
  environment:
    - RERANK_MODEL=BAAI/bge-reranker-v2-m3
  networks: [ ragflow ]
  healthcheck:
    test: ["CMD-SHELL", "python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/v1/health\")' || exit 1"]
    interval: 15s
    timeout: 5s
    retries: 30
  restart: on-failure
```

**التغييرات المهمة:**
- ✅ إضافة `ports: - "8000:8000"` لنشر المنفذ
- ✅ تحديث healthcheck ليستخدم Python بدلاً من curl (غير متوفر في الصورة)
- ✅ تم حذف `HF_HUB_ENABLE_HF_TRANSFER=1` لتجنب أخطاء المكتبات المفقودة

**4. بناء وتشغيل الخدمة:**

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu build rerank
docker compose --profile cpu up -d rerank
```

**5. التحقق من تشغيل الخدمة:**

```bash
# فحص حالة الخدمة
docker ps --filter "name=rerank"

# اختبار API
curl http://localhost:8000/v1/health
# الناتج: {"status":"ok","model":"BAAI/bge-reranker-v2-m3"}
```

**6. إضافة النموذج في RAGFlow:**

عبر الواجهة: **Model Providers → OpenAI-API-Compatible → Add Model**

```yaml
Provider: OpenAI-API-Compatible
Model name: BAAI/bge-reranker-v2-m3
Base URL: http://rerank:8000
API Key: dummy  (أو فارغ)
Model Type: RERANK
Max Tokens: 8192
```

**📌 ملاحظة مهمة:**
- من **داخل Docker network**: استخدم `http://rerank:8000`
- من **خارج Docker** (للاختبار): استخدم `http://localhost:8000`

**الاستخدام:**
- يعمل تلقائياً في الخلفية عند استخدام RAGFlow
- يعيد ترتيب النتائج المسترجعة لتحسين الدقة
- يظهر في **Set default models** بعد إضافته من Model Providers

**اختبار يدوي:**

```bash
curl -X POST http://localhost:8000/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "ما هو التعلم العميق؟",
    "documents": [
      "التعلم العميق هو فرع من الذكاء الاصطناعي",
      "البيتزا طعام لذيذ",
      "الشبكات العصبية تستخدم في التعلم العميق"
    ]
  }'
```

---

## 🚀 خطوات الإعداد الكاملة

### 1. تثبيت Ollama ونماذجه

```bash
# تثبيت Ollama
curl -fsSL https://ollama.com/install.sh | sh

# تنزيل نماذج Embedding
ollama pull bge-m3
ollama pull nomic-embed-text

# تنزيل نماذج Chat
ollama pull qwen2:7b-instruct
ollama pull llama3:8b
ollama pull qwen2.5:0.5b

# التحقق من النماذج
ollama list
```

### 2. تنزيل نموذج multilingual-e5-large

```bash
# تثبيت huggingface-cli
pip install huggingface-hub

# تنزيل النموذج
huggingface-cli download intfloat/multilingual-e5-large \
  --local-dir /srv/models/hf/multilingual-e5-large \
  --local-dir-use-symlinks False
```

### 3. تشغيل RAGFlow مع جميع الخدمات

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker

# تشغيل جميع الخدمات
docker compose --profile cpu up -d

# التحقق من الخدمات
docker compose ps
```

### 4. إضافة النماذج عبر واجهة RAGFlow

1. افتح المتصفح: http://localhost:8080
2. اذهب إلى **User Settings → Model Providers**
3. أضف كل نموذج حسب الجداول أعلاه

---

## 📊 مقارنة النماذج

### نماذج التضمين (Embedding)

| النموذج | Max Tokens | حجم Vector | اللغات | الحجم | السرعة | الدقة |
|---------|-----------|-----------|--------|-------|--------|-------|
| multilingual-e5-large | 512 | 1024 | 100+ | - | متوسط | ⭐⭐⭐⭐⭐ |
| bge-m3 | 8192 | 1024 | متعدد | 1.2GB | سريع | ⭐⭐⭐⭐⭐ |
| nomic-embed-text | 8192 | 768 | EN | 274MB | سريع جداً | ⭐⭐⭐⭐ |

### نماذج المحادثة (Chat)

| النموذج | Context | Max Output | الحجم | اللغات | الأداء |
|---------|---------|-----------|-------|--------|--------|
| qwen2:7b-instruct | 32K | 4096 | 4.4GB | متعدد | ⭐⭐⭐⭐⭐ |
| llama3:8b | 8K | 2048 | 4.7GB | EN/AR | ⭐⭐⭐⭐⭐ |
| qwen2.5:0.5b | 32K | 2048 | 397MB | متعدد | ⭐⭐⭐ |

---

## 🔍 استكشاف الأخطاء

### خدمة TEI لا تعمل

```bash
# فحص السجلات
docker logs docker-tei-cpu-1

# إعادة التشغيل
docker compose --profile cpu restart tei
```

### خدمة Rerank unhealthy

```bash
# فحص الحالة
docker ps --filter "name=rerank"

# اختبار API
curl http://localhost:8000/v1/health

# إعادة البناء والتشغيل
docker compose --profile cpu build rerank
docker compose --profile cpu up -d rerank
```

### Ollama لا يستجيب

```bash
# إعادة تشغيل Ollama
systemctl restart ollama

# فحص الحالة
ollama list
```

---

## 📝 ملاحظات مهمة

1. **Max Tokens للـ Embedding Models:**
   - هو حد النص المُدخل للتضمين
   - RAGFlow يقسّم النصوص تلقائياً إذا تجاوزت الحد

2. **Max Tokens للـ Chat Models:**
   - Context Window: كم يمكن للنموذج قراءته
   - Max Output: كم يمكن للنموذج كتابته في الإجابة

3. **Rerank Model:**
   - يعمل تلقائياً في الخلفية
   - لا يحتاج إعدادات إضافية بعد إضافته

4. **النماذج المحلية:**
   - جميع النماذج تعمل محلياً (offline)
   - لا تحتاج إلى اتصال بالإنترنت بعد التنزيل
   - لا توجد تكاليف API

---

## 🎯 التوصيات

**للاستخدام اليومي:**
- **Embedding:** multilingual-e5-large (للدقة) أو bge-m3 (للنصوص الطويلة)
- **Chat:** qwen2:7b-instruct (الأفضل للغة العربية)
- **Rerank:** BAAI/bge-reranker-v2-m3 (ضروري لتحسين الدقة)

**للاختبار السريع:**
- **Embedding:** nomic-embed-text
- **Chat:** qwen2.5:0.5b

---

## 📞 الدعم

للمزيد من المعلومات:
- **RAGFlow Docs:** https://ragflow.io/docs
- **HuggingFace TEI:** https://github.com/huggingface/text-embeddings-inference
- **Ollama:** https://ollama.com/library

---

**تم التكوين بواسطة:** GitHub Copilot  
**التاريخ:** 18 نوفمبر 2025  
**النسخة:** RAGFlow v0.21.1-slim
