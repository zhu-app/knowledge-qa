import os
import warnings
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# 相似度阈值：低于此值的检索结果将被过滤掉 (0.0~1.0)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))


def validate_config():
    """Validate required configuration at startup. Returns True if valid."""
    if not OPENAI_API_KEY:
        warnings.warn("⚠️ 未设置 OPENAI_API_KEY！请在 .env 文件中配置 API Key，否则 LLM 调用将失败。")
        return False
    if OPENAI_API_KEY == "your-api-key-here":
        warnings.warn("⚠️ OPENAI_API_KEY 仍为默认占位值，请修改为真实 API Key！")
        return False
    return True


# 首次导入时自动验证（但不阻塞）
_CONFIG_VALID = validate_config()
