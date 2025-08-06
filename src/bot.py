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
from src.styles import STYLE_NORMAL, STYLE_CAT, STYLE_VILLAIN, STYLE_DRAMATIC, set_user_style, reset_user_style

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
    dp.message.register(cmd_style, Command("style"))
    dp.message.register(cmd_normal, Command("normal"))
    dp.message.register(cmd_cat, Command("cat"))
    dp.message.register(cmd_villain, Command("villain"))
    dp.message.register(cmd_dramatic, Command("dramatic"))
    dp.message.register(echo)
    
    logger.info("Бот инициализирован")

async def cmd_start(message: types.Message) -> None:
    """
    Обработчик команды /start
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Пользователь {user_id} запустил бота")
    
    # Сбрасываем стиль пользователя на обычный
    reset_user_style(chat_id)
    
    # Получаем метку для обычного стиля
    style_badge = "🔹 <b>Обычный режим</b>"
    
    # Используем сценарий приветствия
    await handle_start_command(message, style_badge=style_badge)

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
    
    # Импортируем стили
    from src.styles import get_user_style, STYLE_NORMAL, STYLE_CAT, STYLE_VILLAIN, STYLE_DRAMATIC
    
    # Определяем текущий стиль ответа
    current_style = get_user_style(chat_id, user_text)
    
    # Цветные метки для разных стилей
    style_badges = {
        STYLE_NORMAL: "🔹 <b>Обычный режим</b>",
        STYLE_CAT: "🐱 <b>Кошачий режим</b>",
        STYLE_VILLAIN: "😈 <b>Злодейский режим</b>",
        STYLE_DRAMATIC: "🎭 <b>Драматический режим</b>"
    }
    
    if service_type:
        # Если определили тип услуги, используем специальный сценарий
        logger.info(f"Определен тип услуги: {service_type}")
        await handle_service_inquiry(message, service_type, style_badge=style_badges[current_style])
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
            
            # Добавляем метку стиля в начало сообщения
            style_badge = style_badges.get(current_style, style_badges[STYLE_NORMAL])
            formatted_response_with_badge = f"{style_badge}\n\n{formatted_response}"
            
            # Отправляем ответ пользователю с поддержкой HTML-форматирования
            await message.answer(formatted_response_with_badge, parse_mode="HTML")
            logger.info(f"Отправлен ответ LLM пользователю {user_id} в стиле {current_style}")
            
            # Сохраняем оригинальный ответ ассистента в историю
            add_message(chat_id, "assistant", response)
        else:
            # В случае ошибки отправляем стандартный ответ с кликабельной ссылкой
            from aiogram.utils.markdown import hlink
            contact_link = hlink("обратитесь к менеджеру", "https://t.me/manager_technoservice")
            error_message = f"{style_badges[STYLE_NORMAL]}\n\nИзвините, произошла ошибка. Попробуйте позже или {contact_link}."
            await message.answer(error_message, parse_mode="HTML")
            
            # Сохраняем стандартный ответ в историю (без HTML-тегов)
            add_message(chat_id, "assistant", "Извините, произошла ошибка. Попробуйте позже или обратитесь к менеджеру.")
            
            logger.error(f"Ошибка при получении ответа от LLM для пользователя {user_id}")

async def cmd_style(message: types.Message) -> None:
    """
    Обработчик команды /style - показывает информацию о доступных стилях
    """
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} запросил информацию о стилях")
    
    # Формируем сообщение с информацией о стилях
    style_info = (
        "Доступные стили общения:\n\n"
        "🔹 /normal - Обычный режим\n"
        "🐱 /cat - Переводчик с технического на кошачий\n"
        "😈 /villain - Переводчик на язык суперзлодеев\n"
        "🎭 /dramatic - Драматический технический писатель\n\n"
        "Вы также можете просто упомянуть стиль в своём сообщении, "
        "и бот автоматически переключится на него. Например: \"Расскажи о базах данных как кот\""
    )
    
    await message.answer(style_info)

async def cmd_normal(message: types.Message) -> None:
    """
    Обработчик команды /normal - устанавливает обычный стиль
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Пользователь {user_id} выбрал обычный стиль")
    
    set_user_style(chat_id, STYLE_NORMAL)
    await message.answer("Выбран обычный стиль общения.")

async def cmd_cat(message: types.Message) -> None:
    """
    Обработчик команды /cat - устанавливает кошачий стиль
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Пользователь {user_id} выбрал кошачий стиль")
    
    set_user_style(chat_id, STYLE_CAT)
    await message.answer("Мяу! Выбран кошачий стиль общения. Мррр... 🐱")

async def cmd_villain(message: types.Message) -> None:
    """
    Обработчик команды /villain - устанавливает стиль суперзлодея
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Пользователь {user_id} выбрал стиль суперзлодея")
    
    set_user_style(chat_id, STYLE_VILLAIN)
    await message.answer("МУАХАХА! Выбран ЗЛОДЕЙСКИЙ стиль общения! Теперь вы в моей ВЛАСТИ! 😈")

async def cmd_dramatic(message: types.Message) -> None:
    """
    Обработчик команды /dramatic - устанавливает драматический стиль
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Пользователь {user_id} выбрал драматический стиль")
    
    set_user_style(chat_id, STYLE_DRAMATIC)
    await message.answer("О, благородный собеседник! Вы избрали ЭПИЧЕСКИЙ и ДРАМАТИЧЕСКИЙ стиль общения! Да начнется наша ВЕЛИЧЕСТВЕННАЯ беседа! 🎭")

async def start_polling() -> None:
    """
    Запускает бота в режиме polling
    """
    if bot is None or dp is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() сначала.")
    
    logger.info("Запуск бота в режиме polling")
    await dp.start_polling(bot)