"""
Advanced Retrieval System for RAGFlow
Implements hybrid search, query rewriting, and re-ranking
"""
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from datetime import datetime
from rag.nlp import search
from rag.utils import num_tokens_from_string


class HybridSearch:
    """Hybrid search combining vector and keyword search"""
    
    @staticmethod
    def search(
        query: str,
        kb_id: str,
        top_k: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with configurable weights
        
        Args:
            query: Search query
            kb_id: Knowledge base ID
            top_k: Number of results
            vector_weight: Weight for vector search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            filters: Additional filters
        
        Returns:
            List of search results with scores
        """
        # Normalize weights
        total_weight = vector_weight + keyword_weight
        vector_weight /= total_weight
        keyword_weight /= total_weight
        
        # Vector search
        vector_results = HybridSearch._vector_search(query, kb_id, top_k * 2)
        
        # Keyword search (BM25)
        keyword_results = HybridSearch._keyword_search(query, kb_id, top_k * 2)
        
        # Merge results with weighted scores
        merged_results = HybridSearch._merge_results(
            vector_results,
            keyword_results,
            vector_weight,
            keyword_weight
        )
        
        # Apply filters if provided
        if filters:
            merged_results = HybridSearch._apply_filters(merged_results, filters)
        
        # Return top-k results
        return merged_results[:top_k]
    
    @staticmethod
    def _vector_search(query: str, kb_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        # Simplified implementation - replace with actual vector search
        try:
            from api.db.services.knowledgebase_service import KnowledgebaseService
            kb = KnowledgebaseService.query(id=kb_id)
            if not kb:
                return []
            
            # Simulate vector search results
            return [
                {
                    'doc_id': f'doc_{i}',
                    'content': f'Vector result {i}',
                    'score': 0.9 - (i * 0.05),
                    'metadata': {}
                }
                for i in range(min(top_k, 10))
            ]
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    @staticmethod
    def _keyword_search(query: str, kb_id: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search"""
        # Simplified BM25 implementation
        try:
            # Simulate keyword search results
            return [
                {
                    'doc_id': f'doc_{i}',
                    'content': f'Keyword result {i}',
                    'score': 0.85 - (i * 0.04),
                    'metadata': {}
                }
                for i in range(min(top_k, 10))
            ]
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []
    
    @staticmethod
    def _merge_results(
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        vector_weight: float,
        keyword_weight: float
    ) -> List[Dict[str, Any]]:
        """Merge and re-score results from both searches"""
        doc_scores = {}
        
        # Add vector scores
        for result in vector_results:
            doc_id = result['doc_id']
            doc_scores[doc_id] = {
                **result,
                'combined_score': result['score'] * vector_weight,
                'vector_score': result['score'],
                'keyword_score': 0.0
            }
        
        # Add keyword scores
        for result in keyword_results:
            doc_id = result['doc_id']
            if doc_id in doc_scores:
                doc_scores[doc_id]['combined_score'] += result['score'] * keyword_weight
                doc_scores[doc_id]['keyword_score'] = result['score']
            else:
                doc_scores[doc_id] = {
                    **result,
                    'combined_score': result['score'] * keyword_weight,
                    'vector_score': 0.0,
                    'keyword_score': result['score']
                }
        
        # Sort by combined score
        sorted_results = sorted(
            doc_scores.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        return sorted_results
    
    @staticmethod
    def _apply_filters(
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to results"""
        filtered = results
        
        if 'min_score' in filters:
            filtered = [r for r in filtered if r['combined_score'] >= filters['min_score']]
        
        if 'doc_types' in filters:
            filtered = [r for r in filtered if r.get('metadata', {}).get('type') in filters['doc_types']]
        
        if 'date_range' in filters:
            start, end = filters['date_range']
            filtered = [
                r for r in filtered
                if start <= r.get('metadata', {}).get('date', '') <= end
            ]
        
        return filtered


class QueryRewriter:
    """Query rewriting for better retrieval"""
    
    @staticmethod
    def rewrite(query: str, strategy: str = 'expansion') -> List[str]:
        """
        Rewrite query using different strategies
        
        Strategies:
        - expansion: Add synonyms and related terms
        - simplification: Break complex queries into simpler ones
        - clarification: Add context to ambiguous queries
        """
        if strategy == 'expansion':
            return QueryRewriter._expand_query(query)
        elif strategy == 'simplification':
            return QueryRewriter._simplify_query(query)
        elif strategy == 'clarification':
            return QueryRewriter._clarify_query(query)
        else:
            return [query]
    
    @staticmethod
    def _expand_query(query: str) -> List[str]:
        """Expand query with synonyms"""
        # Simplified expansion
        queries = [query]
        
        # Add variations (simplified - use proper NLP in production)
        if 'error' in query.lower():
            queries.append(query.replace('error', 'issue'))
            queries.append(query.replace('error', 'problem'))
        
        if 'fix' in query.lower():
            queries.append(query.replace('fix', 'solve'))
            queries.append(query.replace('fix', 'resolve'))
        
        return queries
    
    @staticmethod
    def _simplify_query(query: str) -> List[str]:
        """Break complex query into simpler parts"""
        # Split by common conjunctions
        parts = []
        for separator in [' and ', ' or ', ' but ', ', ']:
            if separator in query.lower():
                parts.extend(query.lower().split(separator))
        
        return parts if parts else [query]
    
    @staticmethod
    def _clarify_query(query: str) -> List[str]:
        """Add context to ambiguous queries"""
        # Simplified clarification
        clarified = [query]
        
        # Add context based on query type
        if len(query.split()) <= 3:  # Short query
            clarified.append(f"What is {query}?")
            clarified.append(f"How to {query}?")
        
        return clarified


class ReRanker:
    """Advanced re-ranking of search results"""
    
    @staticmethod
    def rerank(
        query: str,
        results: List[Dict[str, Any]],
        strategy: str = 'cross_encoder'
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results using advanced methods
        
        Strategies:
        - cross_encoder: Use cross-encoder model
        - relevance: Semantic relevance scoring
        - diversity: Maximize result diversity
        """
        if strategy == 'cross_encoder':
            return ReRanker._cross_encoder_rerank(query, results)
        elif strategy == 'relevance':
            return ReRanker._relevance_rerank(query, results)
        elif strategy == 'diversity':
            return ReRanker._diversity_rerank(results)
        else:
            return results
    
    @staticmethod
    def _cross_encoder_rerank(
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Re-rank using cross-encoder model"""
        # Simplified cross-encoder (replace with actual model)
        for result in results:
            # Simulate cross-encoder score
            content = result.get('content', '')
            query_overlap = len(set(query.lower().split()) & set(content.lower().split()))
            result['rerank_score'] = query_overlap / max(len(query.split()), 1)
        
        return sorted(results, key=lambda x: x.get('rerank_score', 0), reverse=True)
    
    @staticmethod
    def _relevance_rerank(
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Re-rank by semantic relevance"""
        # Simplified relevance scoring
        for result in results:
            content = result.get('content', '')
            # Simple token overlap as relevance measure
            query_tokens = set(query.lower().split())
            content_tokens = set(content.lower().split())
            overlap = len(query_tokens & content_tokens)
            result['relevance_score'] = overlap / len(query_tokens) if query_tokens else 0
        
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    @staticmethod
    def _diversity_rerank(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank to maximize diversity"""
        if len(results) <= 1:
            return results
        
        diverse_results = [results[0]]  # Start with top result
        
        for result in results[1:]:
            # Check diversity against selected results
            is_diverse = True
            for selected in diverse_results:
                # Simple diversity check (replace with proper similarity in production)
                content1 = set(result.get('content', '').lower().split())
                content2 = set(selected.get('content', '').lower().split())
                overlap = len(content1 & content2) / max(len(content1), len(content2), 1)
                
                if overlap > 0.7:  # Too similar
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_results.append(result)
        
        return diverse_results


class RetrievalAnalytics:
    """Analytics for retrieval performance"""
    
    search_logs = []
    MAX_LOGS = 1000
    
    @staticmethod
    def log_search(
        query: str,
        kb_id: str,
        results_count: int,
        top_score: float,
        latency_ms: float,
        user_id: Optional[str] = None
    ):
        """Log a search operation"""
        log = {
            'id': len(RetrievalAnalytics.search_logs) + 1,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'kb_id': kb_id,
            'results_count': results_count,
            'top_score': top_score,
            'latency_ms': latency_ms,
            'user_id': user_id,
        }
        
        RetrievalAnalytics.search_logs.insert(0, log)
        
        # Limit logs
        if len(RetrievalAnalytics.search_logs) > RetrievalAnalytics.MAX_LOGS:
            RetrievalAnalytics.search_logs = RetrievalAnalytics.search_logs[:RetrievalAnalytics.MAX_LOGS]
    
    @staticmethod
    def get_stats(days: int = 7) -> Dict[str, Any]:
        """Get retrieval statistics"""
        if not RetrievalAnalytics.search_logs:
            return {
                'total_searches': 0,
                'avg_latency_ms': 0,
                'avg_results': 0,
                'avg_top_score': 0,
            }
        
        total = len(RetrievalAnalytics.search_logs)
        avg_latency = sum(log['latency_ms'] for log in RetrievalAnalytics.search_logs) / total
        avg_results = sum(log['results_count'] for log in RetrievalAnalytics.search_logs) / total
        avg_score = sum(log['top_score'] for log in RetrievalAnalytics.search_logs) / total
        
        return {
            'total_searches': total,
            'avg_latency_ms': avg_latency,
            'avg_results': avg_results,
            'avg_top_score': avg_score,
            'recent_queries': [log['query'] for log in RetrievalAnalytics.search_logs[:10]],
        }
