#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для модуля bot.py (Итерация 1)
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram import Bot, Dispatcher, types
from src.bot import init_bot, cmd_start, echo, start_polling


@pytest.fixture
def message_mock():
    """Фикстура для создания мока сообщения"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123456789
    message.text = "Тестовое сообщение"
    message.chat = MagicMock()
    message.chat.id = 123456789
    return message


@pytest.mark.asyncio
async def test_cmd_start(message_mock):
    """Тест обработчика команды /start"""
    await cmd_start(message_mock)
    message_mock.answer.assert_called_once()
    assert "ассистент компании" in message_mock.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_echo_without_llm():
    """Тест эхо-обработчика без интеграции с LLM"""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123456789
    message.text = "Тестовое сообщение"
    message.chat = MagicMock()
    message.chat.id = 123456789
    
    # Создаем мок для бота
    bot_mock = AsyncMock()
    bot_mock.send_chat_action = AsyncMock()
    
    with patch("src.bot.bot", bot_mock), \
         patch("src.bot.create_messages_for_llm") as create_messages_mock, \
         patch("src.bot.generate_response", return_value=None) as generate_response_mock:
        
        await echo(message)
        
        # Проверяем, что был вызван метод send_chat_action
        bot_mock.send_chat_action.assert_called_once_with(
            chat_id=message.chat.id, 
            action="typing"
        )
        
        # Проверяем, что были созданы сообщения для LLM
        create_messages_mock.assert_called_once_with(message.text)
        
        # Проверяем, что был вызван generate_response
        generate_response_mock.assert_called_once()
        
        # Проверяем, что был отправлен ответ об ошибке
        message.answer.assert_called_once()
        assert "ошибка" in message.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_init_bot():
    """Тест инициализации бота"""
    with patch("src.bot.Bot") as bot_mock, \
         patch("src.bot.Dispatcher") as dp_mock:
        
        token = "test_token"
        await init_bot(token)
        
        # Проверяем, что бот был создан с правильным токеном
        bot_mock.assert_called_once_with(token=token)
        
        # Проверяем, что диспетчер был создан
        dp_mock.assert_called_once()
        
        # Проверяем, что обработчики были зарегистрированы
        dp_instance = dp_mock.return_value
        assert dp_instance.message.register.call_count == 2


@pytest.mark.asyncio
async def test_start_polling_not_initialized():
    """Тест запуска бота без инициализации"""
    with patch("src.bot.bot", None), \
         patch("src.bot.dp", None):
        
        with pytest.raises(RuntimeError) as exc_info:
            await start_polling()
        
        assert "не инициализирован" in str(exc_info.value)


@pytest.mark.asyncio
async def test_start_polling():
    """Тест запуска бота в режиме polling"""
    with patch("src.bot.bot", MagicMock()), \
         patch("src.bot.dp", AsyncMock()) as dp_mock:
        
        await start_polling()
        
        # Проверяем, что был вызван метод start_polling
        dp_mock.start_polling.assert_called_once()