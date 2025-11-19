"""
Multi-Agent Orchestration API Routes
"""
from flask import Blueprint, request
from agent.orchestration import orchestrator, Agent, AgentType
from api.utils.api_utils import get_json_result, server_error_response
import asyncio
import traceback

agent_orch_bp = Blueprint('agent_orchestration', __name__, url_prefix='/api/v1/orchestration')


@agent_orch_bp.route('/agents', methods=['GET'])
def get_agents():
    """Get all registered agents"""
    try:
        status = orchestrator.get_agent_status()
        return get_json_result(data=status)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/agents', methods=['POST'])
def register_agent():
    """Register a new agent"""
    try:
        data = request.json
        agent = Agent(
            agent_id=data['agent_id'],
            agent_type=AgentType(data['agent_type']),
            name=data['name'],
            capabilities=data['capabilities'],
            model_id=data.get('model_id')
        )
        
        orchestrator.register_agent(agent)
        
        return get_json_result(data={
            'message': 'Agent registered successfully',
            'agent': agent.to_dict()
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/agents/<agent_id>', methods=['DELETE'])
def unregister_agent(agent_id: str):
    """Unregister an agent"""
    try:
        orchestrator.unregister_agent(agent_id)
        return get_json_result(data={'message': 'Agent unregistered successfully'})
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        task_id = request.args.get('task_id')
        status = orchestrator.get_task_status(task_id)
        return get_json_result(data=status)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.json
        task = orchestrator.create_task(
            task_type=data['task_type'],
            description=data['description'],
            input_data=data.get('input_data', {}),
            priority=data.get('priority', 5),
            dependencies=data.get('dependencies')
        )
        
        return get_json_result(data={
            'message': 'Task created successfully',
            'task': task.to_dict()
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/tasks/<task_id>/execute', methods=['POST'])
def execute_task(task_id: str):
    """Execute a task"""
    try:
        # Run async task in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.execute_task(task_id))
        loop.close()
        
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/workflows', methods=['GET'])
def get_workflows():
    """Get all workflows"""
    try:
        workflow_id = request.args.get('workflow_id')
        status = orchestrator.get_workflow_status(workflow_id)
        return get_json_result(data=status)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/workflows', methods=['POST'])
def create_workflow():
    """Create a new workflow"""
    try:
        data = request.json
        workflow_id = orchestrator.create_workflow(
            name=data['name'],
            description=data['description'],
            tasks=data['tasks']
        )
        
        return get_json_result(data={
            'message': 'Workflow created successfully',
            'workflow_id': workflow_id
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id: str):
    """Execute a workflow"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.execute_workflow(workflow_id))
        loop.close()
        
        return get_json_result(data=result)
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@agent_orch_bp.route('/history', methods=['GET'])
def get_execution_history():
    """Get execution history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = orchestrator.get_execution_history(limit)
        
        return get_json_result(data={
            'history': history,
            'total': len(history)
        })
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


__all__ = ['agent_orch_bp']
