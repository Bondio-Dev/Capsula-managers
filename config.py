"""
Конфигурация для RAG Telegram бота
"""

import os
from pathlib import Path

# Токены и API ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_TOKEN_HERE")
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN", "YOUR_GIGACHAT_TOKEN_HERE")

# Пути к данным
DATA_DIR = Path("data")
VECTOR_DB_PATH = DATA_DIR / "vector_db"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Создаем директории если их нет
DATA_DIR.mkdir(exist_ok=True)
VECTOR_DB_PATH.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)

# Настройки RAG
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 5
SIMILARITY_THRESHOLD = 0.7

# Настройки эмбеддингов
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Настройки ГигаЧат
GIGACHAT_BASE_URL = "https://gigachat.devices.sberbank.ru/api/v1"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Логирование
LOG_LEVEL = "INFO"

# Маппинг файлов из таблицы описания
FILE_MAPPING = {
    "capsulahair_portfolio_v2-links.csv": {
        "name": "CAPSULAhair портфолио",
        "description": "Ссылки портфолио специалистов сети CAPSULAhair с разбивкой по студиям и категориям"
    },
    "free.csv": {
        "name": "Бесплатные услуги", 
        "description": "Информация об учете и контроле предоставления бесплатных услуг клиентам"
    },
    "certificates_studio_certif.csv": {
        "name": "Сертификаты студийные",
        "description": "Сертификаты, проданные в студиях"
    },
    "certificates-certif_online.csv": {
        "name": "Сертификаты онлайн",
        "description": "Сертификаты, проданные онлайн"
    },
    "certificates-partner_certif.csv": {
        "name": "Партнерские сертификаты",
        "description": "Партнерские сертификаты"
    },
    "new-spd.csv": {
        "name": "NEW СПб",
        "description": "Специалисты и услуги в Санкт-Петербурге"
    },
    "new-moscow.csv": {
        "name": "NEW Москва", 
        "description": "Специалисты и услуги в Москве"
    },
    "new-nizhny_novgorod.csv": {
        "name": "NEW Нижний Новгород",
        "description": "Специалисты и услуги в Нижнем Новгороде"
    },
    "docs вопрос-ответ.txt": {
        "name": "Вопросы и ответы",
        "description": "Дополнительная информация о работе студий: краски, оплата, процедуры"
    },
    "frv-list_1.csv": {
        "name": "Система мотивации",
        "description": "Рейтинг стилистов и система мотивации менеджеров"
    }
}
