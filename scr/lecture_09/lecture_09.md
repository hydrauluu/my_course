# Лекция 9. Метаклассы и сопоставление шаблону

> 📖 Документация: [Data Model — Metaclasses](https://docs.python.org/3/reference/datamodel.html#metaclasses) · [type()](https://docs.python.org/3/library/functions.html#type) · [PEP 634 — Structural Pattern Matching](https://peps.python.org/pep-0634/) · [PEP 636 — Pattern Matching Tutorial](https://peps.python.org/pep-0636/) · [PEP 487 — __init_subclass__](https://peps.python.org/pep-0487/)

---

## Класс — это объект. Что его создаёт?

В лекции 0 мы установили что всё в Python — объект. В лекции 6 выяснили что классы — объекты типа `type`:

```python
print(type(int))    # <class 'type'>
print(type(str))    # <class 'type'>
print(type(list))   # <class 'type'>

class MyClass:
    pass

print(type(MyClass))   # <class 'type'>
```

`type` — это класс который создаёт классы. Он является собственным экземпляром:

```python
print(type(type))   # <class 'type'>
```

__Метакласс__ — это класс чьи экземпляры являются классами. По умолчанию метакласс любого класса — `type`.

---

## type() в двух режимах

`type()` работает в двух режимах в зависимости от количества аргументов.

__Один аргумент__ — возвращает тип объекта:

```python
type(42)        # <class 'int'>
type("hello")   # <class 'str'>
```

__Три аргумента__ — создаёт новый класс:

```python
type(name, bases, namespace)
```

- `name` — имя класса (строка)
- `bases` — кортеж базовых классов
- `namespace` — словарь атрибутов и методов

```python
# эти два определения класса эквивалентны:

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


Point = type(
    "Point",
    (),    # нет базовых классов, кроме object
    {
        "__init__": lambda self, x, y: setattr(self, "x", x) or setattr(self, "y", y),
        "__repr__": lambda self: f"Point({self.x}, {self.y})",
    }
)
```

Когда Python встречает `class Point:` — он буквально вызывает `type("Point", bases, namespace)`.

---

## Как создаётся класс — полный процесс

!!! quote "docs.python.org / datamodel — Metaclasses"
    *The appropriate metaclass is determined by the following precedence rules: if the `metaclass` keyword argument is passed with the class definition, the class is created using that metaclass; otherwise, if there is at least one base class, the metaclass is determined from the base class; otherwise, the default metaclass `type` is used.*

При выполнении `class Foo(Base, metaclass=Meta):` Python делает следующее:

1. Определяет метакласс — `Meta` если указан явно, иначе берёт из базового класса
2. Подготавливает пространство имён — вызывает `Meta.__prepare__(name, bases)`
3. Выполняет тело класса в этом пространстве имён — заполняет `namespace`
4. Создаёт класс — вызывает `Meta(name, bases, namespace)`

Шаг 4 — это вызов метакласса. `type.__new__` создаёт объект-класс, `type.__init__` инициализирует его.

---

## Собственный метакласс

Метакласс — это класс который наследует от `type` и переопределяет `__new__` или `__init__`:

```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"Создаётся класс {name!r}")
        print(f"  Базовые классы: {bases}")
        print(f"  Атрибуты: {list(namespace.keys())}")

        cls = super().__new__(mcs, name, bases, namespace)
        return cls


class MyClass(metaclass=Meta):
    x = 10

    def greet(self):
        return "hello"

# при определении класса выведет:
# Создаётся класс 'MyClass'
#   Базовые классы: ()
#   Атрибуты: ['__module__', '__qualname__', 'x', 'greet']
```

### Что можно делать в метаклассе

__Автоматически добавлять методы:__

```python
class AutoReprMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        # добавляем __repr__ если не определён
        if "__repr__" not in namespace:
            def __repr__(self):
                attrs = ", ".join(
                    f"{k}={v!r}"
                    for k, v in self.__dict__.items()
                    if not k.startswith("_")
                )
                return f"{type(self).__name__}({attrs})"
            cls.__repr__ = __repr__

        return cls


class Point(metaclass=AutoReprMeta):
    def __init__(self, x, y):
        self.x = x
        self.y = y


p = Point(1, 2)
print(p)   # Point(x=1, y=2) — __repr__ добавлен метаклассом
```

__Валидировать определение класса:__

```python
class RequireDocstringMeta(type):
    def __new__(mcs, name, bases, namespace):
        if not namespace.get("__doc__"):
            raise TypeError(f"Класс {name!r} должен иметь docstring")
        return super().__new__(mcs, name, bases, namespace)


class Good(metaclass=RequireDocstringMeta):
    """Этот класс хорошо задокументирован."""
    pass


class Bad(metaclass=RequireDocstringMeta):
    pass
# TypeError: Класс 'Bad' должен иметь docstring
```

__Регистрировать подклассы:__

```python
class PluginMeta(type):
    registry = {}

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        if bases:   # не регистрируем базовый класс
            mcs.registry[name] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    pass

class AudioPlugin(Plugin):
    pass

class VideoPlugin(Plugin):
    pass

print(PluginMeta.registry)
# {'AudioPlugin': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}
```

---

## __init_subclass__ — более простая альтернатива

!!! quote "PEP 487 — Simpler customisation of class creation"
    *Currently, customising class creation requires the use of a custom metaclass. This custom metaclass then persists for the entire lifecycle of the class, creating the potential for spurious metaclass conflicts. This PEP proposes to instead support a wide range of customisation scenarios through a new `__init_subclass__` hook.*

Для большинства задач метакласс избыточен. `__init_subclass__` — хук который вызывается при создании подкласса:

```python
class Plugin:
    _registry = {}

    def __init_subclass__(cls, plugin_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        name = plugin_name or cls.__name__
        Plugin._registry[name] = cls
        print(f"Зарегистрирован плагин: {name!r}")


class AudioPlugin(Plugin, plugin_name="audio"):
    pass

class VideoPlugin(Plugin):
    pass

print(Plugin._registry)
# {'audio': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}
```

`__init_subclass__` проще метакласса и не создаёт конфликтов при множественном наследовании.

---

## Читаем реальный код — Django ORM ModelBase

Django ORM использует метакласс `ModelBase` для создания моделей. Откроем [django/db/models/base.py](https://github.com/django/django/blob/main/django/db/models/base.py):

```python
class ModelBase(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        # пропускаем сам Model и его прямых предков
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # создаём класс
        new_class = super_new(cls, name, bases, {"__module__": attrs["__module__"]})

        # читаем атрибуты и строим поля модели
        for attr_name, attr_value in attrs.items():
            new_class.add_to_class(attr_name, attr_value)

        # добавляем вложенный класс DoesNotExist
        new_class.add_to_class(
            "DoesNotExist",
            subclass_exception("DoesNotExist", ObjectDoesNotExist, ...)
        )

        return new_class


class Model(metaclass=ModelBase):
    pass
```

Когда вы пишете:

```python
class Book(Model):
    title = CharField(max_length=200)
    author = CharField(max_length=100)
```

`ModelBase.__new__` читает `title` и `author`, видит что это `Field` объекты, регистрирует их как поля модели, добавляет `Book.DoesNotExist` и строит всю инфраструктуру ORM. Ни одной строки явного кода от вас — метакласс делает всё при определении класса.

---

## Сопоставление шаблону (match/case)

!!! quote "PEP 636 — Structural Pattern Matching: Tutorial"
    *Pattern matching provides a concise way to both recognize data structures and bind variables. For those coming from other languages, this is similar to a switch statement, but much more powerful.*

`match/case` — введён в Python 3.10. Это не просто замена `if/elif` — это __структурное__ сопоставление, которое разбирает форму данных.

### Базовый синтаксис

```python
match command:
    case "quit":
        quit_game()
    case "go north" | "go south":
        move()
    case _:
        print("Неизвестная команда")
```

`_` — wildcard, совпадает с чем угодно и ничего не связывает.

### Виды паттернов

__Литеральный паттерн__ — сравнение по значению:

```python
match status_code:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case 500:
        print("Server Error")
    case _:
        print(f"Неизвестный код: {status_code}")
```

__Паттерн захвата__ — связывает значение с именем:

```python
match point:
    case (0, 0):
        print("Начало координат")
    case (x, 0):
        print(f"На оси X: {x}")
    case (0, y):
        print(f"На оси Y: {y}")
    case (x, y):
        print(f"Точка ({x}, {y})")
```

__Паттерн последовательности:__

```python
match command.split():
    case ["quit"]:
        quit()
    case ["go", direction]:
        go(direction)
    case ["get", item, *rest]:
        get(item, rest)
    case _:
        print("Неизвестная команда")
```

`*rest` — захватывает остаток последовательности.

__Паттерн словаря:__

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        handle_click(x, y)
    case {"type": "keypress", "key": key}:
        handle_key(key)
    case {"type": type_name, **rest}:
        print(f"Неизвестное событие {type_name!r}: {rest}")
```

Словарный паттерн совпадает если словарь __содержит__ указанные ключи — наличие других ключей не мешает. `**rest` захватывает оставшиеся пары.

__Паттерн класса:__

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Circle:
    center: Point
    radius: float

@dataclass
class Rectangle:
    top_left: Point
    bottom_right: Point


def describe_shape(shape):
    match shape:
        case Circle(center=Point(x=0, y=0), radius=r):
            print(f"Окружность из начала координат, радиус {r}")
        case Circle(center=Point(x=cx, y=cy), radius=r):
            print(f"Окружность с центром ({cx}, {cy}), радиус {r}")
        case Rectangle(top_left=Point(x=x1, y=y1), bottom_right=Point(x=x2, y=y2)):
            print(f"Прямоугольник ({x1},{y1}) → ({x2},{y2})")
        case _:
            print("Неизвестная фигура")
```

__OR паттерн__ — несколько вариантов через `|`:

```python
match status:
    case "active" | "enabled" | "running":
        print("Работает")
    case "inactive" | "disabled" | "stopped":
        print("Остановлен")
```

__AS паттерн__ — совпасть и захватить:

```python
match point:
    case Point(x=0, y=0) as origin:
        print(f"Начало координат: {origin}")
    case Point() as p:
        print(f"Точка: {p}")
```

__Гард (guard)__ — дополнительное условие через `if`:

```python
match point:
    case Point(x=x, y=y) if x == y:
        print(f"На диагонали: {x}")
    case Point(x=x, y=y):
        print(f"Обычная точка: ({x}, {y})")
```

### __match_args__

Для позиционного сопоставления с классом — атрибут `__match_args__` задаёт порядок позиционных параметров в паттерне:

```python
class Point:
    __match_args__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


match Point(1, 2):
    case Point(0, y):   # позиционно: x=0, y=захватываем
        print(f"На оси Y: {y}")
    case Point(x, 0):   # x=захватываем, y=0
        print(f"На оси X: {x}")
    case Point(x, y):
        print(f"Точка ({x}, {y})")
```

У `@dataclass` `__match_args__` генерируется автоматически из полей.

### match vs if/elif

`match` предпочтительнее когда:

- Данные имеют чёткую __структуру__ (кортежи, словари, объекты)
- Нужно __деструктурировать__ значение и одновременно проверить его форму
- Много вариантов с разной структурой данных

```python
# if/elif — многословно и не деструктурирует
def process(event):
    if isinstance(event, dict):
        if event.get("type") == "click" and "x" in event and "y" in event:
            handle_click(event["x"], event["y"])
        elif event.get("type") == "keypress" and "key" in event:
            handle_key(event["key"])

# match — структурно и чисто
def process(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            handle_click(x, y)
        case {"type": "keypress", "key": key}:
            handle_key(key)
```

---

## Домашнее задание

Создайте файл `hw09.py`. Сдача через PR, ветка: `hw09/фамилия`.

__1.__ Напишите метакласс `SingletonMeta` который гарантирует что класс имеет не более одного экземпляра. Повторный вызов `MyClass()` должен возвращать уже существующий экземпляр. Проверьте через `is` что оба вызова дают один объект.

__2.__ Используя `__init_subclass__` напишите базовый класс `Validator` который автоматически регистрирует все подклассы в словаре по имени. Добавьте подклассы `IntValidator`, `StrValidator`, `EmailValidator`. Напишите функцию `validate(value, validator_name)` которая находит нужный валидатор по имени и применяет его.

__3.__ Напишите функцию `evaluate(expr)` которая принимает вложенную структуру данных представляющую математическое выражение и вычисляет его через `match/case`:

- `("num", n)` → число `n`
- `("add", a, b)` → `evaluate(a) + evaluate(b)`
- `("mul", a, b)` → `evaluate(a) * evaluate(b)`
- `("neg", a)` → `-evaluate(a)`

Пример: `evaluate(("add", ("num", 2), ("mul", ("num", 3), ("num", 4))))` → `14`.
