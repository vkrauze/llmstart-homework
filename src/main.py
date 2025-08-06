#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Точка входа для запуска бота
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from bot import init_bot, start_polling
from llm import init_llm

# Загрузка переменных окружения из .env файла
import os.path
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"Ищем .env файл по пути: {env_path}, существует: {os.path.exists(env_path)}")
load_dotenv(dotenv_path=env_path)
print(f"Загружаем .env файл, TELEGRAM_BOT_TOKEN = {os.getenv('TELEGRAM_BOT_TOKEN')}")

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
        # Если токен не найден в .env, предложим ввести его вручную
        logger.warning("Токен бота не найден в .env файле")
        print("Введите токен Telegram бота:")
        telegram_token = input()
        if not telegram_token:
            logger.error("Токен не был введен")
            return
    
    # Получение API ключа OpenRouter
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        logger.warning("API ключ OpenRouter не найден в .env файле")
        print("Введите API ключ OpenRouter:")
        openrouter_api_key = input()
        if not openrouter_api_key:
            logger.error("API ключ OpenRouter не был введен")
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