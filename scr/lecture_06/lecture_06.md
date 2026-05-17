# Лекция 6. ООП — часть 1: класс и экземпляр

> 📖 Документация: [Classes](https://docs.python.org/3/tutorial/classes.html) · [Data Model — classes](https://docs.python.org/3/reference/datamodel.html#classes) · [Data Model — __new__](https://docs.python.org/3/reference/datamodel.html#object.__new__) · [Data Model — __init__](https://docs.python.org/3/reference/datamodel.html#object.__init__)

---

## Четыре конструкции

Прежде чем писать первый класс, зафиксируем четыре конструкции которые нужно держать в голове всегда:

| Конструкция | Что это |
|---|---|
| __Функция__ | объект типа `function`, вызывается напрямую |
| __Класс__ | объект типа `type`, шаблон для создания экземпляров |
| __Метод__ | функция привязанная к классу, вызывается через экземпляр или класс |
| __Экземпляр__ | конкретный объект созданный из класса |

Всё ООП в Python — это комбинации этих четырёх конструкций.

---

## Класс

!!! quote "docs.python.org / tutorial — classes"
    *Classes provide a means of bundling data and functionality together. Creating a new class creates a new type of object, allowing new instances of that type to be made. Each class instance can have attributes attached to it for maintaining its state. Class instances can also have methods (defined by its class) for modifying its state.*

Класс — это объект типа `type`. Он служит шаблоном для создания экземпляров.

```python
class Point:
    pass

print(type(Point))    # <class 'type'>
print(type(int))      # <class 'type'>  — int тоже класс
print(type(str))      # <class 'type'>
```

Класс сам по себе — объект. У него есть `id()`, `type()`, его можно передать как аргумент, положить в список, присвоить другому имени:

```python
MyPoint = Point        # второе имя для того же объекта-класса
p = MyPoint(1, 2)      # создаём экземпляр через любое из имён
```

---

## Экземпляр

Экземпляр создаётся вызовом класса как функции:

```python
class Point:
    pass

p = Point()            # создать экземпляр
print(type(p))         # <class '__main__.Point'>
print(isinstance(p, Point))   # True
```

Каждый вызов `Point()` создаёт __новый независимый объект__:

```python
p1 = Point()
p2 = Point()

print(p1 is p2)        # False — разные объекты
print(id(p1) == id(p2))  # False
```

---

## __init__ — инициализация

`__init__` — метод который вызывается автоматически после создания экземпляра. Он инициализирует атрибуты объекта.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x)   # 1
print(p.y)   # 2
```

`__init__` не создаёт объект — он только инициализирует уже созданный. Возвращаемое значение должно быть `None` (или ничего).

---

## self — это просто первый аргумент

!!! quote "docs.python.org / tutorial — classes"
    *Often, the first argument of a method is called self. This is nothing more than a convention: the name self has absolutely no special meaning to Python.*

`self` — обычное имя для первого параметра метода. Python автоматически передаёт экземпляр первым аргументом при вызове метода через экземпляр.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self):
        return (self.x**2 + self.y**2) ** 0.5

p = Point(3, 4)
print(p.distance())   # 5.0
```

Вызов `p.distance()` — это синтаксический сахар. Python разворачивает его в:

```python
Point.distance(p)   # явная передача экземпляра первым аргументом
```

Проверим:

```python
print(p.distance())          # 5.0
print(Point.distance(p))     # 5.0 — то же самое
```

!!! quote "docs.python.org / tutorial — classes"
    *When an instance method object is called with an argument list, a new argument list is constructed from the instance object and the argument list, and the function object is called with this new argument list.*

Метод — это функция + привязанный экземпляр. При обращении к методу через экземпляр Python создаёт __связанный метод__ (bound method):

```python
print(type(p.distance))        # <class 'method'>
print(type(Point.distance))    # <class 'function'>

print(p.distance.__self__)     # <__main__.Point object> — привязанный экземпляр
print(p.distance.__func__)     # <function Point.distance> — исходная функция
```

---

## Атрибуты экземпляра vs атрибуты класса

Это одно из самых важных различий в ООП Python.

### Атрибуты экземпляра

