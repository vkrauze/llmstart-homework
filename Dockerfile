FROM python:3.11-slim

WORKDIR /app

# Копирование файлов проекта
COPY pyproject.toml .
COPY requirements.txt .
COPY src/ ./src/
COPY prompts/ ./prompts/

# Установка зависимостей напрямую из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Установка проекта в режиме разработки
RUN pip install -e .

# Создание директории для логов
RUN mkdir -p logs

# Создание файла .env (будет заполнен при запуске)
RUN touch .env

# Запуск приложения
CMD ["python", "src/main.py"]