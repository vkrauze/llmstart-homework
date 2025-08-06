#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с Telegram API
"""
from typing import Dict, Any
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from src.llm import generate_response
from src.prompts import create_messages_for_llm
from src.memory import add_message, clear_dialog_history

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
    welcome_message = "Здравствуйте! Я ассистент компании ООО \"ТехноСервис\". Чем я могу вам помочь?"
    await message.answer(welcome_message)
    
    # Сохраняем приветственное сообщение в историю
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Очищаем предыдущую историю диалога
    clear_dialog_history(chat_id)
    
    # Добавляем системное сообщение и приветствие бота
    add_message(chat_id, "assistant", welcome_message)
    
    logger.info(f"Пользователь {user_id} запустил бота")

async def echo(message: types.Message) -> None:
    """
    Обработчик всех текстовых сообщений
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text
    
    logger.info(f"Пользователь {user_id} отправил сообщение: {user_text}")
    
    # Отправляем индикатор набора текста
    await bot.send_chat_action(chat_id=chat_id, action="typing")
    
    # Сохраняем сообщение пользователя в историю
    add_message(chat_id, "user", user_text)
    
    # Создаем сообщения для LLM с учетом истории диалога
    messages = create_messages_for_llm(user_text, chat_id)
    
    # Получаем ответ от LLM
    response = await generate_response(messages)
    
    if response:
        # Отправляем ответ пользователю
        await message.answer(response)
        logger.info(f"Отправлен ответ LLM пользователю {user_id}")
        
        # Сохраняем ответ ассистента в историю
        add_message(chat_id, "assistant", response)
    else:
        error_message = "Извините, произошла ошибка. Попробуйте позже или обратитесь к менеджеру."
        await message.answer(error_message)
        logger.error(f"Ошибка при получении ответа от LLM для пользователя {user_id}")

async def start_polling() -> None:
    """
    Запускает бота в режиме polling
    """
    if bot is None or dp is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() сначала.")
    
    logger.info("Запуск бота в режиме polling")
    await dp.start_polling(bot)