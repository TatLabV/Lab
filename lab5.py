
# =========================
# Lab 5: Управление потоками в Python
# =========================

import time
import threading
import multiprocessing
import math
import asyncio
import aiohttp
import random
from datetime import datetime
import concurrent.futures

# -------------------------
# ЗАДАЧА 1: Синхронный калькулятор
# -------------------------

def sync_calculate(operation, a, b, delay):
    print(f"Начало операции {a} {operation} {b}")
    time.sleep(delay)

    if operation == '+':
        result = a + b
    elif operation == '-':
        result = a - b
    elif operation == '*':
        result = a * b
    elif operation == '/':
        result = a / b if b != 0 else 'Ошибка'
    else:
        result = 'Ошибка'

    print(f"Конец операции {a} {operation} {b} = {result}")
    return result


def task1():
    start = time.time()

    results = []
    results.append(sync_calculate('+', 15, 25, 2))
    results.append(sync_calculate('-', 40, 18, 1))
    results.append(sync_calculate('*', 12, 8, 3))
    results.append(sync_calculate('/', 100, 5, 1))

    end = time.time()
    print("ЗАДАЧА 1")
    print("Результаты:", results)
    print("Время:", round(end - start, 2), "сек\n")


# -------------------------
# ЗАДАЧА 2: Потоки
# -------------------------

def download_file(name, size):
    print(f"Начало загрузки {name}")
    for i in range(5):
        time.sleep(size * 0.02)
        print(f"{name}: {(i+1)*20}%")
    print(f"Завершена загрузка {name}")


def task2():
    files = [
        ("doc.pdf", 10),
        ("img.jpg", 5),
        ("video.mp4", 20),
        ("archive.zip", 15)
    ]

    start = time.time()
    threads = []

    for f in files:
        t = threading.Thread(target=download_file, args=f)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()
    print("ЗАДАЧА 2")
    print("Время:", round(end - start, 2), "сек\n")


# -------------------------
# ЗАДАЧА 3: Процессы
# -------------------------

def calc_factorial(n):
    return math.factorial(n)

def is_prime(n):
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))


def task3():
    tasks = [
        (calc_factorial, 5000),
        (calc_factorial, 4000),
        (is_prime, 10000019),
        (is_prime, 10000033)
    ]

    start = time.time()

    with multiprocessing.Pool(4) as pool:
        results = pool.starmap(lambda f, x: f(x), tasks)

    end = time.time()

    print("ЗАДАЧА 3")
    print("Результаты:", results)
    print("Время:", round(end - start, 2), "сек\n")


# -------------------------
# ЗАДАЧА 4: Async
# -------------------------

async def fetch(session, url, name):
    try:
        async with session.get(url) as resp:
            text = await resp.text()
            print(f"{name} загружен")
            return len(text)
    except:
        return 0


async def task4():
    urls = [
        ("https://httpbin.org/delay/1", "Сайт1"),
        ("https://httpbin.org/delay/2", "Сайт2"),
        ("https://httpbin.org/delay/1", "Сайт3"),
        ("https://httpbin.org/delay/3", "Сайт4"),
    ]

    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, u, n) for u, n in urls]
        results = await asyncio.gather(*tasks)

    end = time.time()

    print("ЗАДАЧА 4")
    print("Размеры:", results)
    print("Время:", round(end - start, 2), "сек\n")


# -------------------------
# ЗАДАЧА 5: Сравнение
# -------------------------

def io_task(name, t):
    time.sleep(t)
    return name


async def async_task(name, t):
    await asyncio.sleep(t)
    return name


def task5():
    tasks = [("t1",2),("t2",3),("t3",1),("t4",2),("t5",1)]

    # sync
    start = time.time()
    for t in tasks:
        io_task(*t)
    sync_time = time.time() - start

    # threads
    start = time.time()
    threads = []
    for t in tasks:
        th = threading.Thread(target=io_task, args=t)
        threads.append(th)
        th.start()
    for th in threads:
        th.join()
    thread_time = time.time() - start

    # multiprocessing
    start = time.time()
    with multiprocessing.Pool(5) as pool:
        pool.starmap(io_task, tasks)
    proc_time = time.time() - start

    # async
    async def run_async():
        return await asyncio.gather(*[async_task(*t) for t in tasks])

    start = time.time()
    asyncio.run(run_async())
    async_time = time.time() - start

    print("ЗАДАЧА 5")
    print("sync:", round(sync_time,2))
    print("threads:", round(thread_time,2))
    print("process:", round(proc_time,2))
    print("async:", round(async_time,2))


# -------------------------
# ЗАПУСК
# -------------------------

if __name__ == "__main__":
    task1()
    task2()
    task3()
    asyncio.run(task4())
    task5()
