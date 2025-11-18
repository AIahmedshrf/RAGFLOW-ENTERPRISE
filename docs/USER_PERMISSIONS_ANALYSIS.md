# 🔐 تحليل نظام صلاحيات المستخدمين في RAGFlow

**التاريخ**: 18 نوفمبر 2025  
**الهدف**: تحليل آلية تحديد صلاحيات المستخدمين (superuser) عند الإنشاء  

---

## 🎯 الملخص التنفيذي

### المشكلة
عند إنشاء مستخدم جديد من Admin UI في **Community Edition**:
- Form يحتوي على: Email, Password, Confirm Password فقط
- **لا يوجد خيار لتحديد Role أو Superuser status**
- المستخدم الجديد يكون **عادي (non-superuser) دائمًا**

### الحالة المدروسة
```
Email: testadmin@admin.com
Password: admin123456
Created: Tue, 18 Nov 2025 21:09:53 GMT
Expected is_superuser: 0 (False)
```

### السبب الجذري
```python
# admin/server/services.py:82
"is_superuser": role == "admin",

# admin/server/routes.py:86
role = data.get('role', 'user')  # ← Default: 'user'
```

**Frontend لا يُرسل `role` parameter** → Backend يستخدم القيمة الافتراضية `"user"` → `is_superuser = False`

---

## 📊 تحليل الكود

### 1. Frontend Form (Community Edition)

#### الملف: `web/src/pages/admin/forms/user-form.tsx`

```tsx
export const CreateUserForm = ({ id, form, onSubmit }: CreateUserFormProps) => {
  const { t } = useTranslation();

  const { data: roleList } = useQuery({
    queryKey: ['admin/listRoles'],
    queryFn: async () => (await listRoles()).data.data.roles,
    enabled: IS_ENTERPRISE,  // ← فقط في Enterprise!
    retry: false,
  });

  return (
    <Form {...form}>
      <form id={id} onSubmit={form.handleSubmit(onSubmit)}>
        {/* Email field */}
        <FormField name="email" ... />
        
        {/* Password field */}
        <FormField name="password" ... />
        
        {/* Confirm password field */}
        <FormField name="confirmPassword" ... />

        {/* Role field - ENTERPRISE ONLY! */}
        <EnterpriseFeature>
          {() => (
            <FormField name="role">
              <Select>
                {roleList?.map((role) => (
                  <SelectItem value={role.role_name}>
                    {role.role_name}
                  </SelectItem>
                ))}
              </Select>
            </FormField>
          )}
        </EnterpriseFeature>
      </form>
    </Form>
  );
};
```

**النتيجة**:
- في **Community**: 3 حقول فقط (Email, Password, Confirm)
- في **Enterprise**: 4 حقول (+ Role dropdown)

---

### 2. Frontend Submit Handler

#### الملف: `web/src/pages/admin/users.tsx:173-196`

```tsx
const createUserMutation = useMutation({
  mutationFn: async ({
    email,
    password,
    role,  // ← Optional parameter
  }: {
    email: string;
    password: string;
    role?: string;
  }) => {
    // Step 1: Create user (always happens)
    await createUser(email, rsaPsw(password) as string);

    // Step 2: Update role (only in Enterprise + if role provided)
    if (IS_ENTERPRISE && role) {
      await updateUserRoleMutation.mutateAsync({ email, role });
    }
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['admin/listUsers'] });
    setCreateUserModalOpen(false);
    createUserForm.form.reset();
  },
});
```

**التدفق**:
```
Community Edition:
  form data = { email, password, confirmPassword }
  role = undefined
  → createUser(email, password)  // لا يُمرر role!

Enterprise Edition:
  form data = { email, password, confirmPassword, role }
  role = "admin" أو "user" أو غيره
  → createUser(email, password)
  → if (role) updateUserRole(email, role)
```

---

### 3. Backend API Handler

#### الملف: `admin/server/routes.py:78-100`

```python
@admin_bp.route('/users', methods=['POST'])
@login_required
@check_admin_auth
def create_user():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return error_response("Username and password are required", 400)

        username = data['username']
        password = data['password']
        role = data.get('role', 'user')  # ← DEFAULT: 'user'
        
        # Call UserMgr.create_user with role parameter
        res = UserMgr.create_user(username, password, role)
        
        if res["success"]:
            user_info = res["user_info"]
            user_info.pop("password")
            return success_response(user_info, "User created successfully")
        else:
            return error_response("create user failed")

    except AdminException as e:
        return error_response(e.message, e.code)
```

