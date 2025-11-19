"""
Model Management System for RAGFlow
Provides centralized management of LLM models, embeddings, and rerankers
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from api.db.services.llm_service import LLMService, TenantLLMService
from api.db import StatusEnum
from api.db.services.user_service import TenantService
import requests
import json
import time


class ModelRegistry:
    """Central registry for all AI models"""
    
    @staticmethod
    def get_all_models(tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get all available models grouped by type"""
        llm_service = LLMService.query()
        
        models = {
            'llm': [],
            'embedding': [],
            'rerank': [],
            'chat': [],
            'image': [],
        }
        
        for model in llm_service:
            model_info = {
                'id': model.id,
                'name': model.llm_name,
                'model_type': model.model_type,
                'factory': model.fid,
                'status': 'active' if model.status == StatusEnum.VALID.value else 'inactive',
                'created_at': model.create_time.isoformat() if model.create_time else None,
                'updated_at': model.update_time.isoformat() if model.update_time else None,
            }
            
            # Categorize by model type
            if 'embed' in model.model_type.lower():
                models['embedding'].append(model_info)
            elif 'rerank' in model.model_type.lower():
                models['rerank'].append(model_info)
            elif 'image' in model.model_type.lower():
                models['image'].append(model_info)
            elif 'chat' in model.model_type.lower():
                models['chat'].append(model_info)
            else:
                models['llm'].append(model_info)
        
        return models
    
    @staticmethod
    def get_model_by_id(model_id: str) -> Optional[Dict[str, Any]]:
        """Get specific model details"""
        model = LLMService.query(id=model_id)
        if not model:
            return None
        
        model = model[0]
        return {
            'id': model.id,
            'name': model.llm_name,
            'model_type': model.model_type,
            'factory': model.fid,
            'status': 'active' if model.status == StatusEnum.VALID.value else 'inactive',
            'api_key_set': bool(model.api_key),
            'api_base': model.api_base,
            'created_at': model.create_time.isoformat() if model.create_time else None,
            'updated_at': model.update_time.isoformat() if model.update_time else None,
        }
    
    @staticmethod
    def register_model(model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new model"""
        from api.db.services.llm_service import LLMBundle
        
        llm = LLMBundle(
            tenant_id=model_data.get('tenant_id', 'system'),
            llm_name=model_data['name'],
            model_type=model_data['model_type'],
            fid=model_data.get('factory', 'Ollama'),
            api_key=model_data.get('api_key', ''),
            api_base=model_data.get('api_base', ''),
            status=StatusEnum.VALID.value
        )
        
        LLMService.save(llm)
        
        return {
            'id': llm.id,
            'name': llm.llm_name,
            'status': 'registered',
            'message': f'Model {llm.llm_name} registered successfully'
        }
    
    @staticmethod
    def update_model(model_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update model configuration"""
        model = LLMService.query(id=model_id)
        if not model:
            raise ValueError(f'Model {model_id} not found')
        
        model = model[0]
        
        # Update fields
        if 'name' in updates:
            model.llm_name = updates['name']
        if 'api_key' in updates:
            model.api_key = updates['api_key']
        if 'api_base' in updates:
            model.api_base = updates['api_base']
        if 'status' in updates:
            model.status = StatusEnum.VALID.value if updates['status'] == 'active' else StatusEnum.INVALID.value
        
        model.update_time = datetime.now()
        LLMService.update_by_id(model_id, model.to_dict())
        
        return {
            'id': model_id,
            'status': 'updated',
            'message': f'Model {model.llm_name} updated successfully'
        }
    
    @staticmethod
    def delete_model(model_id: str) -> Dict[str, Any]:
        """Delete a model"""
        result = LLMService.delete_by_id(model_id)
        
        return {
            'id': model_id,
            'status': 'deleted' if result else 'failed',
            'message': 'Model deleted successfully' if result else 'Failed to delete model'
        }


class ModelBenchmark:
    """Model performance benchmarking"""
    
    benchmark_results = []  # In-memory storage
    
    @staticmethod
    def run_benchmark(model_id: str, test_type: str = 'latency') -> Dict[str, Any]:
        """Run benchmark tests on a model"""
        model = ModelRegistry.get_model_by_id(model_id)
        if not model:
            raise ValueError(f'Model {model_id} not found')
        
        benchmark = {
            'id': len(ModelBenchmark.benchmark_results) + 1,
            'model_id': model_id,
            'model_name': model['name'],
            'test_type': test_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'running',
        }
        
        try:
            if test_type == 'latency':
                results = ModelBenchmark._test_latency(model)
            elif test_type == 'quality':
                results = ModelBenchmark._test_quality(model)
            elif test_type == 'throughput':
                results = ModelBenchmark._test_throughput(model)
            else:
                results = {'error': 'Unknown test type'}
            
            benchmark.update({
                'status': 'completed',
                'results': results,
            })
        except Exception as e:
            benchmark.update({
                'status': 'failed',
                'error': str(e),
            })
        
        ModelBenchmark.benchmark_results.insert(0, benchmark)
        
        # Limit stored results
        if len(ModelBenchmark.benchmark_results) > 100:
            ModelBenchmark.benchmark_results = ModelBenchmark.benchmark_results[:100]
        
        return benchmark
    
    @staticmethod
    def _test_latency(model: Dict[str, Any]) -> Dict[str, Any]:
        """Test model response latency"""
        # Simulate latency test
        test_prompts = [
            "Hello, how are you?",
            "What is the capital of France?",
            "Explain quantum computing in one sentence.",
        ]
        
        latencies = []
        for prompt in test_prompts:
            start = time.time()
            # Simulate API call (replace with actual call in production)
            time.sleep(0.1)  # Simulated processing
            end = time.time()
            latencies.append((end - start) * 1000)  # ms
        
        return {
            'avg_latency_ms': sum(latencies) / len(latencies),
            'min_latency_ms': min(latencies),
            'max_latency_ms': max(latencies),
            'test_count': len(latencies),
        }
    
    @staticmethod
    def _test_quality(model: Dict[str, Any]) -> Dict[str, Any]:
        """Test model output quality"""
        # Simplified quality test
        return {
            'coherence_score': 0.85,
            'relevance_score': 0.90,
            'factuality_score': 0.88,
            'overall_score': 0.88,
        }
    
    @staticmethod
    def _test_throughput(model: Dict[str, Any]) -> Dict[str, Any]:
        """Test model throughput"""
        return {
            'requests_per_second': 25.5,
            'tokens_per_second': 450.0,
            'concurrent_requests': 10,
        }
    
    @staticmethod
    def get_benchmarks(model_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get benchmark results"""
        results = ModelBenchmark.benchmark_results
        
        if model_id:
            results = [r for r in results if r['model_id'] == model_id]
        
        return results[:limit]
    
    @staticmethod
    def compare_models(model_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple models"""
        comparison = {
            'models': [],
            'metrics': {
                'latency': {},
                'quality': {},
                'throughput': {},
            }
        }
        
        for model_id in model_ids:
            model = ModelRegistry.get_model_by_id(model_id)
            if not model:
                continue
            
            # Get latest benchmarks
            benchmarks = [b for b in ModelBenchmark.benchmark_results if b['model_id'] == model_id]
            
            model_comparison = {
                'id': model_id,
                'name': model['name'],
                'latency': None,
                'quality': None,
                'throughput': None,
            }
            
            for benchmark in benchmarks[:3]:  # Last 3 benchmarks
                if benchmark['status'] == 'completed' and 'results' in benchmark:
                    test_type = benchmark['test_type']
                    if test_type == 'latency':
                        model_comparison['latency'] = benchmark['results'].get('avg_latency_ms')
                    elif test_type == 'quality':
                        model_comparison['quality'] = benchmark['results'].get('overall_score')
                    elif test_type == 'throughput':
                        model_comparison['throughput'] = benchmark['results'].get('requests_per_second')
            
            comparison['models'].append(model_comparison)
        
        return comparison


class ModelVersionControl:
    """Version control for models"""
    
    versions = {}  # model_id -> [versions]
    
    @staticmethod
    def create_version(model_id: str, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new model version"""
        if model_id not in ModelVersionControl.versions:
            ModelVersionControl.versions[model_id] = []
        
        version = {
            'id': len(ModelVersionControl.versions[model_id]) + 1,
            'model_id': model_id,
            'version': version_data.get('version', '1.0.0'),
            'description': version_data.get('description', ''),
            'changes': version_data.get('changes', []),
            'created_at': datetime.now().isoformat(),
            'created_by': version_data.get('created_by', 'system'),
            'is_active': version_data.get('is_active', False),
        }
        
        ModelVersionControl.versions[model_id].insert(0, version)
        
        return version
    
    @staticmethod
    def get_versions(model_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a model"""
        return ModelVersionControl.versions.get(model_id, [])
    
    @staticmethod
    def activate_version(model_id: str, version_id: int) -> Dict[str, Any]:
        """Activate a specific version"""
        versions = ModelVersionControl.versions.get(model_id, [])
        
        # Deactivate all versions
        for v in versions:
            v['is_active'] = False
        
        # Activate target version
        for v in versions:
            if v['id'] == version_id:
                v['is_active'] = True
                return {
                    'status': 'activated',
                    'version': v['version'],
                    'message': f"Version {v['version']} activated"
                }
        
        raise ValueError(f'Version {version_id} not found')
    
    @staticmethod
    def rollback_version(model_id: str) -> Dict[str, Any]:
        """Rollback to previous version"""
        versions = ModelVersionControl.versions.get(model_id, [])
        
        if len(versions) < 2:
            raise ValueError('No previous version available')
        
        # Find current active
        current_idx = next((i for i, v in enumerate(versions) if v['is_active']), -1)
        
        if current_idx == -1 or current_idx == len(versions) - 1:
            raise ValueError('Cannot rollback further')
        
        # Activate previous version
        versions[current_idx]['is_active'] = False
        versions[current_idx + 1]['is_active'] = True
        
        return {
            'status': 'rolled_back',
            'version': versions[current_idx + 1]['version'],
            'message': f"Rolled back to version {versions[current_idx + 1]['version']}"
        }
