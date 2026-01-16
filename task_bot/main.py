"""
Главный файл для запуска Telegram-бота.

Это точка входа в приложение. Здесь происходит:
- загрузка переменных окружения из .env
- инициализация бота и диспетчера
- регистрация обработчиков команд
- запуск бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from bot.handlers import commands


# Настройка логирования (для отладки)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Главная функция для запуска бота.
    
    Загружает переменные окружения, создаёт бота и диспетчер,
    регистрирует обработчики и запускает polling.
    """
    # Загружаем переменные окружения из файла .env
    load_dotenv()
    
    # Получаем токен бота из переменных окружения
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        logger.error("Создайте файл .env и добавьте туда BOT_TOKEN=ваш_токен")
        return
    
    # Создаём объект бота
    # Используем обычный текст без HTML-разметки, чтобы избежать проблем с эмодзи
    bot = Bot(token=bot_token)
    
    # Создаём хранилище для FSM (Finite State Machine)
    # MemoryStorage хранит состояния в памяти (при перезапуске бота состояния сбросятся)
    storage = MemoryStorage()
    
    # Создаём диспетчер (управляет обработчиками сообщений)
    # Передаём storage для работы с FSM
    dp = Dispatcher(storage=storage)
    
    # Регистрируем роутер с обработчиками команд
    dp.include_router(commands.router)
    
    logger.info("Бот запущен и готов к работе!")
    
    # Запускаем polling (постоянное ожидание новых сообщений)
    # skip_updates=True означает, что бот не будет обрабатывать старые сообщения
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    """
    Точка входа в программу.
    
    Запускает асинхронную функцию main().
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
