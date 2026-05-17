# Лекция 12. Асинхронность

> 📖 Документация: [asyncio — Asynchronous I/O](https://docs.python.org/3/library/asyncio.html) · [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html) · [A Conceptual Overview of asyncio](https://docs.python.org/3/howto/a-conceptual-overview-of-asyncio.html) · [PEP 492 — Coroutines with async and await syntax](https://peps.python.org/pep-0492/)

---

## Не параллельность, а кооперативность

Прежде чем писать первый `async def` — нужно понять главное заблуждение.

**asyncio не параллелен.** Всё работает в одном потоке, в одном процессе. Никакого параллельного выполнения нет.

!!! quote "docs.python.org / asyncio — Conceptual Overview"
    *An event loop runs in a thread (typically the main thread) and executes all callbacks and Tasks in its thread. While a Task is running in the event loop, no other Tasks can run in the same thread. When a Task executes an await expression, the running Task gets suspended, and the event loop executes the next Task.*

Идея в другом: когда одна задача **ждёт** (сеть, диск, таймер) — она добровольно отдаёт управление, и в это время выполняется другая задача. Это называется **кооперативная многозадачность**.

Аналогия: один повар может готовить несколько блюд одновременно — пока одно варится, он режет другое. Не потому что у него несколько рук, а потому что он использует время ожидания.

### Когда asyncio нужен, а когда нет

| Задача | Подходит ли asyncio |
|---|---|
| Много сетевых запросов | ✅ — ждём ответ, отдаём управление |
| Работа с базой данных | ✅ — если драйвер async |
| Файловый I/O (много файлов) | ✅ — ждём диск |
| Тяжёлые вычисления (CPU) | ❌ — нет ожидания, один поток не поможет |
| Простой скрипт | ❌ — усложнит без выгоды |

---

## Корутина — возобновляемая функция

!!! quote "PEP 492 — Coroutines with async and await syntax"
    *It is proposed to make coroutines a proper standalone concept in Python, and introduce new supporting syntax. The ultimate goal is to help establish a common, easily approachable, mental model of asynchronous programming in Python and make it as close to synchronous programming as possible.*

Корутина объявляется через `async def`. Вызов корутинной функции **не выполняет её** — возвращает объект-корутину:

```python
import asyncio

async def greet(name: str) -> str:
    return f"Hello, {name}"

result = greet("Alice")   # ничего не выполнилось
print(type(result))       # <class 'coroutine'>
print(result)             # <coroutine object greet at 0x...>
                          # RuntimeWarning: coroutine was never awaited
```

Корутину нужно либо `await`-ить, либо запустить через `asyncio.run()`:

```python
async def main():
    result = await greet("Alice")   # выполнить и получить результат
    print(result)                    # Hello, Alice

asyncio.run(main())
```

### Связь с генераторами

Корутины внутри — особый вид генераторов. `await` это по сути `yield from` для корутин. Каждый `await` — точка где корутина может приостановиться и отдать управление event loop.

```python
# грубо упрощённо — как работает await изнутри
# (реальная реализация сложнее)
async def sleep_and_greet(delay, name):
    await asyncio.sleep(delay)   # приостановиться на delay секунд
    return f"Hello, {name}"
```

Когда интерпретатор доходит до `await asyncio.sleep(delay)` — корутина приостанавливается, event loop получает управление и может запустить другие задачи. Через `delay` секунд — корутина возобновляется.

---

## Event Loop

!!! quote "docs.python.org / asyncio — Conceptual Overview"
    *Everything in asyncio happens relative to the event loop. It's the star of the show. It's like an orchestra conductor.*

Event loop — это цикл который:

1. Берёт задачу из очереди
2. Выполняет её до ближайшего `await`
3. Если задача ждёт — откладывает её, берёт следующую
4. Когда ожидание закончилось — возвращает задачу в очередь
5. Повторяет

```python
import asyncio
import time

async def say_after(delay: float, message: str) -> None:
    await asyncio.sleep(delay)
    print(message)

async def main() -> None:
    print(f"Старт: {time.strftime('%X')}")

    await say_after(1, "раз")    # ждём 1 секунду, потом "раз"
    await say_after(2, "два")    # ждём ещё 2 секунды, потом "два"

    print(f"Конец: {time.strftime('%X')}")

asyncio.run(main())
# Старт: 12:00:00
# раз
# два
# Конец: 12:00:03  — суммарно 3 секунды
```

Здесь корутины выполняются **последовательно** — одна за другой. Чтобы выполнить их **конкурентно** — нужны задачи.

---

## Awaitables — что можно await-ить

!!! quote "docs.python.org / Coroutines and Tasks"
    *We say that an object is an awaitable object if it can be used in an await expression. Many asyncio APIs are designed to accept awaitables. There are three main types of awaitable objects: coroutines, Tasks, and Futures.*

**Корутина** — объект созданный вызовом `async def` функции.

**Task** — корутина обёрнутая в Task и запланированная для выполнения. Создаётся через `asyncio.create_task()`.

**Future** — низкоуровневый объект представляющий результат который появится в будущем. В пользовательском коде редко создаётся напрямую.

Объект является awaitable если реализует метод `__await__`:

```python
class MyAwaitable:
    def __await__(self):
        yield   # приостановиться и отдать управление event loop
        return "результат"
```

---

## Task — конкурентное выполнение

`asyncio.create_task()` — запланировать корутину для выполнения **немедленно**, не дожидаясь `await`:

```python
import asyncio
import time

async def say_after(delay: float, message: str) -> None:
    await asyncio.sleep(delay)
    print(message)

async def main() -> None:
    print(f"Старт: {time.strftime('%X')}")

    # создаём задачи — обе запускаются сразу
    task1 = asyncio.create_task(say_after(1, "раз"))
    task2 = asyncio.create_task(say_after(2, "два"))

    # ждём завершения обеих
    await task1
    await task2

    print(f"Конец: {time.strftime('%X')}")

asyncio.run(main())
# Старт: 12:00:00
# раз
# два
# Конец: 12:00:02  — суммарно 2 секунды, а не 3!
```

Пока `task1` спит — `task2` тоже работает. Оба ожидания идут параллельно во времени.

!!! warning "Сохраняйте ссылку на Task"
    Если Task не сохранён — сборщик мусора может удалить его до завершения:

    ```python
    # плохо
    asyncio.create_task(some_coro())   # ссылка не сохранена!

    # хорошо
    task = asyncio.create_task(some_coro())
    await task
    ```

### asyncio.gather — запустить несколько конкурентно

```python
async def fetch(url: str) -> str:
    await asyncio.sleep(1)   # имитация сетевого запроса
    return f"данные от {url}"

async def main() -> None:
    # запустить все конкурентно и дождаться всех
    results = await asyncio.gather(
        fetch("https://api.example.com/users"),
        fetch("https://api.example.com/posts"),
        fetch("https://api.example.com/comments"),
    )
    print(results)   # ['данные от ...', 'данные от ...', 'данные от ...']
    # суммарно ~1 секунда вместо ~3

asyncio.run(main())
```

### asyncio.TaskGroup — более безопасная альтернатива (Python 3.11+)

!!! quote "docs.python.org / Coroutines and Tasks"
    *TaskGroup provides stronger safety guarantees than gather for scheduling a nesting of subtasks: if a task (or a subtask, a task scheduled by a task) raises an exception, TaskGroup will, while gather will not, cancel the remaining scheduled tasks.*

```python
async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch("https://api.example.com/users"))
        task2 = tg.create_task(fetch("https://api.example.com/posts"))
    # здесь обе задачи завершены
    print(task1.result(), task2.result())
```

Если одна задача упала — остальные отменяются автоматически.

---

## async with и async for

### Асинхронный контекстный менеджер

`async with` — контекстный менеджер который может `await`-ить при входе и выходе. Реализуется через `__aenter__` и `__aexit__`:

```python
class AsyncConnection:
    async def __aenter__(self):
        await asyncio.sleep(0.1)   # имитация подключения
        print("Подключено")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.1)   # имитация закрытия
        print("Отключено")
        return False

async def main():
    async with AsyncConnection() as conn:
        print("Работаем...")

asyncio.run(main())
# Подключено
# Работаем...
# Отключено
```

Типичное использование — асинхронные сессии и соединения:

```python
import aiohttp   # сторонняя библиотека для async HTTP

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Асинхронный итератор

`async for` — итерация по объектам которые производят значения асинхронно. Реализуется через `__aiter__` и `__anext__`:

```python
class AsyncRange:
    def __init__(self, stop: int):
        self.current = 0
        self.stop = stop

    def __aiter__(self):
        return self

    async def __anext__(self) -> int:
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0)   # уступить управление
        value = self.current
        self.current += 1
        return value

