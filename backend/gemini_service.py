import google.generativeai as genai
from typing import List, Dict, Optional
from config.settings import settings
import asyncio
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = None
        self.configure_api()

    def configure_api(self):
        """إعداد Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("تم إعداد Gemini API بنجاح")
        except Exception as e:
            logger.error(f"خطأ في إعداد Gemini API: {e}")
            raise

    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[Dict], 
        domain: str,
        system_prompt: str
    ) -> str:
        """توليد رد من Gemini مع التاريخ الكامل للمحادثة"""
        try:
            # بناء السياق الكامل للمحادثة
            context = self._build_conversation_context(
                system_prompt, 
                conversation_history, 
                message
            )

            # إرسال الطلب إلى Gemini
            response = await asyncio.to_thread(
                self._call_gemini_api, 
                context
            )

            logger.info(f"تم الحصول على رد من Gemini للنطاق: {domain}")
            return response

        except Exception as e:
            logger.error(f"خطأ في توليد الرد من Gemini: {e}")
            return f"عذراً، حدث خطأ في معالجة طلبك. الرجاء المحاولة مرة أخرى."

    def _build_conversation_context(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict], 
        new_message: str
    ) -> str:
        """بناء السياق الكامل للمحادثة"""

        # بناء الحوار الكامل
        context_parts = []

        # إضافة النظام الأساسي
        context_parts.append(f"تعليمات النظام: {system_prompt}")
        context_parts.append("\n--- بداية تاريخ المحادثة ---\n")

        # إضافة تاريخ المحادثة
        for msg in conversation_history:
            role = "المستخدم" if msg.get("role") == "user" else "المساعد"
            content = msg.get("parts", [{}])[0].get("text", "")
            context_parts.append(f"{role}: {content}")

        # إضافة الرسالة الجديدة
        context_parts.append(f"\n--- الرسالة الجديدة ---")
        context_parts.append(f"المستخدم: {new_message}")
        context_parts.append("\nالمساعد:")

        return "\n".join(context_parts)

    def _call_gemini_api(self, prompt: str) -> str:
        """استدعاء Gemini API بشكل متزامن"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=2048,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            )

            return response.text if response.text else "عذراً، لم أتمكن من توليد رد مناسب."

        except Exception as e:
            logger.error(f"خطأ في استدعاء Gemini API: {e}")
            raise

    def validate_domain_response(self, response: str, domain: str) -> str:
        """التحقق من أن الرد يتماشى مع النطاق المحدد"""
        # يمكن إضافة منطق للتحقق من صحة الرد حسب النطاق
        # في الوقت الحالي، نعيد الرد كما هو
        return response

    async def test_connection(self) -> bool:
        """اختبار الاتصال مع Gemini API"""
        try:
            test_response = await asyncio.to_thread(
                self._call_gemini_api, 
                "مرحبا، هل يمكنك الرد بكلمة واحدة فقط؟"
            )
            return bool(test_response and len(test_response.strip()) > 0)
        except Exception as e:
            logger.error(f"فشل اختبار الاتصال مع Gemini: {e}")
            return False

# إنشاء مثيل عام من الخدمة
gemini_service = GeminiService()
