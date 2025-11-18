# إصلاح مشكلة Admin UI - صفحة 404

## المشكلة

عند زيارة `http://localhost:8080/admin` تظهر صفحة 404:

```
404
Page not found, please enter a correct address.
```

## السبب الجذري

**المشكلة 1: Admin Server غير مُفعّل**
- Admin UI يحتاج إلى Backend API على المنفذ 9381
- الخدمة معطلة افتراضيًا ويجب تفعيلها بـ `--enable-adminserver`

**المشكلة 2: ملفات Layouts والـ Wrappers ناقصة**
- الكود في `web/src/routes.ts` كان يستخدم مسارات خاطئة
- الملفات التالية كانت ناقصة:
  * `web/src/pages/admin/layouts/root-layout.tsx`
  * `web/src/pages/admin/layouts/navigation-layout.tsx`
  * `web/src/pages/admin/wrappers/authorized.tsx`

**المشكلة 3: Routes غير متطابقة مع المستودع الأصلي**
- الكود كان يستخدم:
```ts
{
  path: Routes.Admin,
  component: `@/pages/admin`,  // ← خطأ! يجب أن يكون root-layout
  layout: false,
}
```

- بينما يجب أن يكون:
```ts
{
  path: Routes.Admin,
  layout: false,
  component: `@/pages/admin/layouts/root-layout`,
  routes: [
    {
      path: '',
      component: `@/pages/admin/login`,
    },
    // ...
  ]
}
```

## الحل

### الخطوة 1: تفعيل Admin Service

في `docker/docker-compose.yml`:

```yaml
services:
  ragflow-cpu:
    command:
      - --enable-adminserver  # ← أضف هذا
    ports:
      - "8080:80"
      - "${ADMIN_SVR_HTTP_PORT:-9381}:9381"
```

### الخطوة 2: إضافة الملفات الناقصة

**أ. إنشاء المجلدات:**
```bash
mkdir -p web/src/pages/admin/layouts
mkdir -p web/src/pages/admin/wrappers
```

**ب. `web/src/pages/admin/layouts/root-layout.tsx`:**
```tsx
import { Outlet } from 'umi';

const AdminRootLayout = () => {
  return <Outlet />;
};

export default AdminRootLayout;
```

**ج. `web/src/pages/admin/layouts/navigation-layout.tsx`:**
```tsx
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink, Outlet, useNavigate } from 'umi';
import { useMutation, useQuery } from '@tanstack/react-query';
import { LucideMonitor, LucideServerCrash, LucideSquareUserRound, LucideUserCog, LucideUserStar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Routes } from '@/routes';
import { getSystemVersion, logout } from '@/services/admin-service';
import authorizationUtil from '@/utils/authorization-util';
import ThemeSwitch from '../components/theme-switch';
import { IS_ENTERPRISE } from '../utils';

const AdminNavigationLayout = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const { data: version } = useQuery({
    queryKey: ['admin/version'],
    queryFn: async () => (await getSystemVersion())?.data?.data?.version,
  });

  const navItems = useMemo(
    () => [
      {
        path: Routes.AdminServices,
        name: t('admin.serviceStatus'),
        icon: <LucideServerCrash className="size-[1em]" />,
      },
      {
        path: Routes.AdminUserManagement,
        name: t('admin.userManagement'),
        icon: <LucideUserCog className="size-[1em]" />,
      },
      ...(IS_ENTERPRISE
        ? [
            {
              path: Routes.AdminWhitelist,
              name: t('admin.registrationWhitelist'),
              icon: <LucideUserStar className="size-[1em]" />,
            },
            {
              path: Routes.AdminRoles,
              name: t('admin.roles'),
              icon: <LucideSquareUserRound className="size-[1em]" />,
            },
            {
              path: Routes.AdminMonitoring,
              name: t('admin.monitoring'),
              icon: <LucideMonitor className="size-[1em]" />,
            },
          ]
        : []),
    ],
    [t],
  );

  const logoutMutation = useMutation({
    mutationKey: ['adminLogout'],
    mutationFn: async () => {
      await logout();
      authorizationUtil.removeAll();
      navigate(Routes.Admin);
    },
    retry: false,
  });

  return (
    <main className="w-screen h-screen flex flex-row px-6 pt-12 pb-6 dark:*:focus-visible:ring-white">
      <aside className="w-72 mr-6 flex flex-col gap-6">
        <div className="flex items-center mb-6">
          <img className="size-8 mr-5" src="/logo.svg" alt="logo" />
          <span className="text-xl font-bold">{t('admin.title')}</span>
        </div>

        <nav>
          <ul className="space-y-4">
            {navItems.map((it) => (
              <li key={it.path}>
                <NavLink
                  to={it.path}
                  className={({ isActive }) =>
                    cn(
                      'px-4 py-3 rounded-lg',
                      'text-base w-full flex items-center justify-start text-text-secondary',
                      'hover:bg-bg-card focus:bg-bg-card focus-visible:bg-bg-card',
                      'hover:text-text-primary focus:text-text-primary focus-visible:text-text-primary',
                      'active:text-text-primary',
                      'transition-colors',
                      {
                        'bg-bg-card text-text-primary': isActive,
                      },
                    )
                  }
                >
                  {it.icon}
                  <span className="ml-3">{it.name}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="mt-auto space-y-4">
          <div className="flex justify-between items-center">
            <span className="leading-none text-xs text-accent-primary">
              {version}
            </span>

            <ThemeSwitch />
          </div>

          <Button
            size="lg"
            variant="transparent"
            block
            onClick={() => logoutMutation.mutate()}
          >
            {t('header.logout')}
          </Button>
        </div>
      </aside>

      <section className="flex-1 h-full">
        <Outlet />
      </section>
    </main>
  );
};

export default AdminNavigationLayout;
```

