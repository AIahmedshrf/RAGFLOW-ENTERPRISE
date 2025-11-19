"""
Model Management API Routes
Endpoints for managing AI models, benchmarking, and versioning
"""
from flask import Blueprint, request
from api.model_management import ModelRegistry, ModelBenchmark, ModelVersionControl
from api.utils.api_utils import get_json_result, server_error_response
from api.utils import get_uuid
import traceback

model_bp = Blueprint('model_management', __name__, url_prefix='/api/v1/models')


@model_bp.route('/registry', methods=['GET'])
def get_all_models():
    """Get all registered models"""
    try:
        tenant_id = request.args.get('tenant_id')
        models = ModelRegistry.get_all_models(tenant_id)
        return get_json_result(data=models)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/registry/<model_id>', methods=['GET'])
def get_model_details(model_id: str):
    """Get specific model details"""
    try:
        model = ModelRegistry.get_model_by_id(model_id)
        if not model:
            return get_json_result(data=False, code=404, message='Model not found')
        return get_json_result(data=model)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/registry', methods=['POST'])
def register_model():
    """Register a new model"""
    try:
        data = request.json
        if not data or 'name' not in data or 'model_type' not in data:
            return get_json_result(data=False, code=400, message='Missing required fields')
        
        result = ModelRegistry.register_model(data)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/registry/<model_id>', methods=['PUT'])
def update_model(model_id: str):
    """Update model configuration"""
    try:
        data = request.json
        if not data:
            return get_json_result(data=False, code=400, message='No data provided')
        
        result = ModelRegistry.update_model(model_id, data)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/registry/<model_id>', methods=['DELETE'])
def delete_model(model_id: str):
    """Delete a model"""
    try:
        result = ModelRegistry.delete_model(model_id)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/benchmark/<model_id>/run', methods=['POST'])
def run_benchmark(model_id: str):
    """Run benchmark on a model"""
    try:
        data = request.json or {}
        test_type = data.get('test_type', 'latency')
        
        result = ModelBenchmark.run_benchmark(model_id, test_type)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/benchmark', methods=['GET'])
def get_benchmarks():
    """Get benchmark results"""
    try:
        model_id = request.args.get('model_id')
        limit = request.args.get('limit', 50, type=int)
        
        results = ModelBenchmark.get_benchmarks(model_id, limit)
        return get_json_result(data={'benchmarks': results, 'total': len(results)})
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/benchmark/compare', methods=['POST'])
def compare_models():
    """Compare multiple models"""
    try:
        data = request.json
        model_ids = data.get('model_ids', [])
        
        if not model_ids:
            return get_json_result(data=False, code=400, message='No model IDs provided')
        
        comparison = ModelBenchmark.compare_models(model_ids)
        return get_json_result(data=comparison)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/versions/<model_id>', methods=['GET'])
def get_model_versions(model_id: str):
    """Get all versions of a model"""
    try:
        versions = ModelVersionControl.get_versions(model_id)
        return get_json_result(data={'versions': versions, 'total': len(versions)})
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/versions/<model_id>', methods=['POST'])
def create_model_version(model_id: str):
    """Create a new model version"""
    try:
        data = request.json
        if not data:
            return get_json_result(data=False, code=400, message='No data provided')
        
        version = ModelVersionControl.create_version(model_id, data)
        return get_json_result(data=version)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/versions/<model_id>/<int:version_id>/activate', methods=['POST'])
def activate_model_version(model_id: str, version_id: int):
    """Activate a specific version"""
    try:
        result = ModelVersionControl.activate_version(model_id, version_id)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@model_bp.route('/versions/<model_id>/rollback', methods=['POST'])
def rollback_model_version(model_id: str):
    """Rollback to previous version"""
    try:
        result = ModelVersionControl.rollback_version(model_id)
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


# Export blueprint
__all__ = ['model_bp']
