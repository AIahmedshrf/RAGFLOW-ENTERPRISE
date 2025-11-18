# دليل استخدام واجهة الإدارة (Admin UI) - RAGFlow

## 🎯 نظرة عامة

واجهة الإدارة (Admin UI) هي لوحة تحكم متقدمة لإدارة نظام RAGFlow بالكامل. **فقط المستخدمون ذوو صلاحيات Superuser** يمكنهم الوصول إليها.

---

## 🔐 كيفية الوصول إلى Admin UI

### **⚠️ متطلب مهم: تفعيل Admin Server**

**Admin UI يتطلب تفعيل Admin Service أولاً!**

#### **الخطوة 1: تفعيل Admin Server**

**تعديل `docker/docker-compose.yml`:**

```yaml
services:
  ragflow-cpu:
    depends_on:
      # ... dependencies ...
    profiles: [ cpu ]
    image: ${RAGFLOW_IMAGE}
    command:
      - --enable-adminserver  # ← أضف هذا!
    ports:
      - "8080:80"
      - "${ADMIN_SVR_HTTP_PORT:-9381}:9381"  # ← تأكد من نشر المنفذ
      # ... rest of config ...
```

**تطبيق التغييرات:**

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu up -d
```

**التحقق من التفعيل:**

```bash
# يجب أن يعيد: {"code":401,"data":null,"message":"Authentication required"}
curl http://localhost:9381/api/v1/admin/auth
```

---

### **الخطوة 2: الوصول إلى Admin UI**

#### 1. **الرابط:**
```
http://YOUR_SERVER_IP:8080/admin
```

#### 2. **بيانات الدخول الافتراضية:**

| البريد الإلكتروني | كلمة المرور |
|------------------|------------|
| admin@ragflow.io | admin      |

⚠️ **مهم:** هذا المستخدم يتم إنشاؤه تلقائياً عند أول تشغيل للنظام.

---

## 🚫 لماذا لا أرى Admin UI؟

### المشكلة الشائعة:

إذا أنشأت مستخدم جديد عبر **Sign Up** (التسجيل العادي)، فإن المستخدم **لن يكون** Superuser افتراضياً!

```sql
-- مستخدمون عبر Sign Up:
is_superuser: 0  ← ليس admin
```

### التحقق من حالة المستخدم:

```bash
docker exec docker-mysql-1 mysql -uroot -p'YOUR_MYSQL_PASSWORD' -D rag_flow \
  -e "SELECT email, is_superuser, status, nickname FROM user WHERE email='YOUR_EMAIL';"
```

**النتيجة المطلوبة:**
```
email               is_superuser  status  nickname
admin@myragflow.io  1            1       admin
                    ↑ يجب أن يكون 1
```

---

## ✅ الحلول: كيف تصبح Superuser

### **الخيار 1: استخدام المستخدم الافتراضي**

استخدم بيانات الدخول الافتراضية:
- Email: `admin@ragflow.io`
- Password: `admin`

---

### **الخيار 2: ترقية مستخدم موجود إلى Superuser**

#### **الطريقة 1: عبر SQL (الأسرع)**

```bash
# استبدل YOUR_EMAIL ببريدك الفعلي
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "UPDATE user SET is_superuser=1 WHERE email='YOUR_EMAIL';"

# تحقق من التحديث
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "SELECT email, is_superuser, status FROM user WHERE email='YOUR_EMAIL';"
```

**مثال:**
```bash
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "UPDATE user SET is_superuser=1 WHERE email='admin@myragflow.io';"
```

---

#### **الطريقة 2: عبر Admin CLI**

إذا كنت قد فعّلت Admin Service:

```bash
# تثبيت ragflow-cli
pip install ragflow-cli==0.21.1

# الاتصال بـ Admin Service
ragflow-cli -h 127.0.0.1 -p 9381

# بعد تسجيل الدخول بمستخدم admin موجود:
admin> ALTER USER ACTIVE "user@example.com" on;
```

⚠️ **ملاحظة:** Admin CLI لا يمكنه تغيير `is_superuser` مباشرة، فقط `is_active`.

---

#### **الطريقة 3: إنشاء مستخدم Superuser جديد**

استخدم السكريبت الذي أنشأناه سابقاً:

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker

# تشغيل السكريبت
docker exec -i docker-ragflow-cpu-1 python3 /ragflow/docker/create_admin_strong_pass.py
```

هذا السكريبت:
- ✅ يحذف المستخدمين القدامى
- ✅ ينشئ `admin@ragflow.io` مع `is_superuser=1`
- ✅ كلمة المرور: `ragflow123`

---

## 📊 ميزات Admin UI

### 1. **Service Status (حالة الخدمات)**

مراقبة جميع خدمات النظام:
- **RAGFlow Server** - الخدمة الرئيسية
- **MySQL** - قاعدة البيانات
- **Elasticsearch** - محرك البحث
- **Redis** - ذاكرة التخزين المؤقت
- **MinIO** - تخزين الملفات
- **TEI** - خدمة التضمين
- **Local Reranker** - خدمة إعادة الترتيب

**الإجراءات المتاحة:**
- عرض معلومات إضافية (Extra Info)
- عرض تفاصيل الخدمة (Service Details)
- فلترة حسب نوع الخدمة
- البحث بالاسم

---

### 2. **User Management (إدارة المستخدمين)**

إدارة شاملة لجميع المستخدمين:

**الإجراءات:**
- ✅ عرض جميع المستخدمين
- ✅ إنشاء مستخدم جديد (New User)
- ✅ تفعيل/تعطيل المستخدمين (Enable toggle)
- ✅ عرض تفاصيل المستخدم (View Details)
- ✅ تغيير كلمة المرور (Change Password)
- ✅ حذف المستخدم (Delete User)

