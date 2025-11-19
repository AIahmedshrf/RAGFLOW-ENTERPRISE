"""
Enhanced Chat API Routes
"""
from flask import Blueprint, request
from rag.enhanced_chat import collaboration, template_manager, conversation_manager
from api.security import require_api_key, rate_limit


chat_bp = Blueprint('enhanced_chat', __name__, url_prefix='/api/v1/chat')


# Real-time Collaboration
@chat_bp.route('/sessions/<conversation_id>/join', methods=['POST'])
@require_api_key
@rate_limit('basic')
def join_session(conversation_id):
    """Join a conversation session"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        
        result = collaboration.join_session(conversation_id, user_id)
        
        return {
            'success': True,
            'session': result
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/sessions/<conversation_id>/leave', methods=['POST'])
@require_api_key
@rate_limit('basic')
def leave_session(conversation_id):
    """Leave a conversation session"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        
        result = collaboration.leave_session(conversation_id, user_id)
        
        return {
            'success': True,
            'session': result
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/sessions/<conversation_id>/typing', methods=['POST'])
@require_api_key
@rate_limit('basic')
def set_typing(conversation_id):
    """Set typing indicator"""
    try:
        data = request.get_json()
        user_id = data['user_id']
        is_typing = data['is_typing']
        
        result = collaboration.set_typing(conversation_id, user_id, is_typing)
        
        return {
            'success': True,
            'typing': result
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/sessions/<conversation_id>/users', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_active_users(conversation_id):
    """Get active users in conversation"""
    users = collaboration.get_active_users(conversation_id)
    
    return {
        'success': True,
        'active_users': users,
        'total': len(users)
    }


# Templates
@chat_bp.route('/templates', methods=['POST'])
@require_api_key
@rate_limit('professional')
def create_template():
    """Create conversation template"""
    try:
        data = request.get_json()
        
        template = template_manager.create_template(
            template_id=data['template_id'],
            name=data['name'],
            description=data['description'],
            system_prompt=data['system_prompt'],
            initial_messages=data['initial_messages'],
            parameters=data['parameters'],
            created_by=data['created_by']
        )
        
        return {
            'success': True,
            'template': {
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'created_at': template.created_at
            }
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/templates', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_templates():
    """List conversation templates"""
    created_by = request.args.get('created_by')
    
    templates = template_manager.list_templates(created_by)
    
    return {
        'success': True,
        'templates': [
            {
                'template_id': t.template_id,
                'name': t.name,
                'description': t.description,
                'created_by': t.created_by,
                'created_at': t.created_at
            }
            for t in templates
        ],
        'total': len(templates)
    }


@chat_bp.route('/templates/<template_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_template(template_id):
    """Get template details"""
    template = template_manager.get_template(template_id)
    
    if not template:
        return {'error': 'Template not found', 'code': 404}, 404
    
    return {
        'success': True,
        'template': {
            'template_id': template.template_id,
            'name': template.name,
            'description': template.description,
            'system_prompt': template.system_prompt,
            'initial_messages': template.initial_messages,
            'parameters': template.parameters,
            'created_by': template.created_by,
            'created_at': template.created_at
        }
    }


@chat_bp.route('/templates/<template_id>', methods=['DELETE'])
@require_api_key
@rate_limit('professional')
def delete_template(template_id):
    """Delete a template"""
    success = template_manager.delete_template(template_id)
    
    if not success:
        return {'error': 'Template not found', 'code': 404}, 404
    
    return {'success': True, 'message': 'Template deleted'}


# Conversations
@chat_bp.route('/conversations', methods=['POST'])
@require_api_key
@rate_limit('basic')
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        
        conversation = conversation_manager.create_conversation(
            conversation_id=data['conversation_id'],
            user_id=data['user_id'],
            template_id=data.get('template_id'),
            metadata=data.get('metadata')
        )
        
        return {
            'success': True,
            'conversation': conversation
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@require_api_key
@rate_limit('basic')
def add_message(conversation_id):
    """Add message to conversation"""
    try:
        data = request.get_json()
        
        message = conversation_manager.add_message(
            conversation_id=conversation_id,
            user_id=data['user_id'],
            content=data['content'],
            message_type=data.get('message_type', 'user'),
            metadata=data.get('metadata'),
            references=data.get('references')
        )
        
        return {
            'success': True,
            'message': {
                'message_id': message.message_id,
                'content': message.content,
                'message_type': message.message_type,
                'timestamp': message.timestamp
            }
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/conversations/<conversation_id>/history', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_history(conversation_id):
    """Get conversation history"""
    limit = request.args.get('limit', type=int)
    
    messages = conversation_manager.get_conversation_history(
        conversation_id=conversation_id,
        limit=limit
    )
    
    return {
        'success': True,
        'messages': [
            {
                'message_id': m.message_id,
                'user_id': m.user_id,
                'content': m.content,
                'message_type': m.message_type,
                'timestamp': m.timestamp,
                'references': m.references,
                'reaction': m.reaction
            }
            for m in messages
        ],
        'total': len(messages)
    }


@chat_bp.route('/conversations/search', methods=['POST'])
@require_api_key
@rate_limit('basic')
def search_conversations():
    """Search conversations"""
    try:
        data = request.get_json()
        
        results = conversation_manager.search_conversations(
            user_id=data['user_id'],
            query=data.get('query'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        
        return {
            'success': True,
            'conversations': results,
            'total': len(results)
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/conversations/<conversation_id>/messages/<message_id>/reaction', methods=['POST'])
@require_api_key
@rate_limit('basic')
def add_reaction(conversation_id, message_id):
    """Add reaction to message"""
    try:
        data = request.get_json()
        reaction = data['reaction']
        
        success = conversation_manager.add_reaction(
            conversation_id=conversation_id,
            message_id=message_id,
            reaction=reaction
        )
        
        if not success:
            return {'error': 'Message not found', 'code': 404}, 404
        
        return {'success': True, 'message': 'Reaction added'}
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@chat_bp.route('/conversations/<conversation_id>/export', methods=['POST'])
@require_api_key
@rate_limit('professional')
def export_conversation(conversation_id):
    """Export conversation"""
    try:
        data = request.get_json()
        format = data.get('format', 'json')
        
        exported = conversation_manager.export_conversation(
            conversation_id=conversation_id,
            format=format
        )
        
        return {
            'success': True,
            'format': format,
            'data': exported
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400
