"""
Модуль с функциями валидации данных.

Содержит функции для проверки корректности введённых пользователем данных.
"""
from typing import Tuple
import re


def validate_deadline(deadline: str) -> Tuple[bool, str]:
    """
    Валидирует дату срока выполнения.
    
    Формат: "число месяц год" или "число, месяц, год" (разделители: пробел или запятая)
    Проверяет:
    - число от 1 до 31
    - месяц на русском языке
    - год не выше 2099
    - корректность даты (например, не может быть 30 февраля)
    
    Args:
        deadline: строка с датой в формате "число месяц год" или "число, месяц, год"
    
    Returns:
        tuple: (is_valid, error_message)
        - is_valid: True если дата корректна, False иначе
        - error_message: сообщение об ошибке (пустая строка если валидация прошла)
    """
    # Разбиваем строку по запятым или пробелам (учитываем множественные пробелы)
    # Используем регулярное выражение для разделения по запятым или пробелам
    parts = [part.strip() for part in re.split(r'[,\s]+', deadline) if part.strip()]
    
    if len(parts) != 3:
        return False, "Неверный формат. Используйте: число месяц год (можно через запятую или пробел)"
    
    day_str, month_str, year_str = parts
    
    # Проверяем число (день)
    try:
        day = int(day_str)
        if day < 1 or day > 31:
            return False, "Число должно быть от 1 до 31"
    except ValueError:
        return False, "Число должно быть целым числом от 1 до 31"
    
    # Проверяем месяц на русском языке
    russian_months = [
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"
    ]
    
    # Приводим к нижнему регистру для проверки
    month_lower = month_str.lower()
    
    # Проверяем, является ли месяц русским
    if month_lower not in russian_months:
        # Проверяем, не является ли месяц английским
        english_months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december"
        ]
        if month_lower in english_months:
            return False, "напишите, пожалуйста название месяца на русском языке"
        return False, "Неверное название месяца. Используйте русское название месяца"
    
    # Получаем номер месяца (1-12)
    month_number = russian_months.index(month_lower) + 1
    
    # Проверяем год
    try:
        year = int(year_str)
        if year > 2099:
            return False, "Год не может быть больше 2099"
    except ValueError:
        return False, "Год должен быть целым числом"
    
    # Проверяем корректность даты (количество дней в месяце)
    days_in_month = {
        1: 31,   # январь
        2: 29,   # февраль (максимум, проверка на високосный год ниже)
        3: 31,   # март
        4: 30,   # апрель
        5: 31,   # май
        6: 30,   # июнь
        7: 31,   # июль
        8: 31,   # август
        9: 30,   # сентябрь
        10: 31,  # октябрь
        11: 30,  # ноябрь
        12: 31   # декабрь
    }
    
    max_days = days_in_month[month_number]
    
    # Специальная проверка для февраля (високосный год)
    if month_number == 2:
        # Проверяем, является ли год високосным
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        max_days = 29 if is_leap else 28
    
    if day > max_days:
        month_name = russian_months[month_number - 1]
        return False, f"В {month_name} не может быть {day} дня. Максимум дней: {max_days}"
    
    # Все проверки пройдены
    return True, ""
