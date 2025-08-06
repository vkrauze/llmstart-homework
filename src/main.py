#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Точка входа для запуска бота
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from src.bot import init_bot, start_polling
from src.llm import init_llm

# Загрузка переменных окружения
# Сначала проверяем наличие переменных в системном окружении
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

# Если переменные не найдены в системном окружении, пробуем загрузить из .env файла
if not telegram_token or not openrouter_api_key:
    import os.path
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f"Загружены переменные из .env файла")

# Настройка логирования
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main() -> None:
    """
    Основная функция для запуска бота
    """
    # Получение токена Telegram из переменных окружения
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        # Если токен не найден, выводим ошибку и завершаем работу
        logger.error("Токен бота не найден в переменных окружения")
        return
    
    # Получение API ключа OpenRouter
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.error("API ключ OpenRouter не найден в переменных окружения")
        return
    
    # Инициализация LLM клиента
    init_llm(openrouter_api_key)
    
    # Инициализация и запуск бота
    await init_bot(telegram_token)
    await start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")