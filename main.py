from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path

# استيراد الوحدات المحلية
from backend.models import ChatRequest, ChatResponse, DomainInfo
from backend.conversation_manager import ConversationManager
from backend.gemini_service import gemini_service
from config.settings import settings

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Educational Chatbot API",
    description="شات بوت تعليمي متخصص مع دعم للمحادثة المستمرة",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إنشاء مدير المحادثة
conversation_manager = ConversationManager(
    storage_path=os.path.join(os.getcwd(), "conversations")
)

# تقديم الملفات الثابتة
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """تقديم الواجهة الأمامية"""
    frontend_path = Path("frontend/index.html")
    if frontend_path.exists():
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>مرحباً بك في الشات بوت التعليمي</h1>")

@app.get("/api/domains")
async def get_available_domains():
    """الحصول على قائمة التخصصات المتاحة"""
    domains = []
    for domain_id, domain_config in settings.domain_prompts.items():
        domains.append(DomainInfo(
            domain_id=domain_id,
            name=domain_config["name"],
            description=domain_config["description"]
        ))
    return {"domains": domains}

@app.post("/api/chat/new")
async def create_new_chat(domain: str = settings.default_domain):
    """إنشاء محادثة جديدة"""
    if domain not in settings.domain_prompts:
        raise HTTPException(status_code=400, detail="نطاق التخصص غير مدعوم")

    session_id = conversation_manager.create_new_conversation(domain)
    return {
        "session_id": session_id,
        "domain": domain,
        "message": f"مرحباً! أنا مساعدك في {settings.domain_prompts[domain]['name']}. كيف يمكنني مساعدتك؟"
    }

@app.post("/api/chat/{session_id}", response_model=ChatResponse)
async def send_message(session_id: str, chat_request: ChatRequest):
    """إرسال رسالة في محادثة موجودة"""

    # التحقق من وجود الجلسة
    conversation = conversation_manager.get_conversation_history(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")

    # التحقق من صحة النطاق
    domain = chat_request.domain or conversation.domain
    if domain not in settings.domain_prompts:
        raise HTTPException(status_code=400, detail="نطاق التخصص غير مدعوم")

    # إضافة رسالة المستخدم إلى التاريخ
    conversation_manager.add_message(session_id, "user", chat_request.message)

    try:
        # الحصول على تاريخ المحادثة لـ Gemini
        history = conversation_manager.get_messages_for_gemini(session_id)

        # الحصول على prompt النطاق
        domain_config = settings.domain_prompts[domain]
        system_prompt = domain_config["system_prompt"]

        # توليد الرد من Gemini
        response_text = await gemini_service.generate_response(
            message=chat_request.message,
            conversation_history=history,
            domain=domain,
            system_prompt=system_prompt
        )

        # إضافة رد المساعد إلى التاريخ
        conversation_manager.add_message(session_id, "assistant", response_text)

        return ChatResponse(
            message=response_text,
            session_id=session_id,
            domain=domain
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"خطأ في معالجة الرسالة: {str(e)}"
        )

@app.get("/api/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """الحصول على تاريخ المحادثة"""
    conversation = conversation_manager.get_conversation_history(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")

    return {
        "session_id": session_id,
        "domain": conversation.domain,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation.messages
        ]
    }

@app.get("/api/chat/{session_id}/summary")
async def get_chat_summary(session_id: str):
    """الحصول على ملخص المحادثة"""
    summary = conversation_manager.get_conversation_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")

    return summary

@app.delete("/api/chat/{session_id}")
async def delete_chat(session_id: str):
    """حذف محادثة"""
    conversation = conversation_manager.get_conversation_history(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")

    conversation_manager.remove_conversation(session_id)
    return {"message": "تم حذف المحادثة بنجاح"}

@app.get("/api/health")
async def health_check():
    """فحص صحة النظام"""
    gemini_status = await gemini_service.test_connection()

    return {
        "status": "healthy" if gemini_status else "degraded",
        "gemini_api": "connected" if gemini_status else "disconnected",
        "available_domains": list(settings.domain_prompts.keys())
    }

@app.post("/api/admin/cleanup")
async def cleanup_old_conversations():
    """تنظيف المحادثات القديمة (للإدارة)"""
    conversation_manager.cleanup_old_conversations()
    return {"message": "تم تنظيف المحادثات القديمة"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.debug
    )
