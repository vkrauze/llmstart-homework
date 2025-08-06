#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Функции для работы с различными сценариями взаимодействия с пользователем
"""
import logging
import re
from typing import Dict, Any, Optional, List
from aiogram import types
from aiogram.utils.markdown import hbold, hlink

from src.llm import generate_response
from src.prompts import create_messages_for_llm
from src.memory import add_message, clear_dialog_history

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_start_command(message: types.Message) -> None:
    """
    Обрабатывает команду /start, реализуя сценарий приветствия
    
    Args:
        message: Сообщение пользователя с командой /start
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Очищаем предыдущую историю диалога
    clear_dialog_history(chat_id)
    
    # Создаем специальный промпт для приветствия
    greeting_prompt = f"Пользователь {user_name} только что запустил бота. Поприветствуй его, представься как ассистент компании ООО \"ТехноСервис\", кратко расскажи о компании и спроси, чем можешь помочь. Ответ должен быть дружелюбным и профессиональным."
    
    # Создаем сообщения для LLM
    messages = create_messages_for_llm(greeting_prompt)
    
    # Получаем ответ от LLM
    response = await generate_response(messages)
    
    if response:
        # Добавляем кликабельные ссылки в ответ
        formatted_response = add_clickable_links(response)
        
        # Отправляем приветственное сообщение с поддержкой HTML-форматирования
        await message.answer(formatted_response, parse_mode="HTML")
        
        # Сохраняем оригинальное приветственное сообщение в историю
        add_message(chat_id, "assistant", response)
        
        logger.info(f"Отправлено приветственное сообщение пользователю {user_id}")
    else:
        # В случае ошибки отправляем стандартное приветствие с кликабельной ссылкой
        website_link = hlink("нашем сайте", "https://technoservice.ru")
        default_greeting = f"Здравствуйте, {user_name}! Я ассистент компании ООО \"ТехноСервис\". Мы специализируемся на IT-консалтинге и разработке программного обеспечения. Более подробную информацию о наших услугах вы можете узнать на {website_link}. Чем я могу вам помочь?"
        await message.answer(default_greeting, parse_mode="HTML")
        
        # Сохраняем стандартное приветствие в историю (без HTML-тегов)
        add_message(chat_id, "assistant", f"Здравствуйте, {user_name}! Я ассистент компании ООО \"ТехноСервис\". Мы специализируемся на IT-консалтинге и разработке программного обеспечения. Более подробную информацию о наших услугах вы можете узнать на нашем сайте. Чем я могу вам помочь?")
        
        logger.error(f"Ошибка при получении приветственного сообщения от LLM для пользователя {user_id}")

