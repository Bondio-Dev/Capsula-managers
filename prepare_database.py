#!/usr/bin/env python3
"""
Скрипт для подготовки базы данных RAG системы
Загружает и индексирует все CSV и TXT файлы
"""

import asyncio
import logging
from pathlib import Path
from rag_system import RAGSystem
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Подготовка базы данных"""
    print("🚀 Подготовка базы данных для RAG системы...")

    # Проверяем наличие файлов данных
    if not config.DOCUMENTS_DIR.exists():
        print(f"❌ Директория {config.DOCUMENTS_DIR} не существует!")
        print("Создайте папку 'data/documents' и поместите туда CSV и TXT файлы")
        return

    files = list(config.DOCUMENTS_DIR.glob("*"))
    if not files:
        print(f"❌ В директории {config.DOCUMENTS_DIR} нет файлов!")
        return

    print(f"📁 Найдено файлов: {len(files)}")
    for file in files:
        print(f"  - {file.name}")

    # Инициализируем RAG систему
    rag_system = RAGSystem()

    try:
        await rag_system.initialize()

        stats = await rag_system.get_stats()
        print("✅ База данных успешно подготовлена!")
        print(f"📊 Статистика:")
        print(f"  - Обработано файлов: {stats['total_documents']}")
        print(f"  - Создано фрагментов: {stats['total_chunks']}")
        print(f"  - Время обновления: {stats['last_updated']}")

    except Exception as e:
        print(f"❌ Ошибка подготовки базы данных: {e}")
        logger.error(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
