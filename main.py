#!/usr/bin/env python3
"""
RAG Telegram Bot с Ragbits для обработки CSV и TXT файлов
Автор: AI Assistant
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag_system import RAGSystem
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramRAGBot:
    def __init__(self, telegram_token: str):
        self.telegram_token = telegram_token
        self.rag_system = RAGSystem()
        self.application = None

    async def initialize(self):
        """Инициализация RAG системы"""
        await self.rag_system.initialize()
        logger.info("RAG система инициализирована")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await update.message.reply_text(
            "Привет! 👋\n\n"
            "Я RAG-бот для работы с базой знаний CAPSULAhair.\n"
            "Вы можете задать мне любой вопрос о:\n"
            "• Специалистах и их портфолио\n"
            "• Бесплатных услугах\n" 
            "• Сертификатах и абонементах\n"
            "• Акциях и услугах\n"
            "• Дополнительной информации о студиях\n\n"
            "Команды:\n"
            "/start - показать это сообщение\n"
            "/help - справка\n"
            "/stats - статистика базы знаний\n"
            "Просто напишите свой вопрос!"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📋 Справка по использованию бота\n\n"
            "Примеры вопросов:\n"
            "• Какие специалисты работают в студии на Арбате?\n"
            "• Сколько бесплатных услуг может получить клиент?\n"
            "• Как работают сертификаты?\n"
            "• Какие дополнительные услуги доступны?\n"
            "• Информация о кератиновом выпрямлении\n\n"
            "Бот найдет релевантную информацию в базе знаний и даст подробный ответ."
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        stats = await self.rag_system.get_stats()
        await update.message.reply_text(
            f"📊 Статистика базы знаний\n\n"
            f"Всего документов: {stats['total_documents']}\n"
            f"Всего фрагментов: {stats['total_chunks']}\n"
            f"Последнее обновление: {stats['last_updated']}"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_message = update.message.text
        user_id = update.effective_user.id

        logger.info(f"Получен запрос от пользователя {user_id}: {user_message}")

        # Показываем индикатор печати
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        try:
            # Получаем ответ от RAG системы
            response = await self.rag_system.query(user_message)

            # Отправляем ответ
            await update.message.reply_text(response['answer'])

            # Логируем успешный ответ
            logger.info(f"Ответ отправлен пользователю {user_id}")

        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            await update.message.reply_text(
                "Извините, произошла ошибка при обработке вашего запроса. "
                "Попробуйте переформулировать вопрос."
            )

    def run(self):
        """Запуск бота"""
        # Создаем приложение
        self.application = Application.builder().token(self.telegram_token).build()

        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Запускаем бота
        logger.info("Запуск Telegram бота...")
        self.application.run_polling()

async def main():
    """Главная функция"""
    bot = TelegramRAGBot(config.TELEGRAM_TOKEN)

    # Инициализируем RAG систему
    await bot.initialize()

    # Запускаем бота
    bot.run()

if __name__ == "__main__":
    asyncio.run(main())
