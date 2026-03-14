"""
Conversation Manager - State Management
Manages conversation state, context, and history for Gemini agent
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os


class ConversationManager:
    """Manage conversation state and context for scraping sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.current_session_id: Optional[str] = None
        self.max_history_length = 100
        self.context_window = 10  # Last N messages for context
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """Create a new conversation session"""
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        self.sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'context': {
                'url': None,
                'fields': [],
                'status': 'idle',
                'data_extracted': 0
            },
            'metadata': {
                'total_messages': 0,
                'interruptions': 0,
                'last_activity': None
            }
        }
        
        self.current_session_id = session_id
        return session_id
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Add a message to the current session"""
        if not self.current_session_id:
            self.create_session()
        
        session = self.sessions[self.current_session_id]
        
        message = {
            'id': len(session['messages']),
            'role': role,  # 'user' or 'assistant'
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        session['messages'].append(message)
        session['metadata']['total_messages'] += 1
        session['metadata']['last_activity'] = datetime.now().isoformat()
        
        # Trim history if needed
        if len(session['messages']) > self.max_history_length:
            session['messages'] = session['messages'][-self.max_history_length:]
        
        return message
    
    def update_context(self, key: str, value: Any) -> None:
        """Update scraping context for current session"""
        if not self.current_session_id:
            return
        
        session = self.sessions[self.current_session_id]
        session['context'][key] = value
        session['context']['last_updated'] = datetime.now().isoformat()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current session context"""
        if not self.current_session_id:
            return {}
        
        return self.sessions[self.current_session_id]['context']
    
    def get_recent_messages(self, n: int = 5) -> List[Dict]:
        """Get last N messages for context"""
        if not self.current_session_id:
            return []
        
        session = self.sessions[self.current_session_id]
        return session['messages'][-n:]
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation"""
        if not self.current_session_id:
            return "No active session"
        
        session = self.sessions[self.current_session_id]
        context = session['context']
        
        summary = f"""Session: {self.current_session_id}
Status: {context.get('status', 'unknown')}
URL: {context.get('url', 'none')}
Fields: {', '.join(context.get('fields', [])) or 'none'}
Data Extracted: {context.get('data_extracted', 0)} records
Total Messages: {session['metadata']['total_messages']}
Interruptions: {session['metadata']['interruptions']}"""
        
        return summary
    
    def record_interruption(self, reason: str = "") -> None:
        """Record a user interruption"""
        if not self.current_session_id:
            return
        
        session = self.sessions[self.current_session_id]
        session['metadata']['interruptions'] += 1
        
        self.add_message(
            role='system',
            content=f"Interruption: {reason}",
            metadata={'type': 'interruption'}
        )
    
    def set_status(self, status: str) -> None:
        """Set session status"""
        self.update_context('status', status)
    
    def increment_data_count(self, count: int) -> None:
        """Increment extracted data count"""
        if not self.current_session_id:
            return
        
        session = self.sessions[self.current_session_id]
        current = session['context'].get('data_extracted', 0)
        session['context']['data_extracted'] = current + count
    
    def export_session(self, session_id: Optional[str] = None) -> Dict:
        """Export session data for persistence"""
        sid = session_id or self.current_session_id
        if not sid or sid not in self.sessions:
            return {}
        
        return self.sessions[sid].copy()
    
    def import_session(self, session_data: Dict) -> str:
        """Import session data from persistence"""
        session_id = session_data.get('id')
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            session_data['id'] = session_id
        
        self.sessions[session_id] = session_data
        self.current_session_id = session_id
        return session_id
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions with summary"""
        sessions_list = []
        
        for sid, session in self.sessions.items():
            sessions_list.append({
                'id': sid,
                'created_at': session['created_at'],
                'status': session['context'].get('status', 'unknown'),
                'url': session['context'].get('url'),
                'message_count': session['metadata']['total_messages']
            })
        
        return sessions_list
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = None
            return True
        return False
    
    def clear_all_sessions(self) -> None:
        """Clear all sessions"""
        self.sessions.clear()
        self.current_session_id = None
    
    def get_context_for_prompt(self) -> str:
        """Get formatted context for AI prompt"""
        context = self.get_context()
        recent = self.get_recent_messages(3)
        
        prompt_context = f"""Current Session Context:
- URL: {context.get('url', 'Not set')}
- Target Fields: {', '.join(context.get('fields', [])) or 'Not specified'}
- Status: {context.get('status', 'idle')}
- Records Extracted: {context.get('data_extracted', 0)}

Recent Messages:
"""
        
        for msg in recent:
            role = msg['role'].upper()
            content = msg['content'][:200]  # Truncate long messages
            prompt_context += f"- {role}: {content}\n"
        
        return prompt_context
    
    def save_to_file(self, filepath: str) -> bool:
        """Save all sessions to file"""
        try:
            data = {
                'sessions': self.sessions,
                'current_session_id': self.current_session_id,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving sessions: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load sessions from file"""
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.sessions = data.get('sessions', {})
            self.current_session_id = data.get('current_session_id')
            
            return True
            
        except Exception as e:
            print(f"Error loading sessions: {e}")
            return False
