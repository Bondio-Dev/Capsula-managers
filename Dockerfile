FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для данных
RUN mkdir -p data/documents data/vector_db logs

# Подготавливаем базу данных при первом запуске
RUN python prepare_database.py || true

# Запускаем бота
CMD ["python", "main.py"]