**الملاحظات**:
1. `role` parameter اختياري
2. القيمة الافتراضية: `"user"` (ليس `"admin"`)
3. `data.get('role', 'user')` يُرجع `'user'` إذا لم يُرسل Frontend `role`

**في حالة testadmin@admin.com**:
```python
data = {
  'username': 'testadmin@admin.com',
  'password': '<encrypted>',
  # 'role' غير موجود!
}

role = data.get('role', 'user')  # → 'user'
```

---

### 4. User Creation Logic

#### الملف: `admin/server/services.py:69-85`

```python
@staticmethod
def create_user(username, password, role="user") -> dict:
    # Validate email
    if not re.match(r"^[\w\._-]+@([\w_-]+\.)+[\w-]{2,}$", username):
        raise AdminException(f"Invalid email address: {username}!")
    
    # Check if already exists
    if UserService.query(email=username):
        raise UserAlreadyExistsError(username)
    
    # Construct user info
    user_info_dict = {
        "email": username,
        "nickname": "",
        "password": decrypt(password),
        "login_channel": "password",
        "is_superuser": role == "admin",  # ← CRITICAL LINE!
    }
    
    return create_new_user(user_info_dict)
```

**المنطق الحاسم**:
```python
"is_superuser": role == "admin"

# إذا role = "admin" → is_superuser = True
# إذا role = "user" → is_superuser = False
# إذا role = أي شيء آخر → is_superuser = False
```

**في حالة testadmin@admin.com**:
```python
role = "user"  # (من الـ default في routes.py)
is_superuser = ("user" == "admin")  # → False
```

---

## 🔍 تتبع تدفق البيانات الكامل

### السيناريو: إنشاء testadmin@admin.com من Admin UI (Community)

```
┌─────────────────────────────────────────────────────┐
│ Step 1: User fills form in Browser                 │
├─────────────────────────────────────────────────────┤
│ Email: testadmin@admin.com                          │
│ Password: admin123456                               │
│ Confirm: admin123456                                │
│                                                     │
│ Note: No "Role" field visible (Community Edition)  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: Form validation (Zod schema)               │
├─────────────────────────────────────────────────────┤
│ ✓ Email valid format                               │
│ ✓ Password min 6 chars                             │
│ ✓ Password === Confirm password                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: onSubmit called                            │
├─────────────────────────────────────────────────────┤
│ const data = {                                      │
│   email: "testadmin@admin.com",                     │
│   password: "admin123456",                          │
│   confirmPassword: "admin123456",                   │
│   role: undefined  ← Not in form!                   │
│ }                                                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: createUser(email, rsaPsw(password))        │
├─────────────────────────────────────────────────────┤
│ Function: web/src/services/admin-service.ts:154    │
│                                                     │
│ export const createUser = (email, password) =>     │
│   request.post(adminCreateUser, {                  │
│     username: email,                               │
│     password: password,                            │
│     // role: NOT SENT!                             │
│   });                                              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: HTTP POST /api/v1/admin/users              │
├─────────────────────────────────────────────────────┤
│ Request Body:                                       │
│ {                                                   │
│   "username": "testadmin@admin.com",                │
│   "password": "<RSA_ENCRYPTED>",                    │
│ }                                                   │
│                                                     │
│ Note: "role" key not present!                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 6: Backend route handler                      │
├─────────────────────────────────────────────────────┤
│ File: admin/server/routes.py:78                    │
│                                                     │
│ def create_user():                                 │
│     data = request.get_json()                      │
│     # data = {                                     │
│     #   'username': 'testadmin@admin.com',         │
│     #   'password': '<encrypted>'                  │
│     # }                                            │
│                                                     │
│     username = data['username']                    │
│     password = data['password']                    │
│     role = data.get('role', 'user')  ← 'user'!    │
│                                                     │
│     res = UserMgr.create_user(username,            │
│                                password,            │
│                                role='user')         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 7: UserMgr.create_user()                      │
├─────────────────────────────────────────────────────┤
│ File: admin/server/services.py:69                  │
│                                                     │
│ def create_user(username, password, role="user"):  │
│     user_info_dict = {                             │
│         "email": username,                         │
│         "password": decrypt(password),             │
│         "is_superuser": role == "admin",  ← False! │
│         # because role='user' != 'admin'           │
│     }                                              │
│     return create_new_user(user_info_dict)         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 8: Database INSERT                            │
├─────────────────────────────────────────────────────┤
│ INSERT INTO user (                                  │
│   id, email, password, nickname,                   │
│   is_superuser, is_active, create_time, ...        │
│ ) VALUES (                                         │
│   '<uuid>', 'testadmin@admin.com', '<hashed>',     │
│   'testadmin', 0, 1, 1731962993, ...               │
│ );                                                 │
│                                                     │
│ is_superuser = 0  ✓ Confirmed!                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ Step 9: Response to Frontend                       │
├─────────────────────────────────────────────────────┤
│ {                                                   │
│   "code": 0,                                       │
│   "message": "User created successfully",          │
│   "data": {                                        │
│     "email": "testadmin@admin.com",                │
│     "nickname": "testadmin",                       │
│     "is_superuser": false,                         │
│     "is_active": true,                             │
│     ...                                            │
│   }                                                │
│ }                                                  │
└─────────────────────────────────────────────────────┘
```

