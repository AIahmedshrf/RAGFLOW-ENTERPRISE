#!/bin/bash
# سكريبت مراقبة RAGFlow
# الاستخدام: ./monitor_ragflow.sh

echo "🔄 مراقبة RAGFlow - اضغط Ctrl+C للخروج"
echo "========================================"

while true; do
    clear
    echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================"
    echo ""
    
    echo "📦 حالة الحاويات:"
    echo "----------------"
    docker compose --profile cpu ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | head -10
    echo ""
    
    echo "💻 استخدام الموارد:"
    echo "----------------"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -10
    echo ""
    
    echo "🌐 المنافذ المفتوحة:"
    echo "----------------"
    echo "✓ واجهة RAGFlow: http://localhost:8080"
    echo "✓ API الداخلي: http://localhost:9380"
    echo "✓ TEI Embeddings: http://localhost:6380"
    echo "✓ Elasticsearch: http://localhost:1200"
    echo "✓ MySQL: localhost:5455"
    echo "✓ Redis: localhost:6379"
    echo "✓ MinIO: http://localhost:9000"
    echo "✓ MinIO Console: http://localhost:9001"
    echo ""
    
    echo "🧪 اختبارات الصحة:"
    echo "----------------"
    
    # اختبار TEI
    if curl -s http://localhost:6380/ > /dev/null 2>&1; then
        echo "✅ TEI: يعمل"
    else
        echo "❌ TEI: لا يستجيب"
    fi
    
    # اختبار Elasticsearch
    if curl -u elastic:ragflow_es_password123 -s http://localhost:1200 > /dev/null 2>&1; then
        echo "✅ Elasticsearch: يعمل"
    else
        echo "❌ Elasticsearch: لا يستجيب"
    fi
    
    # اختبار RAGFlow
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "✅ RAGFlow UI: يعمل"
    else
        echo "❌ RAGFlow UI: لا يستجيب"
    fi
    
    echo ""
    echo "⏳ التحديث التالي بعد 10 ثوانٍ..."
    sleep 10
done
