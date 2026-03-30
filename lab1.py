# =========================
# Лабораторная работа №1
# =========================

# -------------------------
# ЗАДАЧА 1
# Анализ данных о студентах
# -------------------------

class Student:
    def __init__(self, name, group, grades):
        self.name = name
        self.group = group
        self.grades = grades

    # средний балл
    def average_grade(self):
        return sum(self.grades) / len(self.grades)

    # проверка на отличника
    def is_excellent(self):
        return self.average_grade() >= 4.5


# если файла нет, создаем пример
try:
    with open("students.txt", "r", encoding="utf-8") as f:
        pass
except FileNotFoundError:
    with open("students.txt", "w", encoding="utf-8") as f:
        f.write("Иван;ИВТ-101;5,4,5\n")
        f.write("Анна;ИВТ-101;4,5,5\n")
        f.write("Петр;ПМИ-102;3,4,4\n")
        f.write("Мария;ПМИ-102;5,5,5\n")
        f.write("Олег;ИВТ-101;4,4,4\n")

students = []

with open("students.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            parts = line.split(";")
            name = parts[0]
            group = parts[1]
            grades = list(map(int, parts[2].split(",")))
            students.append(Student(name, group, grades))

# записываем отличников в файл
with open("excellent_students.txt", "w", encoding="utf-8") as f:
    for student in students:
        if student.is_excellent():
            f.write(f"{student.name} - {student.group}\n")

# считаем средний балл по группам
group_data = {}

for student in students:
    if student.group not in group_data:
        group_data[student.group] = []
    group_data[student.group].append(student.average_grade())

print("ЗАДАЧА 1")
for group, averages in group_data.items():
    group_avg = sum(averages) / len(averages)
    print(f"Группа {group}: средний балл = {round(group_avg, 2)}")

print()


# -------------------------
# ЗАДАЧА 2
# Регулярные выражения
# -------------------------

import re

log_text = """
2025-09-10 12:45:33 INFO User admin logged in from 192.168.1.10
2025-09-10 12:47:01 ERROR Failed login from 10.0.0.25 email: user@example.com
2025-09-10 12:50:15 WARNING Disk space LOW on server 172.16.5.100
Contact support at admin@test.org or HELP@MAIL.COM
"""

# шаблоны
ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
time_pattern = r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b"
upper_pattern = r"\b[A-Z]{2,}\b"
email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

ips = re.findall(ip_pattern, log_text)
times = re.findall(time_pattern, log_text)
upper_words = re.findall(upper_pattern, log_text)

# замена email
new_log_text = re.sub(email_pattern, "[EMAIL PROTECTED]", log_text)

print("ЗАДАЧА 2")
print("IPv4 адреса:")
print(ips)

print("\nВременные метки:")
print(times)

print("\nСлова в UPPERCASE:")
print(upper_words)

print("\nТекст после замены email:")
print(new_log_text)

print()


# -------------------------
# ЗАДАЧА 3
# Pandas + matplotlib
# -------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sales_data = {
    "Товар": ["Ноутбук", "Телефон", "Ноутбук", "Планшет", "Телефон", "Планшет", "Ноутбук"],
    "Цена": [50000, 30000, np.nan, 20000, 31000, np.nan, 52000],
    "Количество": [2, 3, 0, 5, 1500, 4, 1]
}

df = pd.DataFrame(sales_data)

# заполняем пропуски медианой
median_price = df["Цена"].median()
df["Цена"] = df["Цена"].fillna(median_price)

# удаляем выбросы по количеству
df = df[(df["Количество"] >= 1) & (df["Количество"] <= 1000)]

# создаем новый столбец
df["Общая_стоимость"] = df["Цена"] * df["Количество"]

# группировка по товару
revenue = df.groupby("Товар")["Общая_стоимость"].sum()

print("ЗАДАЧА 3")
print("DataFrame после обработки:")
print(df)

print("\nВыручка по товарам:")
print(revenue)

# столбчатая диаграмма
plt.figure(figsize=(8, 5))
revenue.plot(kind="bar")
plt.title("Выручка по товарам")
plt.xlabel("Товар")
plt.ylabel("Выручка")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

print()


# -------------------------
# ЗАДАЧА 4
# NumPy
# -------------------------

import numpy as np

np.random.seed(42)

# создаем матрицы 5x5
A = np.random.randint(1, 11, (5, 5))
B = np.random.randint(1, 11, (5, 5))

print("ЗАДАЧА 4")
print("Матрица A:")
print(A)

print("\nМатрица B:")
print(B)

# поэлементное произведение
elementwise = A * B
print("\nПоэлементное произведение:")
print(elementwise)

# матричное произведение
matrix_product = A @ B
print("\nМатричное произведение:")
print(matrix_product)

# определитель A
det_A = np.linalg.det(A)
print("\nОпределитель матрицы A:")
print(det_A)

# транспонированная матрица B
B_T = B.T
print("\nТранспонированная матрица B:")
print(B_T)

# обратная матрица A
print("\nОбратная матрица A:")
try:
    A_inv = np.linalg.inv(A)
    print(A_inv)
except np.linalg.LinAlgError:
    print("Обратная матрица не существует")

# решаем систему A * x = C
C = A.sum(axis=1)
print("\nВектор C (суммы строк A):")
print(C)

try:
    x = np.linalg.solve(A, C)
    print("\nРешение системы A * x = C:")
    print(x)
except np.linalg.LinAlgError:
    print("\nСистему нельзя решить, матрица A вырожденная")

print()


# -------------------------
# ЗАДАЧА 5
# safe_apply + lambda
# -------------------------

import math

def safe_apply(func, data):
    results = []
    errors = []

    for element in data:
        try:
            result = func(element)
            results.append(result)
        except Exception as e:
            errors.append((element, type(e).__name__))

    return results, errors


data = ['4', '16', 'text', '-25', '9.0']

# лямбда для квадратного корня
func = lambda x: math.sqrt(float(x))

results, errors = safe_apply(func, data)

print("ЗАДАЧА 5")
print("Успешные результаты:")
print(results)

print("\nОшибки:")
print(errors)
