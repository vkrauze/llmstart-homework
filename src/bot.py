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
from src.scenarios import handle_start_command, handle_service_inquiry, detect_service_type

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
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запустил бота")
    
    # Используем сценарий приветствия
    await handle_start_command(message)

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
    
    # Определяем, интересуется ли пользователь конкретной услугой
    service_type = detect_service_type(user_text)
    
    if service_type:
        # Если определили тип услуги, используем специальный сценарий
        logger.info(f"Определен тип услуги: {service_type}")
        await handle_service_inquiry(message, service_type)
    else:
        # Если тип услуги не определен, обрабатываем как обычный запрос
        # Сохраняем сообщение пользователя в историю
        add_message(chat_id, "user", user_text)
        
        # Создаем сообщения для LLM с учетом истории диалога
        messages = create_messages_for_llm(user_text, chat_id)
        
        # Получаем ответ от LLM
        response = await generate_response(messages)
        
        if response:
            # Добавляем кликабельные ссылки в ответ
            from src.scenarios import add_clickable_links
            formatted_response = add_clickable_links(response)
            
            # Отправляем ответ пользователю с поддержкой HTML-форматирования
            await message.answer(formatted_response, parse_mode="HTML")
            logger.info(f"Отправлен ответ LLM пользователю {user_id}")
            
            # Сохраняем оригинальный ответ ассистента в историю
            add_message(chat_id, "assistant", response)
        else:
            # В случае ошибки отправляем стандартный ответ с кликабельной ссылкой
            from aiogram.utils.markdown import hlink
            contact_link = hlink("обратитесь к менеджеру", "https://t.me/manager_technoservice")
            error_message = f"Извините, произошла ошибка. Попробуйте позже или {contact_link}."
            await message.answer(error_message, parse_mode="HTML")
            
            # Сохраняем стандартный ответ в историю (без HTML-тегов)
            add_message(chat_id, "assistant", "Извините, произошла ошибка. Попробуйте позже или обратитесь к менеджеру.")
            
            logger.error(f"Ошибка при получении ответа от LLM для пользователя {user_id}")

async def start_polling() -> None:
    """
    Запускает бота в режиме polling
    """
    if bot is None or dp is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() сначала.")
    
    logger.info("Запуск бота в режиме polling")
    await dp.start_polling(bot)