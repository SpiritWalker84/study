"""
Модуль с обработчиками команд бота.

Содержит функции-обработчики для команд:
- /start - приветствие с меню
- /add - добавление задачи (через FSM)
- /list - вывод списка задач
- /list_csv - отправка CSV-файла с задачами
- обработчики callback для кнопок меню
"""
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import csv
import io

from bot.database.db import Database
from bot.keyboards.inline import get_main_menu_keyboard, get_skip_keyboard
from bot.handlers.states import AddTaskStates


# Создаём роутер для команд
router = Router()

# Создаём объект для работы с базой данных
db = Database()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    
    Приветствует пользователя и показывает меню с кнопками.
    
    Args:
        message: объект сообщения от пользователя
    """
    welcome_text = (
        "👋 Привет! Я бот для командной работы с задачами.\n\n"
        "Используй кнопки меню ниже для работы с задачами:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


# Обработчики callback для кнопок меню
@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """
    Обработчик кнопки "Помощь".
    
    Args:
        callback: объект callback-запроса
    """
    help_text = (
        "ℹ️ Доступные команды:\n\n"
        "➕ Добавить задачу - создать новую задачу\n"
        "📋 Список задач - посмотреть все задачи\n"
        "📄 Экспорт в CSV - скачать файл со всеми задачами\n\n"
        "Также можно использовать команды:\n"
        "/start - показать меню\n"
        "/add - добавить задачу\n"
        "/list - список задач\n"
        "/list_csv - экспорт в CSV"
    )
    await callback.message.answer(help_text)
    await callback.answer()


@router.callback_query(F.data == "add_task")
async def callback_add_task(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Добавить задачу".
    
    Начинает процесс добавления задачи через FSM.
    
    Args:
        callback: объект callback-запроса
        state: контекст FSM
    """
    await callback.message.answer(
        "📝 Введите название задачи:"
    )
    await state.set_state(AddTaskStates.waiting_for_text)
    await callback.answer()


