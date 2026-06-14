import os
import sys
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embedding-2")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 相似度阈值：低于此值的检索结果将被过滤掉 (0.0~1.0)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))


def validate_config():
    """Validate required configuration at startup."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here":
        print("错误: 请在 .env 文件中设置有效的 OPENAI_API_KEY")
        print("  参考 .env.example 进行配置")
        sys.exit(1)


validate_config()
