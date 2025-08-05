#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест для проверки чтения .env файла
"""
import os
import os.path
from dotenv import load_dotenv

# Проверяем текущую директорию
current_dir = os.getcwd()
print(f"Текущая директория: {current_dir}")

# Проверяем содержимое директории
print("Содержимое директории:")
for item in os.listdir(current_dir):
    print(f"- {item}")

# Пытаемся загрузить .env из текущей директории
load_dotenv()
print(f"TELEGRAM_BOT_TOKEN из текущей директории = {os.getenv('TELEGRAM_BOT_TOKEN')}")

# Пытаемся загрузить .env из корня проекта
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"Путь к .env файлу: {env_path}")
print(f"Файл существует: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        print(f"Содержимое .env файла:")
        print(f.read())

load_dotenv(dotenv_path=env_path)
print(f"TELEGRAM_BOT_TOKEN из указанного пути = {os.getenv('TELEGRAM_BOT_TOKEN')}")