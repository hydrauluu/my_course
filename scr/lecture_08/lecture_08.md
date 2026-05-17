# Лекция 8. Слоты, дескрипторы, декораторы

> 📖 Документация: [Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html) · [Data Model — __slots__](https://docs.python.org/3/reference/datamodel.html#slots) · [functools — wraps](https://docs.python.org/3/library/functools.html#functools.wraps) · [dataclasses](https://docs.python.org/3/library/dataclasses.html)

---

## Декоратор — функция над функцией

Декоратор — это не специальный синтаксис. Это просто __функция которая принимает функцию и возвращает функцию__. Символ `@` — только синтаксический сахар.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("до вызова")
        result = func(*args, **kwargs)
        print("после вызова")
        return result
    return wrapper

def greet(name):
    print(f"Hello, {name}")

greet = my_decorator(greet)   # применяем декоратор вручную
greet("Alice")
# до вызова
# Hello, Alice
# после вызова
```

Запись с `@` делает то же самое:

```python
@my_decorator
def greet(name):
    print(f"Hello, {name}")

# эквивалентно:
# greet = my_decorator(greet)
```

`@` — это просто синтаксис. Ничего более.

### functools.wraps

После декорирования `greet` — это уже не оригинальная функция, а `wrapper`. Это ломает атрибуты вроде `__name__` и `__doc__`:

```python
print(greet.__name__)   # wrapper — неправильно
print(greet.__doc__)    # None — потеряли документацию
```

`functools.wraps` копирует метаданные оригинальной функции в обёртку:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("до вызова")
        result = func(*args, **kwargs)
        print("после вызова")
        return result
    return wrapper

@my_decorator
def greet(name):
    """Приветствует пользователя."""
    print(f"Hello, {name}")

print(greet.__name__)   # greet — правильно
print(greet.__doc__)    # Приветствует пользователя.
```

!!! warning "Правило"
    Всегда используйте `@functools.wraps` при написании декораторов. Без него декоратор ломает интроспекцию, документацию и отладку.

### Декоратор с параметрами

Чтобы декоратор принимал параметры — нужен ещё один уровень вложенности: функция которая принимает параметры и возвращает декоратор:

```python
import functools

def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say(message):
    print(message)

say("hello")
# hello
# hello
# hello
```

`@repeat(3)` — сначала вызывается `repeat(3)`, получается декоратор, потом этот декоратор применяется к `say`.

### Несколько декораторов

Декораторы применяются снизу вверх:

```python
@decorator_a
@decorator_b
@decorator_c
def func(): ...

# эквивалентно:
# func = decorator_a(decorator_b(decorator_c(func)))
```

### Типичные паттерны применения

__Логирование:__

```python
def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Вызов {func.__name__} с {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} вернул {result!r}")
        return result
    return wrapper
```

__Кеширование:__

```python
def cache(func):
    memo = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in memo:
            memo[args] = func(*args)
        return memo[args]
    return wrapper

@cache
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

Встроенный аналог — `functools.lru_cache`:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

__Проверка типов:__

```python
def validate_types(**type_map):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for name, expected in type_map.items():
                if name in kwargs and not isinstance(kwargs[name], expected):
                    raise TypeError(f"{name} должен быть {expected.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(age=int, name=str)
def create_user(name, age):
    return {"name": name, "age": age}
```

---

## Дескрипторы

!!! quote "docs.python.org / Descriptor HowTo Guide"
    *The descriptor protocol is simple and offers exciting possibilities. Several use cases are so common that they have been prepackaged into built-in tools. Properties, bound methods, static methods, class methods, and `__slots__` are all based on the descriptor protocol.*

Дескриптор — объект который управляет доступом к атрибуту другого объекта. Это механизм за которым стоят `property`, `staticmethod`, `classmethod` и `__slots__`.

### Протокол дескриптора

Объект является дескриптором если реализует один или несколько методов:

- `__get__(self, obj, objtype=None)` — при чтении атрибута
- `__set__(self, obj, value)` — при записи атрибута
- `__delete__(self, obj)` — при удалении атрибута

__Дескриптор данных__ (data descriptor) — реализует `__get__` и `__set__` (или `__delete__`). Имеет приоритет над `__dict__` экземпляра.

__Дескриптор не-данных__ (non-data descriptor) — реализует только `__get__`. `__dict__` экземпляра имеет приоритет над ним.

Чтобы дескриптор работал — он должен быть __атрибутом класса__, а не экземпляра:

```python
class Ten:
    def __get__(self, obj, objtype=None):
        return 10

class A:
    x = 5       # обычный атрибут класса
    y = Ten()   # дескриптор

a = A()
print(a.x)   # 5 — обычный поиск
print(a.y)   # 10 — вызывается Ten.__get__
```

При обращении `a.y` Python видит что `A.y` — дескриптор (имеет `__get__`) и вызывает его вместо прямого возврата объекта.

### Как Python ищет атрибут — полная картина

!!! quote "docs.python.org / Descriptor HowTo Guide"
    *Data and non-data descriptors differ in how overrides are calculated with respect to entries in an instance's dictionary. If an instance's dictionary has an entry with the same name as a data descriptor, the data descriptor takes priority.*

Полный алгоритм поиска `obj.name`:

1. `type(obj).__mro__` — проходим по MRO в поисках `name`
2. Если нашли __дескриптор данных__ (`__get__` + `__set__`) → вызываем его `__get__`
3. Если нашли в `obj.__dict__` → возвращаем
4. Если нашли __дескриптор не-данных__ (`__get__` без `__set__`) → вызываем его `__get__`
5. Если нашли обычный атрибут класса → возвращаем
6. `AttributeError`

Именно поэтому `property` (дескриптор данных) имеет приоритет над `__dict__` экземпляра.

### Собственный дескриптор

```python
class TypedAttribute:
    """Дескриптор с проверкой типа."""

    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __set_name__(self, owner, name):
        # вызывается при создании класса — owner это класс, name это имя атрибута
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self   # доступ через класс — вернуть сам дескриптор
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.public_name} ожидает {self.expected_type.__name__}, "
                f"получен {type(value).__name__}"
            )
        setattr(obj, self.private_name, value)


