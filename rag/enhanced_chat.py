"""
Enhanced Chat Features for RAGFlow Enterprise
Real-time collaboration, custom templates, and advanced interactions
"""
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class ChatMessage:
    """Enhanced chat message with metadata"""
    message_id: str
    conversation_id: str
    user_id: str
    content: str
    message_type: str  # user, assistant, system
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)  # Referenced document IDs
    reaction: Optional[str] = None  # thumbs_up, thumbs_down, etc.


@dataclass
class ConversationTemplate:
    """Reusable conversation template"""
    template_id: str
    name: str
    description: str
    system_prompt: str
    initial_messages: List[Dict[str, str]]
    parameters: Dict[str, Any]
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RealTimeCollaboration:
    """Real-time collaboration for shared conversations"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Set[str]] = defaultdict(set)  # conversation_id -> user_ids
        self.typing_indicators: Dict[str, Set[str]] = defaultdict(set)  # conversation_id -> typing users
    
    def join_session(self, conversation_id: str, user_id: str):
        """User joins a conversation session"""
        self.active_sessions[conversation_id].add(user_id)
        return {
            'conversation_id': conversation_id,
            'active_users': list(self.active_sessions[conversation_id]),
            'timestamp': datetime.now().isoformat()
        }
    
    def leave_session(self, conversation_id: str, user_id: str):
        """User leaves a conversation session"""
        self.active_sessions[conversation_id].discard(user_id)
        self.typing_indicators[conversation_id].discard(user_id)
        
        return {
            'conversation_id': conversation_id,
            'active_users': list(self.active_sessions[conversation_id])
        }
    
    def set_typing(self, conversation_id: str, user_id: str, is_typing: bool):
        """Update typing indicator"""
        if is_typing:
            self.typing_indicators[conversation_id].add(user_id)
        else:
            self.typing_indicators[conversation_id].discard(user_id)
        
        return {
            'conversation_id': conversation_id,
            'typing_users': list(self.typing_indicators[conversation_id])
        }
    
    def get_active_users(self, conversation_id: str) -> List[str]:
        """Get active users in conversation"""
        return list(self.active_sessions[conversation_id])


class TemplateManager:
    """Manage conversation templates"""
    
    def __init__(self):
        self.templates: Dict[str, ConversationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default conversation templates"""
        
        # Research Assistant Template
        self.create_template(
            template_id='research_assistant',
            name='Research Assistant',
            description='Helps with research and analysis tasks',
            system_prompt='You are a helpful research assistant. Provide detailed, well-researched answers with citations.',
            initial_messages=[
                {
                    'role': 'assistant',
                    'content': 'Hello! I\'m your research assistant. How can I help you today?'
                }
            ],
            parameters={
                'temperature': 0.7,
                'max_tokens': 2000,
                'enable_citations': True
            },
            created_by='system'
        )
        
        # Code Review Template
        self.create_template(
            template_id='code_review',
            name='Code Review Assistant',
            description='Reviews code and provides feedback',
            system_prompt='You are an expert code reviewer. Analyze code for bugs, performance issues, and best practices.',
            initial_messages=[
                {
                    'role': 'assistant',
                    'content': 'Ready to review your code. Please share the code you\'d like me to analyze.'
                }
            ],
            parameters={
                'temperature': 0.3,
                'max_tokens': 3000,
                'enable_syntax_highlighting': True
            },
            created_by='system'
        )
        
        # Document Summarization Template
        self.create_template(
            template_id='document_summary',
            name='Document Summarizer',
            description='Summarizes long documents',
            system_prompt='You are a document summarization expert. Create concise, accurate summaries.',
            initial_messages=[
                {
                    'role': 'assistant',
                    'content': 'I can help summarize your documents. Please upload or share the document you\'d like summarized.'
                }
            ],
            parameters={
                'temperature': 0.5,
                'max_tokens': 1000,
                'summary_style': 'bullet_points'
            },
            created_by='system'
        )
    
    def create_template(
        self,
        template_id: str,
        name: str,
        description: str,
        system_prompt: str,
        initial_messages: List[Dict[str, str]],
        parameters: Dict[str, Any],
        created_by: str
    ) -> ConversationTemplate:
        """Create a new template"""
        template = ConversationTemplate(
            template_id=template_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            initial_messages=initial_messages,
            parameters=parameters,
            created_by=created_by
        )
        
        self.templates[template_id] = template
        return template
    
    def get_template(self, template_id: str) -> Optional[ConversationTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(
        self,
        created_by: Optional[str] = None
    ) -> List[ConversationTemplate]:
        """List all templates"""
        templates = list(self.templates.values())
        
        if created_by:
            templates = [t for t in templates if t.created_by == created_by]
        
        return templates
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False


class ConversationManager:
    """Enhanced conversation management"""
    
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = defaultdict(list)
        self.conversation_metadata: Dict[str, Dict[str, Any]] = {}
    
    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        template_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new conversation"""
        self.conversation_metadata[conversation_id] = {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'template_id': template_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'message_count': 0,
            'metadata': metadata or {}
        }
        
        return self.conversation_metadata[conversation_id]
    
    def add_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str,
        message_type: str = 'user',
        metadata: Optional[Dict[str, Any]] = None,
        references: Optional[List[str]] = None
    ) -> ChatMessage:
        """Add message to conversation"""
        message_id = f"msg_{len(self.conversations[conversation_id]) + 1}"
        
        message = ChatMessage(
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
            references=references or []
        )
        
        self.conversations[conversation_id].append(message)
        
        # Update conversation metadata
        if conversation_id in self.conversation_metadata:
            self.conversation_metadata[conversation_id]['updated_at'] = datetime.now().isoformat()
            self.conversation_metadata[conversation_id]['message_count'] += 1
        
        return message
    
    def get_conversation_history(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get conversation history"""
        messages = self.conversations[conversation_id]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def search_conversations(
        self,
        user_id: str,
        query: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search user's conversations"""
        results = []
        
        for conv_id, metadata in self.conversation_metadata.items():
            if metadata['user_id'] != user_id:
                continue
            
            # Date filtering
            created_at = datetime.fromisoformat(metadata['created_at'])
            
            if start_date and created_at < datetime.fromisoformat(start_date):
                continue
            
            if end_date and created_at > datetime.fromisoformat(end_date):
                continue
            
            # Text search in messages
            if query:
                messages = self.conversations[conv_id]
                match_found = any(query.lower() in msg.content.lower() for msg in messages)
                if not match_found:
                    continue
            
            results.append(metadata)
        
        return sorted(results, key=lambda x: x['updated_at'], reverse=True)
    
    def add_reaction(
        self,
        conversation_id: str,
        message_id: str,
        reaction: str
    ) -> bool:
        """Add reaction to a message"""
        messages = self.conversations.get(conversation_id, [])
        
        for msg in messages:
            if msg.message_id == message_id:
                msg.reaction = reaction
                return True
        
        return False
    
    def export_conversation(
        self,
        conversation_id: str,
        format: str = 'json'  # json, markdown, txt
    ) -> str:
        """Export conversation in various formats"""
        messages = self.conversations.get(conversation_id, [])
        metadata = self.conversation_metadata.get(conversation_id, {})
        
        if format == 'json':
            return json.dumps({
                'metadata': metadata,
                'messages': [
                    {
                        'message_id': msg.message_id,
                        'user_id': msg.user_id,
                        'content': msg.content,
                        'timestamp': msg.timestamp,
                        'message_type': msg.message_type
                    }
                    for msg in messages
                ]
            }, indent=2)
        
        elif format == 'markdown':
            lines = [f"# Conversation {conversation_id}\n"]
            lines.append(f"Created: {metadata.get('created_at', 'Unknown')}\n\n")
            
            for msg in messages:
                lines.append(f"**{msg.message_type.title()}** ({msg.timestamp}):\n")
                lines.append(f"{msg.content}\n\n")
            
            return ''.join(lines)
        
        elif format == 'txt':
            lines = [f"Conversation {conversation_id}\n"]
            lines.append(f"{'='*50}\n\n")
            
            for msg in messages:
                lines.append(f"[{msg.timestamp}] {msg.message_type}: {msg.content}\n\n")
            
            return ''.join(lines)
        
        return ""


# Global instances
collaboration = RealTimeCollaboration()
template_manager = TemplateManager()
conversation_manager = ConversationManager()