async def handle_service_inquiry(message: types.Message, service_type: Optional[str] = None) -> None:
    """
    Обрабатывает запрос о услугах компании
    
    Args:
        message: Сообщение пользователя
        service_type: Тип услуги, если удалось определить
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_text = message.text
    
    # Сохраняем сообщение пользователя в историю
    add_message(chat_id, "user", user_text)
    
    # Создаем специальный промпт для ответа на вопрос об услугах
    if service_type:
        service_prompt = f"Пользователь интересуется услугой '{service_type}'. Предоставь подробную информацию об этой услуге, укажи примерную стоимость и сроки. Предложи дополнительные релевантные услуги."
        messages = create_messages_for_llm(service_prompt, chat_id)
    else:
        # Используем обычный промпт с историей диалога
        messages = create_messages_for_llm(user_text, chat_id)
    
    # Получаем ответ от LLM
    response = await generate_response(messages)
    
    if response:
        # Добавляем кликабельные ссылки в ответ
        formatted_response = add_clickable_links(response)
        
        # Отправляем ответ пользователю с поддержкой HTML-форматирования
        await message.answer(formatted_response, parse_mode="HTML")
        
        # Сохраняем оригинальный ответ в историю
        add_message(chat_id, "assistant", response)
        
        logger.info(f"Отправлен ответ на запрос об услугах пользователю {user_id}")
    else:
        # В случае ошибки отправляем стандартный ответ
        contact_link = hlink("свяжитесь с менеджером", "https://t.me/manager_technoservice")
        default_response = f"Извините, произошла ошибка. Пожалуйста, уточните ваш вопрос или {contact_link}."
        await message.answer(default_response, parse_mode="HTML")
        
        # Сохраняем стандартный ответ в историю (без HTML-тегов)
        add_message(chat_id, "assistant", "Извините, произошла ошибка. Пожалуйста, уточните ваш вопрос или свяжитесь с менеджером.")
        
        logger.error(f"Ошибка при получении ответа от LLM для пользователя {user_id}")

def detect_service_type(message_text: str) -> Optional[str]:
    """
    Определяет тип услуги на основе текста сообщения
    
    Args:
        message_text: Текст сообщения пользователя
        
    Returns:
        Тип услуги или None, если не удалось определить
    """
    message_text = message_text.lower()
    
    # Словарь ключевых слов для определения типа услуги
    service_keywords = {
        "разработка веб": "разработка веб-приложений",
        "сайт": "разработка веб-приложений",
        "интернет-магазин": "разработка веб-приложений",
        "лендинг": "разработка веб-приложений",
        "веб-приложени": "разработка веб-приложений",
        
        "мобильн": "разработка мобильных приложений",
        "ios": "разработка мобильных приложений",
        "android": "разработка мобильных приложений",
        "приложени": "разработка мобильных приложений",
        
        "автоматизац": "автоматизация бизнес-процессов",
        "crm": "автоматизация бизнес-процессов",
        "1с": "автоматизация бизнес-процессов",
        "бизнес-процесс": "автоматизация бизнес-процессов",
        
        "консалтинг": "IT-консалтинг",
        "аудит": "IT-консалтинг",
        "стратег": "IT-консалтинг",
        "оптимизац": "IT-консалтинг"
    }
    
    # Проверяем наличие ключевых слов в тексте сообщения
    for keyword, service in service_keywords.items():
        if keyword in message_text:
            return service
    
    return None

def add_clickable_links(text: str) -> str:
    """
    Добавляет кликабельные ссылки в текст сообщения
    
    Args:
        text: Исходный текст сообщения
        
    Returns:
        Текст с HTML-разметкой для кликабельных ссылок
    """
    # Словарь с ключевыми словами и соответствующими ссылками
    link_keywords = {
        "ООО \"ТехноСервис\"": "https://technoservice.ru",
        "ТехноСервис": "https://technoservice.ru",
        "наш сайт": "https://technoservice.ru",
        "веб-приложений": "https://technoservice.ru/web",
        "мобильных приложений": "https://technoservice.ru/mobile",
        "автоматизация бизнес-процессов": "https://technoservice.ru/automation",
        "IT-консалтинг": "https://technoservice.ru/consulting",
        "менеджер": "https://t.me/manager_technoservice",
        "контакты": "https://technoservice.ru/contacts",
        "+7 (999) 123-45-67": "tel:+79991234567",
        "info@technoservice.ru": "mailto:info@technoservice.ru"
    }
    
    # Заменяем ключевые слова на кликабельные ссылки
    result = text
    for keyword, url in link_keywords.items():
        # Используем регулярное выражение для поиска ключевого слова, учитывая возможные окружающие символы
        pattern = re.compile(f"({re.escape(keyword)})", re.IGNORECASE)
        # Заменяем на HTML-ссылку, сохраняя оригинальный текст
        result = pattern.sub(f'<a href="{url}">\\1</a>', result)
    
    # Безопасно обрабатываем URL-адреса, которые уже есть в тексте
    # Используем более надежный паттерн, который исключает возможность создания невалидных тегов
    url_pattern = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)')
    
    # Создаем список частей текста, чередуя обычный текст и URL
    parts = []
    last_end = 0
    
    for match in url_pattern.finditer(result):
        start, end = match.span()
        url = match.group(1)
        
        # Добавляем текст до URL
        if start > last_end:
            parts.append(result[last_end:start])
        
        # Проверяем, не находится ли URL уже внутри тега <a>
        if "<a href=" not in result[max(0, start-20):start]:
            # Если URL начинается с www., добавляем протокол http://
            href = url if url.startswith(('http://', 'https://')) else f"http://{url}"
            parts.append(f'<a href="{href}">{url}</a>')
        else:
            # Если URL уже в теге, добавляем его как есть
            parts.append(url)
        
        last_end = end
    
    # Добавляем оставшийся текст
    if last_end < len(result):
        parts.append(result[last_end:])
    
    # Объединяем все части
    final_result = ''.join(parts)
    
    # Проверяем на наличие некорректных тегов HTML
    if "<a href=" in final_result and ("><" in final_result or "href=\"\"" in final_result):
        # В случае проблем с HTML-разметкой возвращаем исходный текст
        logger.warning("Обнаружены проблемы с HTML-разметкой, возвращаем исходный текст")
        return text
    
    return final_result