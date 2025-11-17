# 🚀 معلومات تشغيل RAGFlow Enterprise

## ✅ حالة النظام
تم تشغيل RAGFlow بنجاح! جميع الخدمات تعمل.

## 🌐 الوصول إلى النظام

### واجهة المستخدم الرئيسية
**URL:** `http://YOUR_SERVER_IP:8080`

**بيانات الدخول الافتراضية:**
- البريد الإلكتروني: `admin@ragflow.io`
- كلمة المرور: `admin`

**⚠️ مهم:** قم بتغيير كلمة المرور بعد أول تسجيل دخول!

---

## 📊 الخدمات المشتغلة

| الخدمة | المنفذ | الحالة | الوصف |
|--------|--------|--------|-------|
| RAGFlow UI | 8080 | ✅ يعمل | الواجهة الرئيسية |
| RAGFlow API | 9380 | ✅ يعمل | API الداخلي |
| TEI Embeddings | 6380 | ✅ يعمل | خدمة التضمينات |
| Elasticsearch | 1200 | ✅ يعمل | قاعدة بيانات البحث |
| MySQL | 5455 | ✅ يعمل | قاعدة البيانات |
| Redis | 6379 | ✅ يعمل | الذاكرة المؤقتة |
| MinIO | 9000 | ✅ يعمل | تخزين الملفات |
| MinIO Console | 9001 | ✅ يعمل | لوحة تحكم MinIO |
| Rerank | 8000 | ⚠️ داخلي | إعادة ترتيب النتائج |

---

## 🔧 الأوامر المفيدة

### عرض حالة الخدمات
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu ps
```

### عرض السجلات
```bash
# سجلات RAGFlow
docker logs docker-ragflow-cpu-1 -f

# سجلات TEI
docker logs docker-tei-cpu-1 -f

# سجلات Elasticsearch
docker logs docker-es01-1 -f
```

### مراقبة النظام
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
./monitor_ragflow.sh
```

### إيقاف النظام
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu down
```

### إعادة تشغيل النظام
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu up -d
```

### إعادة تشغيل خدمة معينة
```bash
# مثال: إعادة تشغيل RAGFlow
docker compose --profile cpu restart ragflow-cpu
```

---

## 📁 النماذج المستخدمة

### نماذج Embedding
- **الموقع:** `/srv/models/hf/multilingual-e5-large`
- **النموذج:** `intfloat/multilingual-e5-large`
- **الخدمة:** TEI (Text Embeddings Inference)

### نماذج Ollama
```bash
ollama list
```

---

## 🔐 كلمات المرور

### Elasticsearch
- **المستخدم:** `elastic`
- **كلمة المرور:** `ragflow_es_password123`

### MySQL
- **المستخدم:** `root`
- **كلمة المرور:** `ragflow_root_ChangeMe_!23`

### Redis
- **كلمة المرور:** `ragflow_redis_ChangeMe_123`

### MinIO
- **المستخدم:** `rag_flow`
- **كلمة المرور:** `ragflow_minio_ChangeMe_!23`

---

## 📝 الخطوات التالية

### 1. تسجيل الدخول
افتح المتصفح وانتقل إلى: `http://YOUR_SERVER_IP:8080`

### 2. إنشاء Knowledge Base جديدة
- من القائمة الجانبية، اختر "Knowledge Base"
- انقر على "Create Knowledge Base"
- أعط اسمًا للمعرفة

### 3. رفع الملفات
- ادخل إلى Knowledge Base التي أنشأتها
- انقر "Upload Files"
- اختر ملفات (PDF, DOCX, TXT, etc.)
- انتظر حتى يتم المعالجة والتجزئة

### 4. إنشاء Chat Assistant
- من القائمة، اختر "Chat"
- انقر "Create Assistant"
- اختر Knowledge Base
- اختر نموذج اللغة (يمكنك استخدام Ollama)

### 5. بدء المحادثة
- ابدأ بطرح أسئلة حول محتوى الملفات!

---

## 🛠️ استكشاف الأخطاء

### إذا لم تعمل واجهة RAGFlow
```bash
# تحقق من السجلات
docker logs docker-ragflow-cpu-1 --tail 100

# تحقق من المنفذ
curl http://localhost:8080
```

### إذا كانت TEI لا تعمل
```bash
# تحقق من السجلات
docker logs docker-tei-cpu-1 --tail 100

# اختبار الخدمة
curl -X POST http://localhost:6380/embed \
  -H "Content-Type: application/json" \
  -d '{"inputs": "test"}'
```

### إذا كان Elasticsearch لا يستجيب
```bash
# تحقق من الصحة
curl -u elastic:ragflow_es_password123 http://localhost:1200

# إعادة التشغيل
docker compose --profile cpu restart es01
```

---

## 📚 الموارد

- **المستودع الأصلي:** https://github.com/infiniflow/ragflow
- **التوثيق:** https://ragflow.io/docs
- **Discord:** https://discord.gg/ragflow

---

## ⚡ نصائح الأداء

1. **للملفات الكبيرة:** قد تحتاج إلى زيادة `MEM_LIMIT` في `.env`
2. **للنماذج الكبيرة:** استخدم GPU profile بدلاً من CPU
3. **للإنتاج:** قم بتغيير جميع كلمات المرور الافتراضية
4. **النسخ الاحتياطي:** قم بعمل backup دوري لـ volumes:
   ```bash
   docker volume ls | grep docker_
   ```

---

**تاريخ التشغيل:** 2025-11-17
**الإصدار:** RAGFlow v0.21.1-slim
**الملف الشخصي:** CPU