class Person:
    name = TypedAttribute("name", str)
    age  = TypedAttribute("age", int)

    def __init__(self, name, age):
        self.name = name   # вызывает TypedAttribute.__set__
        self.age = age


p = Person("Alice", 30)
print(p.name)   # Alice — TypedAttribute.__get__

p.age = "thirty"
# TypeError: age ожидает int, получен str
```

`__set_name__` — специальный метод который Python вызывает автоматически при определении класса, передавая имя атрибута. Это позволяет дескриптору знать под каким именем он хранится.

### property как дескриптор

`property` — встроенный дескриптор данных. Вот его упрощённая реализация на Python:

```python
class Property:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc or (fget.__doc__ if fget else None)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)
```

Реальное использование:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        """Радиус окружности."""
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Радиус не может быть отрицательным")
        self._radius = value

    @property
    def area(self):
        return 3.14159 * self._radius ** 2


c = Circle(5)
print(c.radius)   # 5 — вызывает getter
print(c.area)     # 78.53...

c.radius = 10     # вызывает setter
c.radius = -1     # ValueError
```

---

## __slots__

!!! quote "docs.python.org / datamodel — __slots__"
    *`__slots__` allow us to explicitly declare data members (like properties) and deny the creation of `__dict__` and `__weakref__` (unless explicitly declared in `__slots__` or available in a parent). The space saved over using `__dict__` can be significant. Attribute lookup speed can be significantly improved as well.*

По умолчанию у каждого экземпляра есть `__dict__` — словарь для хранения атрибутов. `__slots__` заменяет его массивом фиксированного размера.

```python
class WithDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class WithSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

Последствия использования `__slots__`:

```python
ws = WithSlots(1, 2)

print(ws.x)       # 1 — работает
ws.x = 10         # работает
ws.z = 3          # AttributeError — нет слота z
print(ws.__dict__)  # AttributeError — __dict__ не создаётся
```

`__slots__` реализованы через дескрипторы — каждый слот это дескриптор в `__dict__` класса:

```python
print(type(WithSlots.x))   # <class 'member_descriptor'>
```

### Когда использовать __slots__

- Когда создаются __миллионы__ экземпляров — экономия памяти существенная
- Когда нужна __защита от опечаток__ в именах атрибутов — `AttributeError` вместо молчаливого создания нового атрибута
- Когда важна __скорость__ доступа к атрибутам

```python
import sys

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = PointSlots(1, 2)