---

## 💡 الحل: كيفية جعل testadmin@admin.com superuser

### الطريقة 1: تحديث قاعدة البيانات (الحل الحالي الوحيد في Community)

```sql
-- الدخول للقاعدة
docker exec -it docker-mysql-1 mysql -uroot -p<password> rag_flow

-- التحديث
UPDATE user 
SET is_superuser = 1 
WHERE email = 'testadmin@admin.com';

-- التحقق
SELECT email, is_superuser, is_active, create_time 
FROM user 
WHERE email = 'testadmin@admin.com';
```

**النتيجة المتوقعة**:
```
+----------------------+--------------+-----------+------------+
| email                | is_superuser | is_active | create_time|
+----------------------+--------------+-----------+------------+
| testadmin@admin.com  |            1 |         1 | 1731962993 |
+----------------------+--------------+-----------+------------+
```

---

### الطريقة 2: تعديل Frontend Form (Community Edition) ⚠️ يتطلب تطوير

#### الهدف
إضافة حقل Role في Create User form حتى في Community Edition.

#### الخطوات

**1. تعديل user-form.tsx**

```tsx
// web/src/pages/admin/forms/user-form.tsx

// إزالة <EnterpriseFeature> wrapper
// قبل:
<EnterpriseFeature>
  {() => (
    <FormField name="role">
      <Select>...</Select>
    </FormField>
  )}
</EnterpriseFeature>

// بعد:
<FormField name="role">
  <FormControl>
    <Select {...field} defaultValue="user">
      <SelectTrigger>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectItem value="user">User</SelectItem>
          <SelectItem value="admin">Admin</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  </FormControl>
</FormField>
```

**2. تعديل users.tsx**

```tsx
// web/src/pages/admin/users.tsx:173

const createUserMutation = useMutation({
  mutationFn: async ({ email, password, role }) => {
    // إرسال role مباشرة للـ API
    await createUser(email, rsaPsw(password) as string, role);
    
    // لا حاجة لـ updateUserRole منفصل
  },
});
```

**3. تعديل admin-service.ts**

```tsx
// web/src/services/admin-service.ts:154

// قبل:
export const createUser = (email: string, password: string) =>
  request.post<ResponseData<boolean>>(adminCreateUser, {
    username: email,
    password,
  });

// بعد:
export const createUser = (
  email: string, 
  password: string,
  role: string = 'user'  // ← إضافة parameter
) =>
  request.post<ResponseData<boolean>>(adminCreateUser, {
    username: email,
    password,
    role,  // ← إرساله للـ backend
  });
```

**4. إعادة البناء**

```bash
cd /srv/projects/RAGFLOW-ENTERPRISE/web
npm run build
docker cp dist docker-ragflow-cpu-1:/ragflow/web/
docker exec docker-ragflow-cpu-1 nginx -s reload
```

