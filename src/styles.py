#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с различными стилями ответов бота
"""
import os
import re
import random
import logging
from typing import Dict, Optional, List, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к директории с промптами
PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prompts')

# Доступные стили
STYLE_NORMAL = "normal"
STYLE_CAT = "cat"
STYLE_VILLAIN = "villain"
STYLE_DRAMATIC = "dramatic"

# Словарь для хранения предпочтений пользователей: {chat_id: style}
user_styles: Dict[int, str] = {}

# Ключевые слова для определения стиля
STYLE_KEYWORDS = {
    STYLE_CAT: [
        "кошачий", "кот", "котик", "мяу", "кошка", "котята", "мурлыкать", 
        "лапки", "хвостик", "мурчать", "объясни как кот", "как котик", 
        "кошачьим языком", "по-кошачьи"
    ],
    STYLE_VILLAIN: [
        "злодей", "суперзлодей", "злодейски", "мировое господство", "захват мира",
        "муахаха", "зловещий", "темная сторона", "как злодей", "злодейским голосом",
        "злобно", "коварный план", "как суперзлодей"
    ],
    STYLE_DRAMATIC: [
        "драматично", "эпично", "сага", "эпос", "драма", "театрально", 
        "пафосно", "как в кино", "как в фильме", "как в книге", "эпическая история",
        "драматическим голосом", "как рассказчик", "как в легенде"
    ]
}

def load_style_prompt(style: str) -> Optional[str]:
    """
    Загружает промпт для указанного стиля
    
    Args:
        style: Название стиля (normal, cat, villain, dramatic)
        
    Returns:
        Текст промпта или None в случае ошибки
    """
    try:
        # Для обычного стиля используем стандартный системный промпт
        if style == STYLE_NORMAL:
            prompt_path = os.path.join(PROMPTS_DIR, 'system.txt')
        else:
            prompt_path = os.path.join(PROMPTS_DIR, f'{style}_mode.txt')
            
        if not os.path.exists(prompt_path):
            logger.error(f"Промпт для стиля {style} не найден по пути: {prompt_path}")
            # Если промпт не найден, используем стандартный
            prompt_path = os.path.join(PROMPTS_DIR, 'system.txt')
            
        with open(prompt_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.info(f"Загружен промпт для стиля {style} ({len(content)} символов)")
            return content
    except Exception as e:
        logger.error(f"Ошибка при загрузке промпта для стиля {style}: {e}")
        return None

def detect_style_from_text(text: str) -> str:
    """
    Определяет стиль на основе текста сообщения
    
    Args:
        text: Текст сообщения пользователя
        
    Returns:
        Название стиля (normal, cat, villain, dramatic)
    """
    text_lower = text.lower()
    
    # Проверяем наличие явных запросов на определенный стиль
    for style, keywords in STYLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                logger.info(f"Определен стиль {style} по ключевому слову '{keyword}'")
                return style
    
    # Если явных запросов нет, возвращаем обычный стиль
    return STYLE_NORMAL

def get_user_style(chat_id: int, message_text: str) -> str:
    """
    Получает стиль для пользователя на основе его предпочтений и текущего сообщения
    
    Args:
        chat_id: ID чата/пользователя
        message_text: Текст сообщения пользователя
        
    Returns:
        Название стиля (normal, cat, villain, dramatic)
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from src.memory import is_first_bot_message
    
    # Пытаемся определить стиль из текущего сообщения
    detected_style = detect_style_from_text(message_text)
    
    # Если стиль определен из сообщения, обновляем предпочтения пользователя
    if detected_style != STYLE_NORMAL:
        user_styles[chat_id] = detected_style
        return detected_style
    
    # Если это первое сообщение от бота, используем обычный стиль
    if is_first_bot_message(chat_id):
        return STYLE_NORMAL
    
    # Если у пользователя уже есть сохраненный стиль, используем его
    if chat_id in user_styles:
        return user_styles[chat_id]
    
    # После первого сообщения выбираем случайный стиль
    random_styles = [STYLE_CAT, STYLE_VILLAIN, STYLE_DRAMATIC]
    random_style = random.choice(random_styles)
    user_styles[chat_id] = random_style
    logger.info(f"Случайно выбран стиль {random_style} для пользователя {chat_id}")
    return random_style

def set_user_style(chat_id: int, style: str) -> None:
    """
    Устанавливает стиль для пользователя
    
    Args:
        chat_id: ID чата/пользователя
        style: Название стиля (normal, cat, villain, dramatic)
    """
    if style in [STYLE_NORMAL, STYLE_CAT, STYLE_VILLAIN, STYLE_DRAMATIC]:
        user_styles[chat_id] = style
        logger.info(f"Установлен стиль {style} для пользователя {chat_id}")
    else:
        logger.warning(f"Попытка установить неизвестный стиль {style} для пользователя {chat_id}")

def reset_user_style(chat_id: int) -> None:
    """
    Сбрасывает стиль пользователя на обычный
    
    Args:
        chat_id: ID чата/пользователя
    """
    if chat_id in user_styles:
        del user_styles[chat_id]
        logger.info(f"Сброшен стиль для пользователя {chat_id}")

def get_available_styles() -> List[Tuple[str, str]]:
    """
    Возвращает список доступных стилей с их описаниями
    
    Returns:
        Список кортежей (код_стиля, описание)
    """
    return [
        (STYLE_NORMAL, "Обычный режим"),
        (STYLE_CAT, "Переводчик с технического на кошачий"),
        (STYLE_VILLAIN, "Переводчик на язык суперзлодеев"),
        (STYLE_DRAMATIC, "Драматический технический писатель")
    ]