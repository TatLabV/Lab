
import sqlite3


DB_PATH = "university.db"



#1. Создание базы данных


def create_database():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                admission_year INTEGER NOT NULL,
                average_grade REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT UNIQUE NOT NULL,
                instructor TEXT NOT NULL,
                credits INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_courses (
                student_id INTEGER,
                course_id INTEGER,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
            """)

            print("База данных и таблицы созданы")
    except sqlite3.Error as e:
        print("Ошибка при создании базы данных:", e)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn



#2. CRUD для студентов


def add_student(first_name, last_name, group_name, admission_year, average_grade=None):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (first_name, last_name, group_name, admission_year, average_grade)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, group_name, admission_year, average_grade))
            return cursor.lastrowid
    except sqlite3.Error as e:
        print("Ошибка при добавлении студента:", e)
        return None


def get_all_students():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print("Ошибка при получении студентов:", e)
        return []


def get_students_by_group(group_name):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE group_name = ? ORDER BY last_name", (group_name,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print("Ошибка при получении студентов группы:", e)
        return []


def update_student_grade(student_id, new_grade):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET average_grade = ? WHERE id = ?", (new_grade, student_id))
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print("Ошибка при обновлении оценки:", e)
        return False


def delete_student(student_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print("Ошибка при удалении студента:", e)
        return False



#3. Курсы и транзакции


def add_course(course_name, instructor, credits):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO courses (course_name, instructor, credits)
                VALUES (?, ?, ?)
            """, (course_name, instructor, credits))
            return cursor.lastrowid
    except sqlite3.Error as e:
        print("Ошибка при добавлении курса:", e)
        return None