print(sys.getsizeof(p1))   # ~48 байт (+ размер __dict__)
print(sys.getsizeof(p2))   # ~56 байт (без __dict__)
# разница становится заметной на больших количествах объектов
```

### __slots__ и наследование

!!! quote "docs.python.org / datamodel"
    *The action of a `__slots__` declaration is limited to the class where it is defined. As a result, subclasses will have a `__dict__` unless they also define `__slots__`.*

```python
class Base:
    __slots__ = ("x",)

class Child(Base):
    pass   # __dict__ снова создаётся у Child

c = Child()
c.x = 1    # работает — слот из Base
c.z = 3    # тоже работает — через __dict__ Child
```

---

## dataclasses — декоратор для классов

`@dataclass` — декоратор который автоматически генерирует `__init__`, `__repr__`, `__eq__` и другие методы на основе аннотаций:

!!! quote "docs.python.org / dataclasses"
    *If `@dataclass` is used just as a simple decorator with no parameters, it acts as if it has the default values: `@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)`*

```python
from dataclasses import dataclass, field

@dataclass
class Point:
    x: float
    y: float

p1 = Point(1.0, 2.0)
p2 = Point(1.0, 2.0)

print(p1)          # Point(x=1.0, y=2.0) — __repr__ сгенерирован
print(p1 == p2)    # True — __eq__ сгенерирован
```

С параметрами:

```python
@dataclass(order=True, frozen=True)
class Vector:
    x: float
    y: float
    z: float = 0.0   # дефолтное значение

    def magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5
```

`frozen=True` — делает экземпляры неизменяемыми (через `__setattr__` и `__delattr__` которые поднимают исключение). `order=True` — генерирует `__lt__`, `__le__`, `__gt__`, `__ge__`.

Мутабельные дефолты через `field`:

```python
from dataclasses import dataclass, field

@dataclass
class Inventory:
    items: list = field(default_factory=list)   # новый список для каждого экземпляра
    tags: set  = field(default_factory=set)
```

`field(default_factory=list)` — правильный способ задать мутабельный дефолт. Без `field` Python поднимет `ValueError`.

---

## Читаем реальный код — Pydantic

[Pydantic](https://github.com/pydantic/pydantic) — библиотека для валидации данных через аннотации типов. Внутри активно использует дескрипторы.

В `pydantic/fields.py` — класс `FieldInfo` описывает поле модели. Когда вы пишете:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0, lt=150)
    email: str = Field(pattern=r".+@.+\..+")
```

`Field(gt=0)` — это вызов функции которая возвращает объект `FieldInfo`. Pydantic при создании класса `User` через метакласс читает аннотации (`__annotations__`) и `FieldInfo` объекты, и строит валидаторы.

При присваивании `user.age = -1` срабатывает дескриптор который вызывает валидатор — и поднимает `ValidationError`.

Упрощённо как это устроено:

```python
class ValidatedField:
    def __init__(self, validator):
        self.validator = validator

    def __set_name__(self, owner, name):
        self.name = name
        self.private = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        validated = self.validator(value)   # валидация при записи
        setattr(obj, self.private, validated)


def positive_int(value):
    value = int(value)
    if value <= 0:
        raise ValueError(f"Ожидается положительное число, получено {value}")
    return value


class User:
    age = ValidatedField(positive_int)

    def __init__(self, age):
        self.age = age   # проходит через ValidatedField.__set__


u = User(25)
print(u.age)   # 25

u.age = -1     # ValueError: Ожидается положительное число, получено -1
```

---

## Домашнее задание

Создайте файл `hw08.py`. Сдача через PR, ветка: `hw08/фамилия`.

__1.__ Напишите декоратор `retry(n, exceptions)` — он перезапускает декорируемую функцию до `n` раз если она поднимает одно из указанных исключений. Если после `n` попыток функция всё равно упала — пробрасывает исключение дальше. Используйте `@functools.wraps`.

__2.__ Напишите дескриптор `Bounded(min_val, max_val)` который при установке атрибута проверяет что значение в диапазоне `[min_val, max_val]` и поднимает `ValueError` если нет. Используйте `__set_name__`. Примените его в классе `Thermometer` с атрибутом `temperature` в диапазоне от -273.15 до 1_000_000.

__3.__ Напишите `@dataclass` класс `Transaction` с полями: `amount: float`, `currency: str`, `description: str = ""`, `tags: list`. Сделайте его `frozen=True`. Добавьте метод `in_usd(rates: dict)` который конвертирует сумму по словарю курсов. Покажите что экземпляр нельзя изменить после создания.
