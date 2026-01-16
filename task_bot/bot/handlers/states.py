"""
Модуль с состояниями FSM (Finite State Machine) для бота.

Используется для пошагового ввода данных при добавлении и удалении задач.
"""
from aiogram.fsm.state import State, StatesGroup


class AddTaskStates(StatesGroup):
    """
    Состояния для процесса добавления задачи.
    
    Последовательность:
    1. waiting_for_text - ожидание текста задачи
    2. waiting_for_responsible - ожидание ФИО ответственного
    3. waiting_for_deadline - ожидание даты завершения
    """
    waiting_for_text = State()  # Ожидание текста задачи
    waiting_for_responsible = State()  # Ожидание ФИО ответственного
    waiting_for_deadline = State()  # Ожидание даты завершения


class DeleteTaskStates(StatesGroup):
    """
    Состояния для процесса удаления задачи.
    """
    waiting_for_task_id = State()  # Ожидание ID задачи для удаления