async def main():
    async for i in AsyncRange(5):
        print(i)

asyncio.run(main())   # 0, 1, 2, 3, 4
```

Асинхронные генераторы — через `async def` с `yield`:

```python
async def async_range(stop: int):
    for i in range(stop):
        await asyncio.sleep(0)
        yield i

async def main():
    async for i in async_range(5):
        print(i)
```

---

## Типичные ошибки

### Забыли await

```python
async def main():
    result = fetch("https://example.com")   # забыли await!
    print(result)   # <coroutine object fetch at 0x...>
    # RuntimeWarning: coroutine 'fetch' was never awaited
```

### Блокирующий вызов внутри корутины

```python
import time

async def bad():
    time.sleep(1)   # блокирует весь event loop — никто не работает 1 секунду

async def good():
    await asyncio.sleep(1)   # отдаёт управление — другие задачи работают
```

Блокирующие операции (синхронный I/O, тяжёлые вычисления) внутри корутины замораживают весь event loop. Для CPU-bound задач используйте `asyncio.run_in_executor()`:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def heavy_computation(n: int) -> int:
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, heavy_computation, 1_000_000)
    print(result)
```

### Создание event loop внутри уже работающего

```python
# плохо — если уже есть event loop
asyncio.run(coro())   # RuntimeError в Jupyter notebook

# в Jupyter используйте await напрямую
result = await coro()
```

