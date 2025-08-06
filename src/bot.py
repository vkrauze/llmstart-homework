#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с Telegram API
"""
from typing import Dict, Any
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from llm import generate_response
from prompts import create_messages_for_llm

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = None
dp = None

async def init_bot(token: str) -> None:
    """
    Инициализирует бота с указанным токеном
    """
    global bot, dp
    bot = Bot(token=token)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(echo)
    
    logger.info("Бот инициализирован")

async def cmd_start(message: types.Message) -> None:
    """
    Обработчик команды /start
    """
    await message.answer("Здравствуйте! Я ассистент компании ООО \"ТехноСервис\". Чем я могу вам помочь?")
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

async def echo(message: types.Message) -> None:
    """
    Обработчик всех текстовых сообщений
    """
    user_id = message.from_user.id
    user_text = message.text
    
    logger.info(f"Пользователь {user_id} отправил сообщение: {user_text}")
    
    # Отправляем индикатор набора текста
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Создаем сообщения для LLM
    messages = create_messages_for_llm(user_text)
    
    # Получаем ответ от LLM
    response = await generate_response(messages)
    
    if response:
        await message.answer(response)
        logger.info(f"Отправлен ответ LLM пользователю {user_id}")
    else:
        await message.answer("Извините, произошла ошибка. Попробуйте позже или обратитесь к менеджеру.")
        logger.error(f"Ошибка при получении ответа от LLM для пользователя {user_id}")

async def start_polling() -> None:
    """
    Запускает бота в режиме polling
    """
    if bot is None or dp is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() сначала.")
    
    logger.info("Запуск бота в режиме polling")
    await dp.start_polling(bot)