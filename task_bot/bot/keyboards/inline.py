"""
Модуль для создания клавиатур бота.

Содержит функции для создания inline-клавиатур с кнопками меню.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт главное меню с кнопками команд.
    
    Returns:
        InlineKeyboardMarkup: клавиатура с кнопками меню
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")
            ],
            [
                InlineKeyboardButton(text="📋 Список задач", callback_data="list_tasks")
            ],
            [
                InlineKeyboardButton(text="🗑️ Удалить задачу", callback_data="delete_task")
            ],
            [
                InlineKeyboardButton(text="📄 Экспорт в CSV", callback_data="export_csv")
            ],
            [
                InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
            ]
        ]
    )
    return keyboard


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру с кнопкой "Пропустить" для опциональных полей.
    
    Returns:
        InlineKeyboardMarkup: клавиатура с кнопкой "Пропустить"
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip")
            ]
        ]
    )
    return keyboard
