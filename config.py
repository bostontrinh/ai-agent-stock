import os
from dotenv import load_dotenv

load_dotenv()


# =========================
# DeepSeek 配置
# =========================

DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY"
)

BASE_URL = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com"
)


MODEL = "deepseek-chat"


# =========================
# Vision 配置
# =========================

VISION_MODEL = MODEL


# =========================
# 其他
# =========================

TIMEOUT = 60


if not DEEPSEEK_API_KEY:
    raise ValueError(
        "未找到 DEEPSEEK_API_KEY，请检查 .env"
    )