Создаются через `self.name = value` — обычно в `__init__`. Принадлежат конкретному экземпляру, хранятся в его `__dict__`:

```python
class Point:
    def __init__(self, x, y):
        self.x = x     # атрибут экземпляра
        self.y = y     # атрибут экземпляра

p1 = Point(1, 2)
p2 = Point(3, 4)

print(p1.__dict__)   # {'x': 1, 'y': 2}
print(p2.__dict__)   # {'x': 3, 'y': 4}

p1.x = 99
print(p1.x)   # 99
print(p2.x)   # 3 — p2 не затронут
```

### Атрибуты класса

Определяются в теле класса вне методов. Принадлежат классу, хранятся в `Class.__dict__`. __Разделяются всеми экземплярами__:

```python
class Circle:
    pi = 3.14159   # атрибут класса

    def __init__(self, radius):
        self.radius = radius   # атрибут экземпляра

    def area(self):
        return Circle.pi * self.radius ** 2

c1 = Circle(5)
c2 = Circle(10)

print(Circle.pi)   # 3.14159
print(c1.pi)       # 3.14159 — доступ через экземпляр тоже работает
print(c2.pi)       # 3.14159
```

### Как Python ищет атрибут

При обращении `obj.name` Python ищет в таком порядке:

1. `obj.__dict__` — атрибуты экземпляра
2. `type(obj).__dict__` — атрибуты класса
3. Атрибуты базовых классов (об этом в лекции 7)

```python
class Counter:
    count = 0   # атрибут класса

    def increment(self):
        self.count += 1   # создаёт атрибут экземпляра!

c1 = Counter()
c2 = Counter()

print(Counter.count)   # 0
c1.increment()
print(c1.count)        # 1 — атрибут экземпляра c1
print(Counter.count)   # 0 — атрибут класса не изменился
print(c2.count)        # 0 — у c2 своего атрибута нет, берёт из класса
```

`self.count += 1` читает `count` из класса (0), прибавляет 1, и __записывает результат как атрибут экземпляра__ — не трогая атрибут класса.

!!! warning "Важно"
    Мутабельные атрибуты класса — классическая ловушка:

    ```python
    class Bad:
        items = []   # разделяется всеми экземплярами!

        def add(self, item):
            self.items.append(item)   # изменяет общий список

    a = Bad()
    b = Bad()
    a.add(1)
    print(b.items)   # [1] — неожиданно!
    ```

    Правильно — инициализировать в `__init__`:

    ```python
    class Good:
        def __init__(self):
            self.items = []   # у каждого экземпляра свой список
    ```

---

## Создание объекта: __new__ и __init__

Когда вы пишете `Point(1, 2)` — происходит два шага:

!!! quote "docs.python.org / datamodel — __new__"
    *`__new__()` is a static method that takes the class of which an instance was requested as its first argument. The return value of `__new__()` should be the new object instance (usually an instance of cls).*
    *If `__new__()` returns an instance of cls, then the new instance's `__init__()` method will be invoked.*

__Шаг 1 — `__new__`__: создаёт объект в памяти, возвращает его. Статический метод, принимает класс (`cls`), а не экземпляр.

__Шаг 2 — `__init__`__: получает уже созданный объект (`self`), инициализирует его атрибуты.

```python
class Point:
    def __new__(cls, x, y):
        print(f"__new__ вызван для {cls}")
        instance = super().__new__(cls)   # создаём объект
        return instance                   # передаём в __init__

    def __init__(self, x, y):
        print(f"__init__ вызван, self={self}")
        self.x = x
        self.y = y

p = Point(1, 2)
# __new__ вызван для <class '__main__.Point'>
# __init__ вызван, self=<__main__.Point object>
```

В большинстве случаев `__new__` переопределять не нужно. Он используется в особых ситуациях — например чтобы контролировать создание объектов неизменяемых типов или реализовывать паттерн Singleton.

---

## Специальные методы — dunder methods

Python использует специальные методы с двойными подчёркиваниями (`__method__`) чтобы перегружать операторы и встроенные функции. Это позволяет вашим объектам вести себя как встроенные типы.

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __len__(self):
        return 2   # двумерный вектор

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


v1 = Vector(1, 2)
v2 = Vector(3, 4)

