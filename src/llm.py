#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с LLM API через OpenRouter
"""
from typing import Dict, List, Any, Optional
import os
import logging
import json
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Клиент OpenAI для работы с OpenRouter
client = None

def init_llm(api_key: str, base_url: str = "https://openrouter.ai/api/v1") -> None:
    """
    Инициализирует клиент для работы с LLM через OpenRouter
    
    Args:
        api_key: API ключ OpenRouter
        base_url: Базовый URL для API (по умолчанию OpenRouter)
    """
    global client
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    logger.info("LLM клиент инициализирован")

async def generate_response(
    messages: List[Dict[str, str]], 
    model: str = "qwen/qwen3-30b-a3b:free", 
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Optional[str]:
    """
    Генерирует ответ от LLM на основе сообщений
    
    Args:
        messages: Список сообщений в формате [{role, content}]
        model: Модель для использования
        temperature: Температура генерации (0.0-1.0)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текст ответа или None в случае ошибки
    """
    if client is None:
        logger.error("LLM клиент не инициализирован")
        return None
    
    try:
        # Логирование запроса
        logger.info(f"Запрос к LLM: модель={model}, температура={temperature}")
        logger.debug(f"Сообщения: {json.dumps(messages, ensure_ascii=False)}")
        
        # Отправка запроса к API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Получение и логирование ответа
        result = response.choices[0].message.content
        logger.info(f"Получен ответ от LLM ({len(result)} символов)")
        logger.debug(f"Ответ: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при запросе к LLM: {e}")
        return None