#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для модуля prompts.py (Итерация 2)
"""
import pytest
import os
from unittest.mock import patch, mock_open
from src.prompts import load_system_prompt, create_messages_for_llm


@pytest.fixture
def mock_system_prompt():
    """Фикстура для создания мока системного промпта"""
    return "Это тестовый системный промпт"


def test_load_system_prompt_success(mock_system_prompt):
    """Тест успешной загрузки системного промпта"""
    # Мокаем open для возврата тестового промпта
    with patch("builtins.open", mock_open(read_data=mock_system_prompt)), \
         patch("os.path.exists", return_value=True):
        
        result = load_system_prompt()
        
        # Проверяем результат
        assert result == mock_system_prompt


def test_load_system_prompt_file_not_found():
    """Тест загрузки системного промпта, когда файл не найден"""
    with patch("os.path.exists", return_value=False):
        result = load_system_prompt()
        
        # Проверяем, что был возвращен None
        assert result is None


def test_load_system_prompt_exception():
    """Тест обработки исключений при загрузке системного промпта"""
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", side_effect=Exception("Test exception")):
        
        result = load_system_prompt()
        
        # Проверяем, что был возвращен None при исключении
        assert result is None


def test_create_messages_for_llm_with_system_prompt(mock_system_prompt):
    """Тест создания сообщений с системным промптом"""
    user_message = "Привет!"
    
    with patch("src.prompts.load_system_prompt", return_value=mock_system_prompt):
        messages = create_messages_for_llm(user_message)
        
        # Проверяем, что сообщения созданы правильно
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == mock_system_prompt
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == user_message


def test_create_messages_for_llm_without_system_prompt():
    """Тест создания сообщений без системного промпта"""
    user_message = "Привет!"
    
    with patch("src.prompts.load_system_prompt", return_value=None):
        messages = create_messages_for_llm(user_message)
        
        # Проверяем, что создано только сообщение пользователя
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == user_message