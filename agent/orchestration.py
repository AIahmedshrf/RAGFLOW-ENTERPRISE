"""
Multi-Agent Orchestration System
Coordinates multiple AI agents for complex tasks
"""
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import asyncio
import json
from threading import Thread, Lock


class AgentType(Enum):
    """Types of agents"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CODING = "coding"
    PLANNING = "planning"
    VERIFICATION = "verification"
    CUSTOM = "custom"


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent:
    """Individual AI agent"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str,
        capabilities: List[str],
        model_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities
        self.model_id = model_id
        self.status = "idle"
        self.current_task = None
    
    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a task type"""
        return task_type in self.capabilities
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        self.status = "busy"
        self.current_task = task
        
        try:
            # Simulate task execution
            await asyncio.sleep(1)  # Replace with actual execution
            
            result = {
                'agent_id': self.agent_id,
                'agent_name': self.name,
                'task_id': task.get('id'),
                'result': f"Completed task: {task.get('description')}",
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
        except Exception as e:
            return {
                'agent_id': self.agent_id,
                'task_id': task.get('id'),
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
        finally:
            self.status = "idle"
            self.current_task = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'name': self.name,
            'capabilities': self.capabilities,
            'model_id': self.model_id,
            'status': self.status,
            'current_task': self.current_task
        }


class Task:
    """Task to be executed"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        description: str,
        input_data: Dict[str, Any],
        priority: int = 5,
        dependencies: Optional[List[str]] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.input_data = input_data
        self.priority = priority
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.assigned_agent = None
        self.result = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'description': self.description,
            'priority': self.priority,
            'status': self.status.value,
            'assigned_agent': self.assigned_agent,
            'result': self.result,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Orchestrator:
    """Main orchestrator for multi-agent system"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.lock = Lock()
    
    def register_agent(self, agent: Agent):
        """Register an agent"""
        with self.lock:
            self.agents[agent.agent_id] = agent
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        with self.lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
    
    def create_task(
        self,
        task_type: str,
        description: str,
        input_data: Dict[str, Any],
        priority: int = 5,
        dependencies: Optional[List[str]] = None
    ) -> Task:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1}"
        task = Task(task_id, task_type, description, input_data, priority, dependencies)
        
        with self.lock:
            self.tasks[task_id] = task
        
        return task
    
    def assign_task(self, task_id: str) -> Optional[Agent]:
        """Assign task to best available agent"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # Check dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    return None  # Dependencies not met
        
        # Find capable and idle agent
        with self.lock:
            for agent in self.agents.values():
                if agent.status == "idle" and agent.can_handle(task.task_type):
                    task.assigned_agent = agent.agent_id
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    return agent
        
        return None
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a single task"""
        task = self.tasks.get(task_id)
        if not task:
            return {'error': 'Task not found'}
        
        agent = self.assign_task(task_id)
        if not agent:
            return {'error': 'No available agent'}
        
        # Execute task
        result = await agent.execute(task.to_dict())
        
        # Update task
        with self.lock:
            task.result = result
            task.status = TaskStatus.COMPLETED if result.get('status') == 'success' else TaskStatus.FAILED
            task.completed_at = datetime.now()
        
        # Log execution
        self.execution_history.append({
            'task_id': task_id,
            'agent_id': agent.agent_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow with multiple tasks"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'error': 'Workflow not found'}
        
        tasks = workflow.get('tasks', [])
        results = []
        
        for task_config in tasks:
            task = self.create_task(
                task_type=task_config['type'],
                description=task_config['description'],
                input_data=task_config.get('input', {}),
                priority=task_config.get('priority', 5),
                dependencies=task_config.get('dependencies')
            )
            
            result = await self.execute_task(task.task_id)
            results.append(result)
        
        return {
            'workflow_id': workflow_id,
            'results': results,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
    
    def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]]
    ) -> str:
        """Create a new workflow"""
        workflow_id = f"workflow_{len(self.workflows) + 1}"
        
        workflow = {
            'workflow_id': workflow_id,
            'name': name,
            'description': description,
            'tasks': tasks,
            'created_at': datetime.now().isoformat()
        }
        
        with self.lock:
            self.workflows[workflow_id] = workflow
        
        return workflow_id
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        with self.lock:
            return {
                'total_agents': len(self.agents),
                'idle_agents': sum(1 for a in self.agents.values() if a.status == "idle"),
                'busy_agents': sum(1 for a in self.agents.values() if a.status == "busy"),
                'agents': [a.to_dict() for a in self.agents.values()]
            }
    
    def get_task_status(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Get task status"""
        if task_id:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else {'error': 'Task not found'}
        
        with self.lock:
            return {
                'total_tasks': len(self.tasks),
                'pending': sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                'running': sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING),
                'completed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                'failed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
                'tasks': [t.to_dict() for t in self.tasks.values()]
            }
    
    def get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow status"""
        if workflow_id:
            workflow = self.workflows.get(workflow_id)
            return workflow if workflow else {'error': 'Workflow not found'}
        
        with self.lock:
            return {
                'total_workflows': len(self.workflows),
                'workflows': list(self.workflows.values())
            }
    
    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history[-limit:]


# Global orchestrator instance
orchestrator = Orchestrator()

# Register default agents
default_agents = [
    Agent("agent_research_1", AgentType.RESEARCH, "Research Agent 1", ["research", "search", "summarize"]),
    Agent("agent_analysis_1", AgentType.ANALYSIS, "Analysis Agent 1", ["analysis", "compare", "evaluate"]),
    Agent("agent_writing_1", AgentType.WRITING, "Writing Agent 1", ["writing", "editing", "formatting"]),
    Agent("agent_coding_1", AgentType.CODING, "Coding Agent 1", ["coding", "debugging", "testing"]),
]

for agent in default_agents:
    orchestrator.register_agent(agent)
