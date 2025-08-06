#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с промптами
"""
import os
import logging
from typing import Dict, List, Optional

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к директории с промптами
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prompts')

def load_system_prompt() -> Optional[str]:
    """
    Загружает системный промпт из файла
    
    Returns:
        Текст системного промпта или None в случае ошибки
    """
    try:
        system_prompt_path = os.path.join(PROMPTS_DIR, 'system.txt')
        if not os.path.exists(system_prompt_path):
            logger.error(f"Системный промпт не найден по пути: {system_prompt_path}")
            return None
            
        with open(system_prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Системный промпт загружен ({len(content)} символов)")
            return content
    except Exception as e:
        logger.error(f"Ошибка при загрузке системного промпта: {e}")
        return None

def create_messages_for_llm(user_message: str) -> List[Dict[str, str]]:
    """
    Создает список сообщений для отправки в LLM API
    
    Args:
        user_message: Сообщение пользователя
        
    Returns:
        Список сообщений в формате [{role, content}]
    """
    messages = []
    
    # Добавляем системный промпт
    system_prompt = load_system_prompt()
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    # Добавляем сообщение пользователя
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    return messages