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
        llm_params = {
            "model": Config.OPENAI_MODEL,
            "api_key": Config.OPENAI_API_KEY,
            "temperature": 0.3
        }

        if Config.OPENAI_BASE_URL:
            llm_params["base_url"] = Config.OPENAI_BASE_URL

        return ChatOpenAI(**llm_params)
    except Exception as e:
        print(f"Error initializing LLM with primary config: {e}")
        return None

# 全局 LLM 实例
llm = get_llm()

# 全局配置实例（供其他模块使用）
settings = Config()