print(v1)           # (1, 2) — __str__
print(repr(v1))     # Vector(1, 2) — __repr__
print(v1 + v2)      # (4, 6) — __add__
print(v1 * 3)       # (3, 6) — __mul__
print(len(v1))      # 2 — __len__
print(v1 == v2)     # False — __eq__
```

### __repr__ vs __str__

- `__repr__` — однозначное представление для разработчика. Должно позволять воссоздать объект. Вызывается в REPL, при `repr()`, внутри контейнеров.
- `__str__` — читаемое представление для пользователя. Вызывается при `print()`, `str()`.

Если `__str__` не определён — Python использует `__repr__`. Если не определён ни один — используется дефолтное `<__main__.ClassName object at 0x...>`.

```python
v = Vector(1, 2)
print(str(v))    # (1, 2) — __str__
print(repr(v))   # Vector(1, 2) — __repr__
print([v])       # [Vector(1, 2)] — внутри списка используется __repr__
```

---

## staticmethod и classmethod

Помимо обычных методов экземпляра Python поддерживает два других вида методов.

### @staticmethod

Обычная функция внутри класса — не получает ни `self` ни `cls`. Используется когда логика относится к классу, но не требует доступа к экземпляру или классу:

```python
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def is_even(n):
        return n % 2 == 0

print(MathUtils.add(1, 2))      # 3
print(MathUtils.is_even(4))     # True
```

### @classmethod

Получает класс как первый аргумент (`cls`). Типичное применение — альтернативные конструкторы:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def from_tuple(cls, coords):
        return cls(coords[0], coords[1])

    @classmethod
    def origin(cls):
        return cls(0, 0)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p1 = Point(1, 2)
p2 = Point.from_tuple((3, 4))
p3 = Point.origin()

print(p1, p2, p3)   # Point(1, 2) Point(3, 4) Point(0, 0)
```

`cls` — это сам класс. При наследовании `cls` будет подклассом, а не базовым — это важное отличие от жёсткого использования имени класса.

---

## Читаем реальный код — Toga WindowSet

Откроем [toga/src/toga/app.py](https://github.com/beeware/toga/blob/main/core/src/toga/app.py) — класс `WindowSet`:

```python
class WindowSet:
    def __init__(self, app):
        self.app = app
        self._windows = {}    # атрибут экземпляра — свой для каждого приложения

    def add(self, window):
        if not isinstance(window, Window):
            raise TypeError("...") 
        self._windows[id(window)] = window   # id объекта как ключ словаря
        window.app = self.app

    def __iter__(self):
        return iter(self._windows.values())  # WindowSet итерируемый

    def __len__(self):
        return len(self._windows)

    def __contains__(self, window):
        return id(window) in self._windows
```

Что здесь видно:

- `self._windows` — атрибут экземпляра, у каждого приложения своё хранилище окон
- `id(window)` как ключ словаря — вместо самого объекта Window (который не хешируем если изменяемый)
- `__iter__`, `__len__`, `__contains__` — WindowSet ведёт себя как коллекция благодаря специальным методам
- `isinstance` — явная проверка типа на входе

---

## Домашнее задание

Создайте файл `hw06.py`. Сдача через PR, ветка: `hw06/фамилия`.

__1.__ Напишите класс `Stack` (стек — LIFO). Реализуйте методы `push(item)`, `pop()`, `peek()` (посмотреть верхний элемент без удаления), `is_empty()`. Добавьте `__len__`, `__repr__`, `__bool__` (пустой стек — False). `pop()` из пустого стека должен поднимать `IndexError`.

__2.__ Напишите класс `Temperature` с атрибутом `celsius`. Добавьте `@classmethod` конструкторы `from_fahrenheit(cls, f)` и `from_kelvin(cls, k)`. Реализуйте `__repr__` и `__eq__`. Проверьте что `Temperature.from_fahrenheit(212) == Temperature(100)`.

__3.__ Воспроизведите ловушку с мутабельным атрибутом класса: создайте класс где `items = []` — атрибут класса, покажите через два экземпляра что список общий. Затем исправьте через `__init__` и покажите что теперь списки независимые. Добавьте комментарии.
