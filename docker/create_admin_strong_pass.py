#!/usr/bin/env python3
"""
سكريبت لإنشاء مستخدم admin بكلمة مرور قوية
"""
import sys
sys.path.insert(0, '/ragflow')

from api.db.services.user_service import UserService, TenantService
from api.db import StatusEnum
from api.db.db_models import User
from api.utils import get_uuid

print("="*70)
print("🔧 إنشاء مستخدم Admin مع كلمة مرور: ragflow123")
print("="*70)

# حذف المستخدمين القدامى
print("\n🗑️  حذف مستخدمين قدامى...")
try:
    deleted = User.delete().where(User.email == "admin@ragflow.io").execute()
    print(f"   ✅ تم حذف {deleted} سجل")
except Exception as e:
    print(f"   ⚠️  {e}")

# إنشاء IDs
user_id = get_uuid()
tenant_id = get_uuid()

# إنشاء Tenant
print(f"\n📦 إنشاء Tenant (ID: {tenant_id[:16]}...)")
try:
    TenantService.save(
        id=tenant_id,
        name="Admin Tenant",
        llm_id="deepseek-chat",
        embd_id="BAAI/bge-large-zh-v1.5",
        asr_id="openai/whisper-1",
        parser_ids="naive:General,qa:Q&A"
    )
    print("   ✅ Tenant تم إنشاؤه")
except Exception as e:
    print(f"   ⚠️  {e}")

# إنشاء المستخدم
print(f"\n👤 إنشاء المستخدم (ID: {user_id[:16]}...)")
try:
    UserService.save(
        id=user_id,
        email="admin@ragflow.io",
        nickname="Admin",
        password="ragflow123",  # كلمة مرور جديدة قوية
        status=StatusEnum.VALID.value,
        is_superuser=True,
        tenant_id=tenant_id
    )
    print("   ✅ المستخدم تم إنشاؤه بنجاح!")
except Exception as e:
    print(f"   ❌ خطأ: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# التحقق
print("\n🔍 التحقق من المستخدم...")
try:
    user_check = UserService.query_user("admin@ragflow.io", "ragflow123")
    if user_check:
        print("   ✅ نجح! المستخدم يمكنه تسجيل الدخول")
        print(f"      البريد: {user_check.email}")
        print(f"      الاسم: {user_check.nickname}")
        print(f"      الحالة: {user_check.status}")
        print(f"      Superuser: {user_check.is_superuser}")
    else:
        print("   ❌ فشل التحقق!")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ خطأ في التحقق: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("🎉 تم بنجاح! استخدم هذه البيانات لتسجيل الدخول:")
print("="*70)
print()
print("  📧 البريد الإلكتروني: admin@ragflow.io")
print("  🔑 كلمة المرور: ragflow123")
print()
print("="*70)
print("🌐 افتح: http://YOUR_SERVER_IP:8080")
print("="*70)