**د. `web/src/pages/admin/wrappers/authorized.tsx`:**
```tsx
import { Routes } from '@/routes';
import authorizationUtil from '@/utils/authorization-util';
import { Navigate, Outlet } from 'umi';

export default function AuthorizedAdminWrapper() {
  const isLogin = !!authorizationUtil.getAuthorization();

  return isLogin ? <Outlet /> : <Navigate to={Routes.Admin} />;
}
```

### الخطوة 3: تصحيح Routes

في `web/src/routes.ts`، استبدل:

```ts
// Admin routes
{
  path: Routes.Admin,
  component: `@/pages/admin`,
  layout: false,
},
{
  path: `${Routes.AdminUserManagement}/:id`,
  layout: false,
  wrappers: ['@/wrappers/authAdmin'],
  component: `@/pages/admin/user-detail`,
},
{
  path: Routes.Admin,
  component: `@/pages/admin/layout`,
  layout: false,
  routes: [
    {
      path: Routes.AdminServices,
      component: `@/pages/admin/service-status`,
      wrappers: ['@/wrappers/authAdmin'],
    },
    // ...
  ]
}
```

بـ:

```ts
// Admin routes
{
  path: Routes.Admin,
  layout: false,
  component: `@/pages/admin/layouts/root-layout`,
  routes: [
    {
      path: '',
      component: `@/pages/admin/login`,
    },
    {
      path: `${Routes.AdminUserManagement}/:id`,
      wrappers: ['@/pages/admin/wrappers/authorized'],
      component: `@/pages/admin/user-detail`,
    },
    {
      path: Routes.Admin,
      component: `@/pages/admin/layouts/navigation-layout`,
      wrappers: ['@/pages/admin/wrappers/authorized'],
      routes: [
        {
          path: Routes.AdminServices,
          component: `@/pages/admin/service-status`,
        },
        {
          path: Routes.AdminUserManagement,
          component: `@/pages/admin/users`,
        },
        ...(IS_ENTERPRISE
          ? [
              {
                path: Routes.AdminWhitelist,
                component: `@/pages/admin/whitelist`,
              },
              {
                path: Routes.AdminRoles,
                component: `@/pages/admin/roles`,
              },
              {
                path: Routes.AdminMonitoring,
                component: `@/pages/admin/monitoring`,
              },
            ]
          : []),
      ],
    },
  ],
},
```

### الخطوة 4: نقل index.tsx

```bash
mv web/src/pages/admin/index.tsx web/src/pages/admin/login.tsx
```

### الخطوة 5: إعادة بناء الـ Docker Image

```bash
cd docker
docker compose --profile cpu build ragflow-cpu
docker compose --profile cpu up -d ragflow-cpu
```

أو إعادة بناء سريعة (إذا كان المصدر موجودًا):

```bash
cd docker
docker compose --profile cpu restart ragflow-cpu
```

## التحقق من الحل

### 1. Admin Service يعمل:
```bash
curl http://localhost:9381/api/v1/admin/auth
# يجب أن يعيد:
# {"code":401,"data":null,"message":"Authentication required"}
```

### 2. Admin UI يُحمّل:
```bash
curl -I http://localhost:8080/admin
# يجب أن يعيد HTTP 200
```

### 3. تسجيل الدخول:
- افتح: `http://localhost:8080/admin`
- البيانات:
  - Email: `admin@myragflow.io`
  - Password: `admin`

### 4. صفحات Admin تعمل:
- Service Status: `http://localhost:8080/admin/services`
- User Management: `http://localhost:8080/admin/users`

## الملاحظات المهمة

### البنية الصحيحة للـ Routes

Admin UI يستخدم **3 مستويات من الـ routing**:

```
/admin (root-layout)
  ├─ '' (login page) ← صفحة تسجيل الدخول
  ├─ /admin/users/:id (user-detail) ← تفاصيل مستخدم
  └─ /admin (navigation-layout with wrapper)
       ├─ /admin/services (service-status)
       ├─ /admin/users (users list)
       ├─ /admin/whitelist (whitelist) [Enterprise]
       ├─ /admin/roles (roles) [Enterprise]
       └─ /admin/monitoring (monitoring) [Enterprise]
```

### الفرق بين الـ Wrappers

- `@/wrappers/auth`: للمستخدمين العاديين (RAGFlow UI)
- `@/wrappers/authAdmin`: **لا يوجد** في المستودع الأصلي!
- `@/pages/admin/wrappers/authorized`: للـ Admin UI فقط

### لماذا توقفت الصفحة عند 404؟

1. **React Router** حمّل `index.html`
2. **JavaScript bundle** فحص المسار `/admin`
3. **Routes config** لم يجد تطابقًا:
   - `@/pages/admin` كان يبحث عن component مباشر
   - لم يجد `root-layout` → `login`
4. **Fallback** إلى صفحة 404

## المراجع

- **المستودع الأصلي**: [infiniflow/ragflow](https://github.com/infiniflow/ragflow/tree/main/web/src/pages/admin)
- **التوثيق الرسمي**: [Accessing Admin UI](https://ragflow.io/docs/dev/accessing_admin_ui)
- **Umi Routing**: [Umi.js Routes Configuration](https://umijs.org/docs/guides/routes)

## الخلاصة

**المشكلة** كانت مزيج من:
1. ✅ Admin Service معطل (تم إصلاحه بـ `--enable-adminserver`)
2. ✅ Routes غير صحيحة (تم تصحيحها لتتطابق مع infiniflow/ragflow)
3. ✅ Layouts ناقصة (تمت إضافتها من المستودع الأصلي)

**النتيجة**:
- Admin UI يعمل بشكل كامل ✅
- Service Management يعمل ✅
- User Management يعمل ✅