---

## Читаем реальный код — Django async views

Django поддерживает async views начиная с версии 3.1. Откроем как это выглядит в реальном проекте:

```python
# views.py
import asyncio
import aiohttp
from django.http import JsonResponse

async def fetch_weather(request, city: str) -> JsonResponse:
    """Асинхронный view — не блокирует сервер пока ждём внешний API."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.weather.com/v1/{city}"
        ) as response:
            data = await response.json()

    return JsonResponse({"city": city, "temp": data["temp"]})


async def dashboard(request) -> JsonResponse:
    """Несколько запросов конкурентно."""
    cities = ["Moscow", "London", "Tokyo"]

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_city_data(session, city)
            for city in cities
        ]
        results = await asyncio.gather(*tasks)

    return JsonResponse({"data": results})
```

Обычный синхронный view держит поток занятым пока ждёт ответ от внешнего API. Async view отдаёт поток обратно серверу — тот может обрабатывать другие запросы пока идёт ожидание.

Django также поддерживает async ORM начиная с версии 4.1:

```python
async def get_books(request) -> JsonResponse:
    # async версии стандартных методов
    books = await Book.objects.filter(author="Tolstoy").aall()
    count = await Book.objects.acount()

    # async итерация
    titles = []
    async for book in Book.objects.filter(pages__gte=300):
        titles.append(book.title)

    return JsonResponse({"titles": titles, "count": count})
```

---

## Домашнее задание

Создайте файл `hw12.py`. Сдача через PR, ветка: `hw12/фамилия`.

**1.** Напишите корутину `fetch_all(urls: list[str]) -> list[str]` которая имитирует загрузку каждого URL через `asyncio.sleep(random.uniform(0.1, 1.0))` и возвращает список результатов. Запустите все конкурентно через `asyncio.gather`. Замерьте время через `time.time()` и сравните с последовательным выполнением.

**2.** Напишите асинхронный генератор `async_fibonacci()` который бесконечно генерирует числа Фибоначчи с задержкой `asyncio.sleep(0)` между каждым. Используйте `async for` с `break` чтобы взять первые 10 чисел.

**3.** Напишите асинхронный контекстный менеджер `AsyncTimer` который при входе запоминает время, при выходе выводит сколько секунд прошло. Используйте как `async with AsyncTimer() as t:`. Внутри блока запустите несколько конкурентных задач через `TaskGroup`.
