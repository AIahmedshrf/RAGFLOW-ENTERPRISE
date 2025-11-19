"""
Advanced Retrieval API Routes
Endpoints for hybrid search, query rewriting, and analytics
"""
from flask import Blueprint, request
from rag.advanced_retrieval import HybridSearch, QueryRewriter, ReRanker, RetrievalAnalytics
from api.utils.api_utils import get_json_result, server_error_response
import time
import traceback

retrieval_bp = Blueprint('advanced_retrieval', __name__, url_prefix='/api/v1/retrieval')


@retrieval_bp.route('/hybrid-search', methods=['POST'])
def hybrid_search():
    """Perform hybrid search"""
    try:
        data = request.json
        query = data.get('query')
        kb_id = data.get('kb_id')
        
        if not query or not kb_id:
            return get_json_result(data=False, code=400, message='Missing query or kb_id')
        
        top_k = data.get('top_k', 10)
        vector_weight = data.get('vector_weight', 0.7)
        keyword_weight = data.get('keyword_weight', 0.3)
        filters = data.get('filters')
        
        start_time = time.time()
        results = HybridSearch.search(
            query=query,
            kb_id=kb_id,
            top_k=top_k,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight,
            filters=filters
        )
        latency = (time.time() - start_time) * 1000
        
        # Log search
        RetrievalAnalytics.log_search(
            query=query,
            kb_id=kb_id,
            results_count=len(results),
            top_score=results[0]['combined_score'] if results else 0,
            latency_ms=latency,
            user_id=data.get('user_id')
        )
        
        return get_json_result(data={
            'results': results,
            'total': len(results),
            'latency_ms': latency
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@retrieval_bp.route('/query/rewrite', methods=['POST'])
def rewrite_query():
    """Rewrite query for better retrieval"""
    try:
        data = request.json
        query = data.get('query')
        strategy = data.get('strategy', 'expansion')
        
        if not query:
            return get_json_result(data=False, code=400, message='Missing query')
        
        rewritten_queries = QueryRewriter.rewrite(query, strategy)
        
        return get_json_result(data={
            'original': query,
            'rewritten': rewritten_queries,
            'strategy': strategy
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@retrieval_bp.route('/rerank', methods=['POST'])
def rerank_results():
    """Re-rank search results"""
    try:
        data = request.json
        query = data.get('query')
        results = data.get('results', [])
        strategy = data.get('strategy', 'cross_encoder')
        
        if not query or not results:
            return get_json_result(data=False, code=400, message='Missing query or results')
        
        reranked = ReRanker.rerank(query, results, strategy)
        
        return get_json_result(data={
            'results': reranked,
            'total': len(reranked),
            'strategy': strategy
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@retrieval_bp.route('/analytics/stats', methods=['GET'])
def get_retrieval_stats():
    """Get retrieval analytics"""
    try:
        days = request.args.get('days', 7, type=int)
        stats = RetrievalAnalytics.get_stats(days)
        
        return get_json_result(data=stats)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@retrieval_bp.route('/analytics/logs', methods=['GET'])
def get_search_logs():
    """Get search logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = RetrievalAnalytics.search_logs[:limit]
        
        return get_json_result(data={
            'logs': logs,
            'total': len(logs)
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


# Export blueprint
__all__ = ['retrieval_bp']