@router.message(AddTaskStates.waiting_for_text)
async def process_task_text(message: Message, state: FSMContext):
    """
    Обработчик ввода текста задачи.
    
    Сохраняет текст задачи и запрашивает ФИО ответственного.
    
    Args:
        message: объект сообщения от пользователя
        state: контекст FSM
    """
    task_text = message.text.strip()
    
    if not task_text:
        await message.answer("❌ Текст задачи не может быть пустым. Введите название задачи:")
        return
    
    # Сохраняем текст задачи в состоянии
    await state.update_data(task_text=task_text)
    
    # Запрашиваем ФИО ответственного
    await message.answer(
        "👤 Введите ФИО ответственного за задачу:\n"
        "(или нажмите кнопку 'Пропустить', если не нужно)",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(AddTaskStates.waiting_for_responsible)


@router.callback_query(F.data == "skip", StateFilter(AddTaskStates.waiting_for_responsible))
async def skip_responsible(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Пропустить" для ответственного.
    
    Args:
        callback: объект callback-запроса
        state: контекст FSM
    """
    await callback.message.answer(
        "📅 Введите дату завершения в формате: число, месяц, год\n"
        "Например: 25, январь, 2025\n"
        "(или нажмите кнопку 'Пропустить', если не нужно)",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(AddTaskStates.waiting_for_deadline)
    await callback.answer()


@router.message(AddTaskStates.waiting_for_responsible)
async def process_responsible(message: Message, state: FSMContext):
    """
    Обработчик ввода ФИО ответственного.
    
    Сохраняет ФИО и запрашивает дату завершения.
    
    Args:
        message: объект сообщения от пользователя
        state: контекст FSM
    """
    responsible = message.text.strip()
    
    # Сохраняем ФИО ответственного
    await state.update_data(responsible=responsible)
    
    # Запрашиваем дату завершения
    await message.answer(
        "📅 Введите дату завершения в формате: число, месяц, год\n"
        "Например: 25, январь, 2025\n"
        "(или нажмите кнопку 'Пропустить', если не нужно)",
        reply_markup=get_skip_keyboard()
    )
    await state.set_state(AddTaskStates.waiting_for_deadline)


@router.callback_query(F.data == "skip", StateFilter(AddTaskStates.waiting_for_deadline))
async def skip_deadline(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Пропустить" для даты завершения.
    
    Завершает процесс добавления задачи.
    
    Args:
        callback: объект callback-запроса
        state: контекст FSM
    """
    # Получаем все данные из состояния
    data = await state.get_data()
    task_text = data.get("task_text")
    responsible = data.get("responsible")
    deadline = None
    
    # Получаем имя пользователя
    user_name = callback.from_user.username or callback.from_user.first_name or "Неизвестный"
    
    try:
        # Добавляем задачу в базу данных
        task_id = db.add_task(task_text, user_name, responsible, deadline)
        
        result_text = (
            f"✅ Задача добавлена!\n\n"
            f"ID: {task_id}\n"
            f"Задача: {task_text}\n"
        )
        
        if responsible:
            result_text += f"Ответственный: {responsible}\n"
        if deadline:
            result_text += f"Срок: {deadline}\n"
        
        await callback.message.answer(result_text, reply_markup=get_main_menu_keyboard())
        await state.clear()
        await callback.answer()
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при добавлении задачи: {e}")
        await state.clear()
        await callback.answer()


@router.message(AddTaskStates.waiting_for_deadline)
async def process_deadline(message: Message, state: FSMContext):
    """
    Обработчик ввода даты завершения.
    
    Сохраняет дату и завершает процесс добавления задачи.
    
    Args:
        message: объект сообщения от пользователя
        state: контекст FSM
    """
    deadline = message.text.strip()
    
    # Получаем все данные из состояния
    data = await state.get_data()
    task_text = data.get("task_text")
    responsible = data.get("responsible")
    
    # Получаем имя пользователя
    user_name = message.from_user.username or message.from_user.first_name or "Неизвестный"
    
    try:
        # Добавляем задачу в базу данных
        task_id = db.add_task(task_text, user_name, responsible, deadline)
        
        result_text = (
            f"✅ Задача добавлена!\n\n"
            f"ID: {task_id}\n"
            f"Задача: {task_text}\n"
        )
        
        if responsible:
            result_text += f"Ответственный: {responsible}\n"
        if deadline:
            result_text += f"Срок: {deadline}\n"
        
        await message.answer(result_text, reply_markup=get_main_menu_keyboard())
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении задачи: {e}")
        await state.clear()


# Старый обработчик /add для обратной совместимости
@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """
    Обработчик команды /add (для обратной совместимости).
    
    Начинает процесс добавления задачи через FSM.
    
    Args:
        message: объект сообщения от пользователя
        state: контекст FSM
    """
    await message.answer("📝 Введите название задачи:")
    await state.set_state(AddTaskStates.waiting_for_text)


@router.callback_query(F.data == "list_tasks")
async def callback_list_tasks(callback: CallbackQuery):
    """
    Обработчик кнопки "Список задач".
    
    Выводит список всех задач.
    
    Args:
        callback: объект callback-запроса
    """
    try:
        # Получаем все задачи из базы данных
        tasks = db.get_all_tasks()
        
        if not tasks:
            await callback.message.answer(
                "📝 Список задач пуст. Добавьте первую задачу через меню.",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Формируем текст со списком задач
        tasks_text = "📋 Список всех задач:\n\n"
        for task in tasks:
            task_id, text, user, responsible, deadline, created_at = task
            tasks_text += (
                f"ID: {task_id}\n"
                f"Задача: {text}\n"
                f"Пользователь: {user}\n"
            )
            if responsible:
                tasks_text += f"Ответственный: {responsible}\n"
            if deadline:
                tasks_text += f"Срок: {deadline}\n"
            tasks_text += f"Создано: {created_at}\n"
            tasks_text += f"{'-' * 30}\n"
        
        # Отправляем список с меню
        await callback.message.answer(tasks_text, reply_markup=get_main_menu_keyboard())
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при получении списка задач: {e}")
        await callback.answer()


@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Обработчик команды /list.
    
    Выводит список всех задач из базы данных.
    
    Args:
        message: объект сообщения от пользователя
    """
    try:
        # Получаем все задачи из базы данных
        tasks = db.get_all_tasks()
        
        if not tasks:
            await message.answer(
                "📝 Список задач пуст. Добавьте первую задачу командой /add",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Формируем текст со списком задач
        tasks_text = "📋 Список всех задач:\n\n"
        for task in tasks:
            task_id, text, user, responsible, deadline, created_at = task
            tasks_text += (
                f"ID: {task_id}\n"
                f"Задача: {text}\n"
                f"Пользователь: {user}\n"
            )
            if responsible:
                tasks_text += f"Ответственный: {responsible}\n"
            if deadline:
                tasks_text += f"Срок: {deadline}\n"
            tasks_text += f"Создано: {created_at}\n"
            tasks_text += f"{'-' * 30}\n"
        
        # Отправляем список с меню
        await message.answer(tasks_text, reply_markup=get_main_menu_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка задач: {e}")


@router.callback_query(F.data == "export_csv")
async def callback_export_csv(callback: CallbackQuery):
    """
    Обработчик кнопки "Экспорт в CSV".
    
    Создаёт CSV-файл со всеми задачами и отправляет его пользователю.
    
    Args:
        callback: объект callback-запроса
    """
    try:
        # Получаем все задачи из базы данных
        tasks = db.get_tasks_for_csv()
        
        if not tasks:
            await callback.message.answer(
                "📝 Список задач пуст. Добавьте первую задачу через меню.",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Создаём CSV-файл в памяти
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Записываем заголовки
        writer.writerow(["ID", "Текст задачи", "Пользователь", "Ответственный", "Срок", "Дата создания"])
        
        # Записываем все задачи
        for task in tasks:
            task_id, text, user, responsible, deadline, created_at = task
            writer.writerow([
                task_id, 
                text, 
                user, 
                responsible or "", 
                deadline or "", 
                created_at
            ])
        
        # Преобразуем в байты для отправки
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')  # utf-8-sig для корректного отображения в Excel
        csv_buffer.close()
        
        # Создаём файл для отправки
        csv_file = BufferedInputFile(csv_bytes, filename="tasks.csv")
        
        # Отправляем файл пользователю
        await callback.message.answer_document(
            csv_file,
            caption="📄 CSV-файл со всеми задачами"
        )
        # Показываем меню после отправки файла
        await callback.message.answer("✅ Файл отправлен!", reply_markup=get_main_menu_keyboard())
        await callback.answer()
        
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при создании CSV-файла: {e}")
        await callback.answer()


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message):
    """
    Обработчик команды /list_csv.
    
    Создаёт CSV-файл со всеми задачами и отправляет его пользователю.
    
    Args:
        message: объект сообщения от пользователя
    """
    try:
        # Получаем все задачи из базы данных
        tasks = db.get_tasks_for_csv()
        
        if not tasks:
            await message.answer(
                "📝 Список задач пуст. Добавьте первую задачу командой /add",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Создаём CSV-файл в памяти
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        # Записываем заголовки
        writer.writerow(["ID", "Текст задачи", "Пользователь", "Ответственный", "Срок", "Дата создания"])
        
        # Записываем все задачи
        for task in tasks:
            task_id, text, user, responsible, deadline, created_at = task
            writer.writerow([
                task_id, 
                text, 
                user, 
                responsible or "", 
                deadline or "", 
                created_at
            ])
        
        # Преобразуем в байты для отправки
        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')  # utf-8-sig для корректного отображения в Excel
        csv_buffer.close()
        
        # Создаём файл для отправки
        csv_file = BufferedInputFile(csv_bytes, filename="tasks.csv")
        
        # Отправляем файл пользователю
        await message.answer_document(
            csv_file,
            caption="📄 CSV-файл со всеми задачами"
        )
        # Показываем меню после отправки файла
        await message.answer("✅ Файл отправлен!", reply_markup=get_main_menu_keyboard())
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании CSV-файла: {e}")
