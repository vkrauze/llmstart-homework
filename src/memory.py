#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с памятью диалогов
"""
from typing import Dict, List, Any, Optional
import logging
import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальный словарь для хранения диалогов
# Ключ - идентификатор чата (chat_id), значение - список сообщений
dialogs = {}

def add_message(chat_id: int, role: str, content: str) -> None:
    """
    Добавляет сообщение в историю диалога
    
    Args:
        chat_id: Идентификатор чата
        role: Роль отправителя (system/user/assistant)
        content: Текст сообщения
    """
    # Создаем запись для чата, если её еще нет
    if chat_id not in dialogs:
        dialogs[chat_id] = []
    
    # Добавляем сообщение с текущим временем
    timestamp = datetime.datetime.now().isoformat()
    message = {
        "role": role,
        "content": content,
        "timestamp": timestamp
    }
    
    dialogs[chat_id].append(message)
    logger.debug(f"Добавлено сообщение для чата {chat_id}: {role}")

def get_dialog_history(chat_id: int, max_messages: int = 10) -> List[Dict[str, Any]]:
    """
    Возвращает историю диалога для указанного чата
    
    Args:
        chat_id: Идентификатор чата
        max_messages: Максимальное количество последних сообщений для возврата
        
    Returns:
        Список сообщений в формате [{role, content, timestamp}]
    """
    if chat_id not in dialogs:
        logger.debug(f"История для чата {chat_id} не найдена")
        return []
    
    # Возвращаем последние max_messages сообщений
    history = dialogs[chat_id][-max_messages:] if len(dialogs[chat_id]) > max_messages else dialogs[chat_id]
    logger.debug(f"Получена история для чата {chat_id}: {len(history)} сообщений")
    return history

def get_dialog_messages_for_llm(chat_id: int, max_messages: int = 10) -> List[Dict[str, str]]:
    """
    Возвращает историю диалога в формате для отправки в LLM API
    
    Args:
        chat_id: Идентификатор чата
        max_messages: Максимальное количество последних сообщений
        
    Returns:
        Список сообщений в формате [{role, content}] без timestamp
    """
    history = get_dialog_history(chat_id, max_messages)
    
    # Преобразуем в формат для LLM (без timestamp)
    llm_messages = []
    for message in history:
        if message["role"] in ["system", "user", "assistant"]:
            llm_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
    
    return llm_messages

def clear_dialog_history(chat_id: int) -> None:
    """
    Очищает историю диалога для указанного чата
    
    Args:
        chat_id: Идентификатор чата
    """
    if chat_id in dialogs:
        dialogs[chat_id] = []
        logger.info(f"История диалога для чата {chat_id} очищена")