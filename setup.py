#!/usr/bin/env python3
"""
Скрипт первоначальной настройки RAG Telegram бота
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "data",
        "data/documents", 
        "data/vector_db",
        "logs"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана директория: {directory}")

def check_env_file():
    """Проверка файла окружения"""
    if not Path(".env").exists():
        print("⚠️  Файл .env не найден!")
        print("📋 Скопируйте .env.example в .env и заполните токены")
        return False
    return True

def check_data_files():
    """Проверка наличия файлов данных"""
    data_dir = Path("data/documents")
    files = list(data_dir.glob("*"))

    if not files:
        print("⚠️  Файлы данных не найдены!")
        print(f"📁 Поместите CSV и TXT файлы в директорию: {data_dir}")
        return False

    print(f"✅ Найдено файлов данных: {len(files)}")
    return True

def main():
    """Основная функция настройки"""
    print("🚀 Настройка RAG Telegram бота...")
    print("="*50)

    # Создаем директории
    create_directories()

    # Проверяем окружение
    env_ok = check_env_file()

    # Проверяем данные
    data_ok = check_data_files()

    print("="*50)

    if env_ok and data_ok:
        print("✅ Настройка завершена!")
        print("🔄 Выполните: python prepare_database.py")
        print("🚀 Затем запустите: python main.py")
    else:
        print("❌ Настройка не завершена!")
        print("📋 Выполните все необходимые шаги")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
