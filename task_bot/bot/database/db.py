"""
Модуль для работы с базой данных SQLite3.

Содержит класс Database для управления задачами:
- создание таблицы tasks
- добавление задач
- получение всех задач
- получение задач в формате для CSV
"""
import sqlite3
from datetime import datetime
from typing import List, Tuple


class Database:
    """
    Класс для работы с базой данных SQLite3.
    
    Отвечает за все операции с задачами:
    создание таблицы, добавление, получение списка задач.
    """
    
    def __init__(self, db_name: str = "tasks.db"):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_name: имя файла базы данных (по умолчанию tasks.db)
        """
        self.db_name = db_name
        # Создаём таблицу при инициализации
        self.create_table()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Создаёт и возвращает подключение к базе данных.
        
        Returns:
            sqlite3.Connection: объект подключения к БД
        """
        return sqlite3.connect(self.db_name)
    
    def create_table(self):
        """
        Создаёт таблицу tasks, если она ещё не существует.
        
        Структура таблицы:
        - id: уникальный идентификатор (автоинкремент)
        - text: текст задачи
        - user: имя пользователя, который добавил задачу
        - responsible: ФИО ответственного (может быть NULL)
        - deadline: дата завершения в формате "число, месяц, год" (может быть NULL)
        - created_at: дата и время создания задачи
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # SQL-запрос для создания таблицы
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                user TEXT NOT NULL,
                responsible TEXT,
                deadline TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Добавляем новые колонки, если таблица уже существовала
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN responsible TEXT")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN deadline TEXT")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        conn.commit()
        conn.close()
    
    def add_task(self, text: str, user: str, responsible: str = None, deadline: str = None) -> int:
        """
        Добавляет новую задачу в базу данных.
        
        Args:
            text: текст задачи
            user: имя пользователя (username или first_name)
            responsible: ФИО ответственного (опционально)
            deadline: дата завершения в формате "число, месяц, год" (опционально)
        
        Returns:
            int: ID добавленной задачи
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем текущую дату и время в формате строки
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Вставляем новую задачу
        cursor.execute(
            "INSERT INTO tasks (text, user, responsible, deadline, created_at) VALUES (?, ?, ?, ?, ?)",
            (text, user, responsible, deadline, created_at)
        )
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_all_tasks(self) -> List[Tuple]:
        """
        Получает все задачи из базы данных.
        
        Returns:
            List[Tuple]: список кортежей (id, text, user, responsible, deadline, created_at)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем все задачи, отсортированные по дате создания
        cursor.execute("SELECT id, text, user, responsible, deadline, created_at FROM tasks ORDER BY created_at DESC")
        tasks = cursor.fetchall()
        
        conn.close()
        return tasks
    
    def get_tasks_for_csv(self) -> List[Tuple]:
        """
        Получает все задачи в формате для экспорта в CSV.
        
        Returns:
            List[Tuple]: список кортежей (id, text, user, responsible, deadline, created_at)
        """
        # Используем тот же метод, что и для обычного списка
        return self.get_all_tasks()
    
    def delete_task(self, task_id: int) -> bool:
        """
        Удаляет задачу по ID.
        
        Args:
            task_id: ID задачи для удаления
        
        Returns:
            bool: True если задача удалена, False если задача не найдена
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, существует ли задача
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        
        if not task:
            conn.close()
            return False
        
        # Удаляем задачу
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def get_task_by_id(self, task_id: int) -> Tuple | None:
        """
        Получает задачу по ID.
        
        Args:
            task_id: ID задачи
        
        Returns:
            Tuple | None: кортеж (id, text, user, responsible, deadline, created_at) или None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, text, user, responsible, deadline, created_at FROM tasks WHERE id = ?",
            (task_id,)
        )
        task = cursor.fetchone()
        
        conn.close()
        return task
