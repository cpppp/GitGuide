import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

class Config:
    # OpenAI 配置（支持自定义 API）
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # GitHub 配置
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # 应用配置
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    APP_ENV = os.getenv("APP_ENV", "development")

# 初始化 LLM 客户端
def get_llm():
    try:
        # 支持自定义 API URL（如智谱 GLM）
        llm_params = {
            "model": Config.OPENAI_MODEL,
            "api_key": Config.OPENAI_API_KEY,
            "temperature": 0.3
        }

        # 如果配置了自定义 base_url，添加进去
        if Config.OPENAI_BASE_URL:
            llm_params["base_url"] = Config.OPENAI_BASE_URL

        return ChatOpenAI(**llm_params)
    except Exception as e:
        # 降级处理
        print(f"Error initializing LLM: {e}")
        # 尝试使用默认的 GPT-3.5-turbo
        try:
            return ChatOpenAI(
                model="ark-code-latest",
                api_key=Config.OPENAI_API_KEY,
                temperature=0.3
            )
        except:
            return None

# 全局 LLM 实例
llm = get_llm()