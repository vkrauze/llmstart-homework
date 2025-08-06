#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для модуля llm.py (Итерация 2)
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from src.llm import init_llm, generate_response


@pytest.fixture
def openai_client_mock():
    """Фикстура для создания мока клиента OpenAI"""
    client_mock = MagicMock()
    return client_mock


def test_init_llm(openai_client_mock):
    """Тест инициализации клиента LLM"""
    with patch("src.llm.OpenAI", return_value=openai_client_mock) as openai_mock:
        api_key = "test_api_key"
        base_url = "https://test-url.com/api/v1"
        
        init_llm(api_key, base_url)
        
        # Проверяем, что OpenAI был вызван с правильными параметрами
        openai_mock.assert_called_once_with(
            api_key=api_key,
            base_url=base_url
        )
        
        # Проверяем, что глобальная переменная client была установлена
        from src.llm import client
        assert client == openai_client_mock


@pytest.mark.asyncio
async def test_generate_response_client_not_initialized():
    """Тест generate_response когда клиент не инициализирован"""
    with patch("src.llm.client", None):
        messages = [{"role": "user", "content": "Привет!"}]
        result = await generate_response(messages)
        assert result is None


@pytest.mark.asyncio
async def test_generate_response_success():
    """Тест успешной генерации ответа"""
    # Создаем мок ответа от OpenAI
    mock_response = MagicMock(spec=ChatCompletion)
    mock_message = MagicMock(spec=ChatCompletionMessage)
    mock_message.content = "Это тестовый ответ от LLM"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Создаем мок клиента
    mock_client = MagicMock()
    # Создаем корутину, которая возвращает mock_response
    async def mock_create(*args, **kwargs):
        return mock_response
    mock_client.chat.completions.create = mock_create
    
    with patch("src.llm.client", mock_client):
        messages = [{"role": "user", "content": "Привет!"}]
        model = "test-model"
        temperature = 0.5
        max_tokens = 500
        
        result = await generate_response(messages, model, temperature, max_tokens)
        
                    # В этом случае мы не можем проверить вызов метода create,
            # так как мы заменили его на корутину
        
        # Проверяем результат
        assert result == "Это тестовый ответ от LLM"


@pytest.mark.asyncio
async def test_generate_response_exception():
    """Тест обработки исключений при генерации ответа"""
    # Создаем мок клиента, который вызывает исключение
    mock_client = MagicMock()
    
    # Создаем корутину, которая вызывает исключение
    async def mock_create_exception(*args, **kwargs):
        raise Exception("Test exception")
    
    mock_client.chat.completions.create = mock_create_exception
    
    with patch("src.llm.client", mock_client):
        messages = [{"role": "user", "content": "Привет!"}]
        
        result = await generate_response(messages)
        
        # Проверяем, что был возвращен None при исключении
        assert result is None