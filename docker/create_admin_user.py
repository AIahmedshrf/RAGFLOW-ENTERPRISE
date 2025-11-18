#!/usr/bin/env python3
"""
سكريبت إنشاء مستخدم admin افتراضي في RAGFlow
"""
import sys
sys.path.insert(0, '/ragflow')

from api.db.services.user_service import UserService, TenantService
from api.utils import get_uuid

def main():
    print("="*60)
    print("🔧 إنشاء مستخدم Admin افتراضي في RAGFlow")
    print("="*60)
    
    # توليد IDs فريدة
    user_id = get_uuid()
    tenant_id = get_uuid()
    
    print(f"\n✓ تم توليد معرفات فريدة")
    print(f"  User ID: {user_id}")
    print(f"  Tenant ID: {tenant_id}")
    
    # الخطوة 1: إنشاء Tenant
    print("\n📦 الخطوة 1: إنشاء Tenant...")
    try:
        TenantService.save(
            id=tenant_id,
            name="Admin Tenant",
            llm_id="deepseek-chat",
            embd_id="BAAI/bge-large-zh-v1.5",
            asr_id="openai/whisper-1",
            parser_ids="naive:General,qa:Q&A"
        )
        print("   ✅ تم إنشاء Tenant بنجاح")
    except Exception as e:
        print(f"   ⚠️  خطأ أو موجود مسبقاً: {e}")
    
    # الخطوة 2: إنشاء المستخدم
    print("\n👤 الخطوة 2: إنشاء المستخدم...")
    try:
        # password ستكون خام - سيتم تشفيرها تلقائياً بواسطة UserService.save
        result = UserService.save(
            id=user_id,
            email="admin@ragflow.io",
            nickname="Admin",
            password="admin",
            status="1",
            is_superuser=True,
            tenant_id=tenant_id
        )
        print("   ✅ تم إنشاء المستخدم بنجاح!")
        print(f"   النتيجة: {result}")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # الخطوة 3: التحقق
    print("\n🔍 الخطوة 3: التحقق من المستخدمين في النظام...")
    try:
        users = UserService.query()
        print(f"   ✓ عدد المستخدمين في قاعدة البيانات: {len(users)}")
        
        if users:
            print("\n   📋 قائمة المستخدمين:")
            for idx, u in enumerate(users, 1):
                print(f"      {idx}. البريد: {u.email}")
                print(f"         الاسم: {u.nickname}")
                print(f"         Tenant ID: {u.tenant_id}")
                print(f"         الحالة: {u.status}")
                print(f"         Admin: {u.is_superuser}")
        else:
            print("   ⚠️  لا توجد مستخدمين! قد تكون هناك مشكلة.")
            return False
    except Exception as e:
        print(f"   ❌ خطأ في الاستعلام: {e}")
        return False
    
    # النجاح!
    print("\n" + "="*60)
    print("🎉 تم إنشاء المستخدم بنجاح!")
    print("="*60)
    print("\n📝 بيانات تسجيل الدخول:")
    print(f"   📧 البريد الإلكتروني: admin@ragflow.io")
    print(f"   🔑 كلمة المرور: admin")
    print("\n💡 يمكنك الآن تسجيل الدخول على: http://YOUR_SERVER:8080")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
