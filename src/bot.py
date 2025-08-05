#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с Telegram API
"""
from typing import Dict, Any
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

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
    await message.answer("Привет! Я эхо-бот. Напишите мне что-нибудь.")
    logger.info(f"Пользователь {message.from_user.id} запустил бота")

async def echo(message: types.Message) -> None:
    """
    Обработчик всех текстовых сообщений
    """
    await message.answer(message.text)
    logger.info(f"Пользователь {message.from_user.id} отправил сообщение: {message.text}")

async def start_polling() -> None:
    """
    Запускает бота в режиме polling
    """
    if bot is None or dp is None:
        raise RuntimeError("Бот не инициализирован. Вызовите init_bot() сначала.")
    
    logger.info("Запуск бота в режиме polling")
    await dp.start_polling(bot)