def enroll_student_in_course(student_id, course_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
            if cursor.fetchone() is None:
                print("Студент не найден")
                return False

            cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
            if cursor.fetchone() is None:
                print("Курс не найден")
                return False

            cursor.execute("""
                INSERT OR IGNORE INTO student_courses (student_id, course_id)
                VALUES (?, ?)
            """, (student_id, course_id))
            return True
    except sqlite3.Error as e:
        print("Ошибка при записи на курс:", e)
        return False


def get_student_courses(student_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.course_name, c.instructor, c.credits
                FROM courses c
                JOIN student_courses sc ON c.id = sc.course_id
                WHERE sc.student_id = ?
                ORDER BY c.course_name
            """, (student_id,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print("Ошибка при получении курсов студента:", e)
        return []


def get_course_students(course_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.first_name, s.last_name, s.group_name
                FROM students s
                JOIN student_courses sc ON s.id = sc.student_id
                WHERE sc.course_id = ?
                ORDER BY s.last_name
            """, (course_id,))
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print("Ошибка при получении студентов курса:", e)
        return []


def transfer_student(student_id, new_group):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
            if cursor.fetchone() is None:
                print("Студент не найден")
                return False

            conn.execute("BEGIN")

            cursor.execute("UPDATE students SET group_name = ? WHERE id = ?", (new_group, student_id))
            cursor.execute("DELETE FROM student_courses WHERE student_id = ?", (student_id,))

            conn.commit()
            print("Студент переведен в новую группу, старые курсы очищены")
            return True
    except sqlite3.Error as e:
        print("Ошибка при переводе студента:", e)
        return False



#4. Класс-обертка


class UniversityDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            return True
        except sqlite3.Error as e:
            print("Ошибка execute_query:", e)
            return False

    def fetch_all(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print("Ошибка fetch_all:", e)
            return []

    def fetch_one(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print("Ошибка fetch_one:", e)
            return None

    def add_student(self, first_name, last_name, group_name, admission_year, average_grade=None):
        return self.execute_query("""
            INSERT INTO students (first_name, last_name, group_name, admission_year, average_grade)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, group_name, admission_year, average_grade))

    def get_student_statistics(self):
        total = self.fetch_one("SELECT COUNT(*) AS total_students, AVG(average_grade) AS avg_grade FROM students")
        groups = self.fetch_all("""
            SELECT group_name, COUNT(*) AS student_count
            FROM students
            GROUP BY group_name
            ORDER BY group_name
        """)
        return {
            "total_students": total["total_students"] if total else 0,
            "avg_grade": round(total["avg_grade"], 2) if total and total["avg_grade"] is not None else None,
            "groups": groups
        }

    def get_top_students(self, limit=5):
        return self.fetch_all("""
            SELECT id, first_name, last_name, group_name, average_grade
            FROM students
            WHERE average_grade IS NOT NULL
            ORDER BY average_grade DESC, last_name ASC
            LIMIT ?
        """, (limit,))

    def get_group_statistics(self):
        return self.fetch_all("""
            SELECT
                group_name,
                COUNT(*) AS student_count,
                ROUND(AVG(average_grade), 2) AS avg_group_grade
            FROM students
            GROUP BY group_name
            ORDER BY group_name
        """)

    def find_students_by_last_name(self, last_name_part):
        return self.fetch_all("""
            SELECT * FROM students
            WHERE last_name LIKE ?
            ORDER BY last_name, first_name
        """, (f"%{last_name_part}%",))

    def update_student_grade(self, student_id, new_grade):
        return self.execute_query(
            "UPDATE students SET average_grade = ? WHERE id = ?",
            (new_grade, student_id)
        )

    def delete_student(self, student_id):
        return self.execute_query(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )



#5. Консольное приложение


def print_students_table(students):
    if not students:
        print("Нет данных")
        return

    print("-" * 85)
    print(f"{'ID':<5}{'Имя':<15}{'Фамилия':<20}{'Группа':<12}{'Год':<10}{'Средний балл':<15}")
    print("-" * 85)
    for s in students:
        grade = s["average_grade"] if s["average_grade"] is not None else "-"
        print(f"{s['id']:<5}{s['first_name']:<15}{s['last_name']:<20}{s['group_name']:<12}{s['admission_year']:<10}{str(grade):<15}")
    print("-" * 85)


def add_student_interactive():
    print("\n--- Добавление студента ---")
    first_name = input("Имя: ").strip()
    last_name = input("Фамилия: ").strip()
    group_name = input("Группа: ").strip()

    while True:
        try:
            admission_year = int(input("Год поступления: "))
            if 2000 <= admission_year <= 2030:
                break
            print("Год должен быть между 2000 и 2030")
        except ValueError:
            print("Введите корректный год")

    while True:
        grade_text = input("Средний балл (можно пусто): ").strip()
        if grade_text == "":
            average_grade = None
            break
        try:
            average_grade = float(grade_text)
            if 0 <= average_grade <= 5:
                break
            print("Средний балл должен быть от 0 до 5")
        except ValueError:
            print("Введите число")

    with UniversityDB(DB_PATH) as db:
        if db.add_student(first_name, last_name, group_name, admission_year, average_grade):
            print("Студент успешно добавлен")
        else:
            print("Ошибка при добавлении студента")


def display_all_students():
    with UniversityDB(DB_PATH) as db:
        students = db.fetch_all("SELECT * FROM students ORDER BY id")
    print_students_table(students)


def search_student_by_last_name():
    last_name = input("Введите фамилию или ее часть: ").strip()
    with UniversityDB(DB_PATH) as db:
        students = db.find_students_by_last_name(last_name)
    print_students_table(students)


def update_student_grade_interactive():
    try:
        student_id = int(input("ID студента: "))
        new_grade = float(input("Новый средний балл: "))
        if not (0 <= new_grade <= 5):
            print("Оценка должна быть от 0 до 5")
            return
    except ValueError:
        print("Некорректный ввод")
        return

    with UniversityDB(DB_PATH) as db:
        if db.update_student_grade(student_id, new_grade):
            print("Оценка обновлена")
        else:
            print("Не удалось обновить оценку")


def delete_student_interactive():
    try:
        student_id = int(input("ID студента для удаления: "))
    except ValueError:
        print("Некорректный ID")
        return

    with UniversityDB(DB_PATH) as db:
        if db.delete_student(student_id):
            print("Студент удален")
        else:
            print("Не удалось удалить студента")


def show_statistics():
    with UniversityDB(DB_PATH) as db:
        stats = db.get_student_statistics()
        top_students = db.get_top_students()
        group_stats = db.get_group_statistics()

    print("\n=== Общая статистика ===")
    print("Всего студентов:", stats["total_students"])
    print("Средний балл по университету:", stats["avg_grade"])

    print("\n=== Статистика по группам ===")
    for g in group_stats:
        print(f"Группа {g['group_name']}: студентов {g['student_count']}, средний балл {g['avg_group_grade']}")

    print("\n=== Топ студентов ===")
    for s in top_students:
        print(f"{s['first_name']} {s['last_name']} ({s['group_name']}) - {s['average_grade']}")


def fill_demo_data():
    if get_all_students():
        return

    s1 = add_student("Иван", "Петров", "ГР-01", 2023, 4.5)
    s2 = add_student("Мария", "Иванова", "ГР-01", 2023, 4.8)
    s3 = add_student("Алексей", "Сидоров", "ГР-02", 2023, 3.9)

    c1 = add_course("Математика", "Проф. Иванов", 5)
    c2 = add_course("Физика", "Проф. Петрова", 4)
    c3 = add_course("Программирование", "Доц. Сидоров", 6)

    if s1 and c1:
        enroll_student_in_course(s1, c1)
    if s1 and c3:
        enroll_student_in_course(s1, c3)
    if s3 and c2:
        enroll_student_in_course(s3, c2)


def main():
    create_database()
    fill_demo_data()

    while True:
        print("\n=== Университетский учет ===")
        print("1. Добавить студента")
        print("2. Просмотреть всех студентов")
        print("3. Найти студента по фамилии")
        print("4. Обновить оценку студента")
        print("5. Удалить студента")
        print("6. Показать статистику")
        print("7. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            add_student_interactive()
        elif choice == "2":
            display_all_students()
        elif choice == "3":
            search_student_by_last_name()
        elif choice == "4":
            update_student_grade_interactive()
        elif choice == "5":
            delete_student_interactive()
        elif choice == "6":
            show_statistics()
        elif choice == "7":
            print("Выход из программы")
            break
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()
