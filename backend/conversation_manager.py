import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from backend.models import ConversationHistory, ChatMessage
import os

class ConversationManager:
    def __init__(self, storage_path: str = "conversations"):
        self.storage_path = storage_path
        self.conversations: Dict[str, ConversationHistory] = {}
        self.ensure_storage_directory()
        self.load_conversations()

    def ensure_storage_directory(self):
        """التأكد من وجود مجلد التخزين"""
        os.makedirs(self.storage_path, exist_ok=True)

    def generate_session_id(self) -> str:
        """توليد معرف جلسة جديد"""
        return str(uuid.uuid4())

    def create_new_conversation(self, domain: str) -> str:
        """إنشاء محادثة جديدة"""
        session_id = self.generate_session_id()
        conversation = ConversationHistory(
            session_id=session_id,
            domain=domain,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.conversations[session_id] = conversation
        self.save_conversation(session_id)
        return session_id

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """إضافة رسالة إلى المحادثة"""
        if session_id not in self.conversations:
            return False

        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )

        self.conversations[session_id].messages.append(message)
        self.conversations[session_id].updated_at = datetime.now()
        self.save_conversation(session_id)
        return True

    def get_conversation_history(self, session_id: str) -> Optional[ConversationHistory]:
        """الحصول على تاريخ المحادثة"""
        return self.conversations.get(session_id)

    def get_messages_for_gemini(self, session_id: str) -> List[Dict]:
        """تحويل الرسائل لتنسيق Gemini API"""
        if session_id not in self.conversations:
            return []

        messages = []
        for msg in self.conversations[session_id].messages:
            # تحويل role إلى تنسيق Gemini
            if msg.role == "user":
                messages.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "assistant":
                messages.append({"role": "model", "parts": [{"text": msg.content}]})

        return messages

    def save_conversation(self, session_id: str):
        """حفظ المحادثة في ملف"""
        if session_id not in self.conversations:
            return

        file_path = os.path.join(self.storage_path, f"{session_id}.json")
        conversation_data = self.conversations[session_id].dict()

        # تحويل datetime إلى string للتسلسل
        for message in conversation_data["messages"]:
            if isinstance(message["timestamp"], datetime):
                message["timestamp"] = message["timestamp"].isoformat()

        conversation_data["created_at"] = conversation_data["created_at"].isoformat()
        conversation_data["updated_at"] = conversation_data["updated_at"].isoformat()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)

    def load_conversations(self):
        """تحميل جميع المحادثات المحفوظة"""
        if not os.path.exists(self.storage_path):
            return

        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    session_id = filename[:-5]  # إزالة .json
                    file_path = os.path.join(self.storage_path, filename)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # تحويل strings إلى datetime
                    for message in data["messages"]:
                        message["timestamp"] = datetime.fromisoformat(message["timestamp"])

                    data["created_at"] = datetime.fromisoformat(data["created_at"])
                    data["updated_at"] = datetime.fromisoformat(data["updated_at"])

                    conversation = ConversationHistory(**data)
                    self.conversations[session_id] = conversation

                except Exception as e:
                    print(f"خطأ في تحميل المحادثة {filename}: {e}")

    def cleanup_old_conversations(self, days: int = 30):
        """حذف المحادثات القديمة"""
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions_to_remove = []

        for session_id, conversation in self.conversations.items():
            if conversation.updated_at < cutoff_date:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            self.remove_conversation(session_id)

    def remove_conversation(self, session_id: str):
        """حذف محادثة"""
        if session_id in self.conversations:
            del self.conversations[session_id]

            file_path = os.path.join(self.storage_path, f"{session_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)

    def get_conversation_summary(self, session_id: str) -> Dict:
        """الحصول على ملخص المحادثة"""
        if session_id not in self.conversations:
            return {}

        conversation = self.conversations[session_id]
        return {
            "session_id": session_id,
            "domain": conversation.domain,
            "message_count": len(conversation.messages),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "last_message": conversation.messages[-1].content if conversation.messages else None
        }
