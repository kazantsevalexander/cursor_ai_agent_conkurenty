"""
Конфигурация приложения
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
    
    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # История
    history_file: str = os.getenv("HISTORY_FILE", "history.json")
    max_history_items: int = int(os.getenv("MAX_HISTORY_ITEMS", "10"))
    
    # Парсер
    parser_timeout: int = int(os.getenv("PARSER_TIMEOUT", "10"))
    parser_user_agent: str = os.getenv(
        "PARSER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Selenium настройки
    use_selenium: bool = os.getenv("USE_SELENIUM", "false").lower() == "true"
    selenium_timeout: int = int(os.getenv("SELENIUM_TIMEOUT", "15"))
    selenium_headless: bool = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
    selenium_wait_time: int = int(os.getenv("SELENIUM_WAIT_TIME", "3"))
    # URL конкурентов для мониторинга (через запятую)
    competitor_urls: str = os.getenv("COMPETITOR_URLS", "")
    
    # Telegram Bot (опционально)
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