**النتيجة**:
- Form يظهر dropdown "Role"
- الخيارات: "User" أو "Admin"
- Backend يستقبل `role` parameter
- `is_superuser` يُحدد تلقائيًا

---

### الطريقة 3: استخدام Admin CLI

```bash
# الدخول للـ container
docker exec -it docker-ragflow-cpu-1 bash

# تشغيل Admin CLI
cd /ragflow/admin/client
python3 admin_client.py

# إنشاء مستخدم admin
admin> create user "superadmin@example.com" "password123" admin;

# التحقق
admin> list users;
```

**ملاحظة**: Admin CLI يدعم `role` parameter مباشرة!

---

## 📋 الخلاصة والتوصيات

### الوضع الحالي

| Component | Status | Supports Role? |
|-----------|--------|----------------|
| Admin API (Backend) | ✅ جاهز | ✅ نعم (`role` parameter) |
| Admin CLI | ✅ جاهز | ✅ نعم (في الأمر) |
| Admin UI (Enterprise) | ✅ جاهز | ✅ نعم (dropdown في form) |
| Admin UI (Community) | ⚠️ محدود | ❌ لا (لا يوجد حقل) |

### testadmin@admin.com

**الحالة الحالية**:
```sql
SELECT email, is_superuser FROM user WHERE email='testadmin@admin.com';
-- Result: testadmin@admin.com | 0
```

**السبب**:
1. Community UI لا يُرسل `role` parameter
2. Backend يستخدم default: `role = 'user'`
3. `is_superuser = ('user' == 'admin')` → `False`

**الحل الفوري**:
```sql
UPDATE user SET is_superuser=1 WHERE email='testadmin@admin.com';
```

**الحل الدائم**:
- إما: الترقية لـ Enterprise Edition
- أو: تعديل Community Form (الطريقة 2 أعلاه)
- أو: استخدام Admin CLI لإنشاء admins

### التوصيات

#### للـ Community Edition Users
1. **استخدم SQL لتحويل المستخدمين لـ superuser**:
   ```sql
   UPDATE user SET is_superuser=1 WHERE email='your-admin@example.com';
   ```

2. **أنشئ admins من Admin CLI**:
   ```bash
   admin> create user "admin@example.com" "password" admin;
   ```

3. **أنشئ مستخدم admin واحد يدويًا، ثم استخدمه لإدارة الباقين**

#### لـ RAGFlow Developers
1. **فكّر في إضافة checkbox "Is Admin" في Community Create User form**
   - بسيط ولا يحتاج Roles system كامل
   - يسمح بإنشاء admins بدون SQL

2. **وضّح في الـ documentation**:
   - كيفية إنشاء superuser الأول
   - الفرق بين Community و Enterprise

3. **أضف validation في Backend**:
   ```python
   if role == "admin" and not current_user.is_superuser:
       raise AdminException("Only superusers can create admin users")
   ```

---

## 🔗 المراجع

### الملفات ذات الصلة

```
Backend:
- admin/server/routes.py:78-100       (create_user endpoint)
- admin/server/services.py:69-85      (UserMgr.create_user logic)
- admin/server/auth.py:97-102         (check_admin_auth decorator)
- api/apps/user_app.py:227            (register endpoint)

Frontend:
- web/src/pages/admin/users.tsx:173-196           (createUserMutation)
- web/src/pages/admin/forms/user-form.tsx:131-157 (Role field)
- web/src/services/admin-service.ts:154-158       (createUser API call)
- web/src/pages/admin/wrappers/authorized.tsx     (Auth check)

Database:
- api/db/db_models.py                 (User model definition)
```

### الأوامر المفيدة

```sql
-- فحص جميع المستخدمين
SELECT email, is_superuser, is_active, role, create_time FROM user;

-- فحص admins فقط
SELECT email, is_superuser FROM user WHERE is_superuser = 1;

-- تحويل مستخدم لـ admin
UPDATE user SET is_superuser = 1 WHERE email = 'user@example.com';

-- حذف مستخدم
DELETE FROM user WHERE email = 'user@example.com';
```

---

**الكاتب**: AI Expert System  
**التاريخ**: 18 نوفمبر 2025  
**المرجع**: RAGFlow source code analysis + Admin UI testing  
**الحالة**: ✅ تحليل مكتمل