**الفلترة:**
- حسب الحالة (Active / Inactive)
- البحث بالبريد الإلكتروني أو الاسم

---

### 3. **User Detail (تفاصيل المستخدم)**

عرض تفصيلي لبيانات المستخدم:
- المعلومات الشخصية
- جميع الـ Datasets المملوكة
- جميع الـ Agents المُنشأة
- تاريخ الإنشاء والتعديل

---

## 🔧 تفعيل Admin Service (اختياري)

Admin Service هو واجهة CLI (سطر الأوامر) منفصلة.

### تفعيل عبر Docker:

**1. تعديل `docker-compose.yml`:**

```yaml
services:
  ragflow-cpu:
    command:
      - --enable-adminserver
```

**2. إعادة التشغيل:**

```bash
docker compose --profile cpu up -d
```

**3. استخدام CLI:**

```bash
pip install ragflow-cli==0.21.1
ragflow-cli -h 127.0.0.1 -p 9381
```

**كلمة المرور الافتراضية:** `admin`

---

## 🚨 استكشاف الأخطاء

### **الخطأ 0: صفحة 404 عند زيارة /admin**

**الأعراض:**
```
404
Page not found, please enter a correct address.
```

**السبب:**
Admin Server **غير مُفعّل** في docker-compose.yml

**الحل:**
```yaml
# في docker/docker-compose.yml
services:
  ragflow-cpu:
    command:
      - --enable-adminserver  # ← أضف هذا
```

**التطبيق:**
```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/docker
docker compose --profile cpu up -d
```

**التحقق:**
```bash
# يجب أن ترى: "RAGFlow Admin service start..."
docker logs docker-ragflow-cpu-1 | grep -i admin

# اختبار API
curl http://localhost:9381/api/v1/admin/auth
# يجب أن يعيد: {"code":401,"data":null,"message":"Authentication required"}
```

---

### **الخطأ 1: "Not admin" (403)**

**السبب:**
```python
if not user.is_superuser:
    raise AdminException("Not admin", 403)
```

**الحل:**
```bash
# تحديث is_superuser إلى 1
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "UPDATE user SET is_superuser=1 WHERE email='YOUR_EMAIL';"
```

---

### **الخطأ 2: صفحة 404 عند زيارة /admin (بعد التفعيل)**

**السبب:** لم تسجل الدخول بعد.

**الحل:** 
1. اذهب إلى `http://localhost:8080/admin`
2. سجل دخول ببيانات Superuser
3. ستظهر لوحة التحكم تلقائياً

---

### **الخطأ 3: "User inactive"**

**السبب:**
```sql
is_active: 0
```

**الحل:**
```bash
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "UPDATE user SET is_active=1 WHERE email='YOUR_EMAIL';"
```

---

## 📝 الفرق بين Admin UI و Admin CLI

| الميزة | Admin UI (واجهة ويب) | Admin CLI (سطر الأوامر) |
|--------|---------------------|----------------------|
| **الوصول** | http://localhost:8080/admin | ragflow-cli -h 127.0.0.1 -p 9381 |
| **المتطلبات** | متصفح ويب | تثبيت ragflow-cli |
| **إدارة المستخدمين** | ✅ كاملة | ✅ كاملة |
| **مراقبة الخدمات** | ✅ واجهة رسومية | ✅ نصية |
| **سهولة الاستخدام** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **التشغيل التلقائي** | ✅ دائماً مفعّل | ❌ يحتاج --enable-adminserver |

**التوصية:** استخدم **Admin UI** للإدارة اليومية (أسهل وأسرع).

---

## 🔒 أفضل الممارسات الأمنية

### 1. **تغيير كلمة المرور الافتراضية**

```bash
# عبر Admin UI:
1. اذهب إلى User Management
2. ابحث عن admin@ragflow.io
3. اضغط Change Password
4. أدخل كلمة مرور قوية
```

### 2. **إنشاء مستخدمين منفصلين**

- لا تستخدم `admin@ragflow.io` للاستخدام اليومي
- أنشئ مستخدمين منفصلين لكل شخص
- فعّل فقط Admin لمن يحتاجه

### 3. **مراجعة المستخدمين دورياً**

```sql
-- عرض جميع Superusers
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "SELECT email, is_superuser, is_active, create_date FROM user WHERE is_superuser=1;"
```

---

## 📚 المراجع

- [الوثائق الرسمية: Accessing Admin UI](https://ragflow.io/docs/dev/accessing_admin_ui)
- [الوثائق الرسمية: Admin CLI](https://ragflow.io/docs/dev/manage_users_and_services)
- [ملف manage_users_and_services.md](/srv/projects/RAGFLOW-ENTERPRISE/docs/guides/manage_users_and_services.md)

---

## ✅ خلاصة سريعة

### للوصول إلى Admin UI:

```bash
# 1. تأكد من أن المستخدم superuser
docker exec docker-mysql-1 mysql -uroot -p'ragflow_root_ChangeMe_!23' -D rag_flow \
  -e "UPDATE user SET is_superuser=1 WHERE email='YOUR_EMAIL';"

# 2. افتح المتصفح
http://localhost:8080/admin

# 3. سجل دخول
Email: YOUR_EMAIL
Password: YOUR_PASSWORD
```

**Done! 🎉**

---

**تاريخ التحديث:** 18 نوفمبر 2025  
**الإصدار:** RAGFlow v0.21.1-slim
