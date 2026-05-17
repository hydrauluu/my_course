# Лекция 11. Управление памятью и жизненный цикл объекта

> 📖 Документация: [gc — Garbage Collector interface](https://docs.python.org/3/library/gc.html) · [weakref — Weak references](https://docs.python.org/3/library/weakref.html) · [sys.getrefcount](https://docs.python.org/3/library/sys.html#sys.getrefcount) · [Data Model — __del__](https://docs.python.org/3/reference/datamodel.html#object.__del__) · [Data Model — __new__](https://docs.python.org/3/reference/datamodel.html#object.__new__)

---

## Жизненный цикл объекта

В лекции 6 мы разобрали что создание объекта — это два шага: `__new__` создаёт объект в памяти, `__init__` его инициализирует. Теперь посмотрим на полный жизненный цикл — от создания до уничтожения.

```
__new__()  →  __init__()  →  [объект живёт]  →  __del__()  →  освобождение памяти
```

Вопрос: когда именно вызывается `__del__` и гарантировано ли что он вызовется вообще?

---

## Подсчёт ссылок

CPython использует __подсчёт ссылок__ как основной механизм управления памятью. У каждого объекта есть счётчик — сколько имён и контейнеров на него ссылаются. Когда счётчик падает до нуля — объект немедленно удаляется.

```python
import sys

a = []          # создали список, refcount = 1
b = a           # второе имя, refcount = 2
c = [a]         # список внутри списка, refcount = 3

print(sys.getrefcount(a))   # 4 — getrefcount сам добавляет временную ссылку

del c           # refcount = 3
del b           # refcount = 2
del a           # refcount = 1 — объект ещё жив, на него смотрит getrefcount
                # после выхода из выражения → refcount = 0 → удалён
```

!!! warning "sys.getrefcount всегда показывает на 1 больше"
    При передаче объекта в `getrefcount` создаётся временная ссылка — аргумент функции. Поэтому результат всегда на единицу больше реального счётчика.

### Когда увеличивается refcount

- Присваивание: `b = a`
- Передача в функцию: `func(a)`
- Добавление в контейнер: `lst.append(a)`
- Добавление в замыкание

### Когда уменьшается refcount

- `del a` — удаление имени
- Переприсваивание: `a = something_else`
- Выход из области видимости функции
- Удаление из контейнера: `lst.remove(a)`

---

## Циклические ссылки — ахиллесова пята подсчёта ссылок

Подсчёт ссылок не справляется с циклическими ссылками. Если объекты ссылаются друг на друга — их счётчики никогда не упадут до нуля, даже если они недостижимы из программы.

```python
import gc

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

    def __del__(self):
        print(f"Node({self.value}) удалён")

# создаём цикл
a = Node(1)
b = Node(2)
a.next = b   # a → b
b.next = a   # b → a (цикл!)

del a
del b
# Node(1) и Node(2) НЕ удалились — refcount у обоих не нуль
# они ссылаются друг на друга
print("после del a, del b")

gc.collect()   # явный запуск сборщика мусора
# Node(1) удалён
# Node(2) удалён
print("после gc.collect()")
```

Циклы возникают не только в связных списках — они случаются и при более неочевидных ситуациях:

```python
# объект ссылается на себя через атрибут
class Self:
    pass

s = Self()
s.me = s     # цикл: s → s.me → s

# замыкание ссылается на функцию
def make_cycle():
    def inner():
        return outer   # inner ссылается на outer
    outer = inner
    return outer       # outer ссылается на inner через замыкание
```

---

## Сборщик мусора (gc)

!!! quote "docs.python.org / gc module"
    *Since the collector supplements the reference counting already used in Python, you can disable the collector if you are sure your program does not create reference cycles.*

Python использует __генерационный сборщик мусора__ для обнаружения циклических ссылок. Объекты делятся на три поколения (0, 1, 2) в зависимости от возраста:

- __Поколение 0__ — только что созданные объекты. Проверяется чаще всего
- __Поколение 1__ — пережили одну проверку поколения 0
- __Поколение 2__ — старые долгоживущие объекты. Проверяется редко

Идея: большинство объектов живут недолго. Часто проверять долгоживущие объекты неэффективно.

```python
import gc

print(gc.get_threshold())   # (700, 10, 10) — пороги для каждого поколения
print(gc.get_count())       # текущее количество объектов в каждом поколении

# ручной запуск
gc.collect()      # проверить все поколения
gc.collect(0)     # только поколение 0

# статистика
gc.set_debug(gc.DEBUG_STATS)   # вывод статистики при каждом запуске
```

### gc в практике

В большинстве программ gc работает автоматически и не требует вмешательства. Ручное управление нужно в особых случаях:

```python
# отключить gc в критичном по производительности месте
gc.disable()
# ... операция создающая много временных объектов
gc.enable()
gc.collect()   # явно собрать после

# найти утечку — что ссылается на объект
import gc
suspects = gc.get_referrers(some_object)
```

---

## __del__ — финализатор

`__del__` вызывается __перед__ уничтожением объекта. Но не сразу когда вы ожидаете:

```python
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"{name}: создан")

    def __del__(self):
        print(f"{self.name}: уничтожен")


r = Resource("A")   # A: создан
del r               # A: уничтожен — немедленно (нет цикла, refcount = 0)
```

```python
# но при цикле — неопределённый момент
a = Resource("A")
b = Resource("B")
a.ref = b
b.ref = a
del a
del b
# ничего не выведется — gc ещё не запустился
```

!!! danger "Не используйте __del__ для освобождения ресурсов"
    `__del__` не гарантирует момент вызова, не гарантирует вызов вообще (например при завершении интерпретатора), и создаёт проблемы с циклическими ссылками. Для освобождения ресурсов используйте контекстный менеджер (`with`) или `weakref.finalize`.

### Контекстный менеджер — правильный способ

```python
class DatabaseConnection:
    def __init__(self, url):
        self.url = url
        self.connection = self._connect()

    def _connect(self):
        print(f"Подключение к {self.url}")
        return object()   # имитация соединения

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()
        return False   # не подавляем исключение

    def _close(self):
        print(f"Закрытие соединения с {self.url}")


with DatabaseConnection("postgresql://localhost/db") as conn:
    # работаем с conn
    pass
# соединение закрыто гарантированно — даже если было исключение
```

`__exit__` вызывается __всегда__ при выходе из блока `with` — и при нормальном завершении, и при исключении.

---

## Слабые ссылки (weakref)

Слабая ссылка — ссылка которая __не увеличивает__ счётчик ссылок. Объект может быть удалён несмотря на наличие слабых ссылок на него.

```python
import weakref

class Cache:
    pass

obj = Cache()
weak = weakref.ref(obj)   # слабая ссылка

print(weak())    # <Cache object> — объект жив
print(id(weak()) == id(obj))   # True

del obj          # refcount → 0 → объект удалён
print(weak())    # None — объект исчез, слабая ссылка вернула None
```

`weak()` — вызов слабой ссылки как функции возвращает объект или `None` если он уже удалён.

### Зачем нужны слабые ссылки

__Кеш без утечек памяти:__

```python
import weakref

class ExpensiveObject:
    def __init__(self, key):
        self.key = key
        self.data = [0] * 1_000_000   # много памяти

# обычный словарь держит объекты живыми вечно
cache: dict = {}

# WeakValueDictionary — объект удаляется когда нет других ссылок
cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

def get_object(key):
    obj = cache.get(key)
    if obj is None:
        obj = ExpensiveObject(key)
        cache[key] = obj
    return obj

a = get_object("x")   # создаётся и кешируется
b = get_object("x")   # возвращается из кеша
print(a is b)         # True

del a, b              # нет других ссылок — объект удалён из памяти
print(cache.get("x")) # None — кеш сам очистился
```

__Избегание циклических ссылок:__

```python
import weakref

class Parent:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class Child:
    def __init__(self, parent):
        # сильная ссылка создала бы цикл: parent → children → child → parent
        self.parent = weakref.ref(parent)   # слабая — цикла нет

    def get_parent(self):
        p = self.parent()
        if p is None:
            raise RuntimeError("Родитель был удалён")
        return p
```

### weakref.finalize

`weakref.finalize` — надёжный способ запустить код при удалении объекта:

```python
import weakref

class Connection:
    def __init__(self, host):
        self.host = host
        # регистрируем финализатор — он вызовется при удалении объекта
        self._finalizer = weakref.finalize(
            self, self._cleanup, host
        )

    @staticmethod
    def _cleanup(host):
        print(f"Закрываем соединение с {host}")


conn = Connection("localhost")
del conn
# Закрываем соединение с localhost
```

`weakref.finalize` надёжнее `__del__`: он гарантированно вызывается при завершении интерпретатора и корректно работает с циклическими ссылками.

---

## sys.getsizeof и профилирование памяти

```python
import sys

print(sys.getsizeof(42))          # 28 байт — int
print(sys.getsizeof("hello"))     # 54 байт — str
print(sys.getsizeof([]))          # 56 байт — пустой list
print(sys.getsizeof([1, 2, 3]))   # 88 байт — list с тремя элементами
```

!!! warning "sys.getsizeof не учитывает вложенные объекты"
    `sys.getsizeof([1, 2, 3])` возвращает размер самого списка — без размеров объектов внутри него. Для рекурсивного подсчёта нужен отдельный обход.

```python
def deep_sizeof(obj, seen=None):
    """Рекурсивный подсчёт размера объекта и всего что он содержит."""
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0   # уже считали — избегаем цикла

    seen.add(obj_id)
    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(deep_sizeof(k, seen) + deep_sizeof(v, seen)
                    for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_sizeof(item, seen) for item in obj)

    return size
```

---

## Читаем реальный код — WeakrefCallable из Toga

Откроем [toga/src/toga/app.py](https://github.com/beeware/toga/blob/main/core/src/toga/app.py) — класс `WeakrefCallable`:

```python
class WeakrefCallable:
    """Обёртка над callable которая хранит слабую ссылку на него.

    Используется чтобы обработчики событий не удерживали объекты живыми.
    """

    def __init__(self, callable):
        try:
            # для методов — слабая ссылка на экземпляр и имя метода отдельно
            self._ref = weakref.ref(callable.__self__)
            self._func_name = callable.__func__.__name__
        except AttributeError:
            # для обычных функций — слабая ссылка напрямую
            self._ref = weakref.ref(callable)
            self._func_name = None

    def __call__(self, *args, **kwargs):
        obj = self._ref()   # получаем объект по слабой ссылке
        if obj is None:
            return           # объект удалён — молча игнорируем

        if self._func_name:
            return getattr(obj, self._func_name)(*args, **kwargs)
        return obj(*args, **kwargs)
```

Зачем это нужно: если виджет подписывается на событие и передаёт метод как обработчик — сильная ссылка удержит виджет живым даже после того как он должен был удалиться. `WeakrefCallable` решает эту проблему: если виджет удалён — обработчик просто ничего не делает.

Обратите внимание на разницу между методом и функцией: для метода нужно хранить слабую ссылку на __экземпляр__ (`__self__`) и отдельно __имя метода__ (`__func__.__name__`) — потому что слабая ссылка на сам bound method не работает (bound method создаётся каждый раз заново и не имеет референтов).

---

## Домашнее задание

Создайте файл `hw11.py`. Сдача через PR, ветка: `hw11/фамилия`.

__1.__ Напишите класс `TrackedObject` который при создании регистрирует себя в классовом списке через слабую ссылку (`WeakValueDictionary` или `WeakSet`). Продемонстрируйте что после `del obj` объект исчезает из реестра автоматически — без явного удаления из реестра.

__2.__ Создайте два взаимно ссылающихся объекта (цикл). Через `gc.collect()` и `gc.get_count()` покажите что они не удаляются подсчётом ссылок и требуют сборщика мусора. Добавьте `__del__` и покажите момент вызова.

__3.__ Напишите простой LRU-кеш через `WeakValueDictionary` — функцию `cached(func)` которая кеширует результаты вызовов. При удалении результата из памяти — кеш очищается автоматически. Сравните поведение с обычным словарём-кешем.
