# # from pydantic import BaseSettings
# from pydantic_settings import BaseSettings

# from typing import List

# class Settings(BaseSettings):
#     gemini_api_key: str
#     host: str = "0.0.0.0"
#     port: int = 8000
#     debug: bool = True
#     available_domains: str
#     default_domain: str = "html_css_js"

#     # Domain configurationse
#     domain_prompts = {
#         "html_css_js": {
#             "name": "HTML, CSS & JavaScript",
#             "description": "تطوير الواجهات الأمامية باستخدام HTML و CSS و JavaScript",
#             "system_prompt": '''أنت مساعد ذكي متخصص في HTML و CSS و JavaScript فقط. 
#             يجب أن تجيب فقط على الأسئلة المتعلقة بهذه التقنيات الثلاث.
#             إذا سأل المستخدم عن شيء خارج نطاق HTML/CSS/JS، اعتذر بلطف وأعد توجيهه للسؤال في التخصص المحدد.
#             قدم إجابات واضحة ومفصلة مع أمثلة عملية عندما يكون ذلك مناسباً.'''
#         },
#         "python": {
#             "name": "Python Programming",
#             "description": "برمجة Python وتطوير التطبيقات",
#             "system_prompt": '''أنت مساعد ذكي متخصص في برمجة Python فقط.
#             يجب أن تجيب فقط على الأسئلة المتعلقة بلغة Python.
#             إذا سأل المستخدم عن لغات برمجة أخرى، اعتذر بلطف وأعد توجيهه للسؤال في Python.
#             قدم إجابات واضحة مع أمثلة كود عملية.'''
#         },
#         "web_development": {
#             "name": "Web Development",
#             "description": "تطوير الويب الشامل",
#             "system_prompt": '''أنت مساعد ذكي متخصص في تطوير الويب.
#             يجب أن تجيب فقط على الأسئلة المتعلقة بتطوير المواقع والتطبيقات الويب.
#             إذا سأل المستخدم عن موضوع خارج تطوير الويب، اعتذر بلطف وأعد التوجيه.
#             قدم إجابات شاملة مع أمثلة عملية.'''
#         }
#     }

#     class Config:
#         env_file = ".env"

# settings = Settings()

from pydantic_settings import BaseSettings
from typing import ClassVar, Dict, Any

class Settings(BaseSettings):
    gemini_api_key: str
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    available_domains: str
    default_domain: str = "html_css_js"

    # Domain configurations (ليس حقل من environment)
    domain_prompts: ClassVar[Dict[str, Dict[str, Any]]] = {
        "html_css_js": {
            "name": "HTML, CSS & JavaScript",
            "description": "تطوير الواجهات الأمامية باستخدام HTML و CSS و JavaScript",
            "system_prompt": '''أنت مساعد ذكي متخصص في HTML و CSS و JavaScript فقط. 
            يجب أن تجيب فقط على الأسئلة المتعلقة بهذه التقنيات الثلاث.
            إذا سأل المستخدم عن شيء خارج نطاق HTML/CSS/JS، اعتذر بلطف وأعد توجيهه للسؤال في التخصص المحدد.
            قدم إجابات واضحة ومفصلة مع أمثلة عملية عندما يكون ذلك مناسباً.'''
        },
        "python": {
            "name": "Python Programming",
            "description": "برمجة Python وتطوير التطبيقات",
            "system_prompt": '''أنت مساعد ذكي متخصص في برمجة Python فقط.
            يجب أن تجيب فقط على الأسئلة المتعلقة بلغة Python.
            إذا سأل المستخدم عن لغات برمجة أخرى، اعتذر بلطف وأعد توجيهه للسؤال في Python.
            قدم إجابات واضحة مع أمثلة كود عملية.'''
        },
        "web_development": {
            "name": "Web Development",
            "description": "تطوير الويب الشامل",
            "system_prompt": '''أنت مساعد ذكي متخصص في تطوير الويب.
            يجب أن تجيب فقط على الأسئلة المتعلقة بتطوير المواقع والتطبيقات الويب.
            إذا سأل المستخدم عن موضوع خارج تطوير الويب، اعتذر بلطف وأعد التوجيه.
            قدم إجابات شاملة مع أمثلة عملية.'''
        }
    }

    class Config:
        env_file = ".env"

settings = Settings()
