# Лекция 10. Типизация в Python

> 📖 Документация: [typing — Support for type hints](https://docs.python.org/3/library/typing.html) · [PEP 484 — Type Hints](https://peps.python.org/pep-0484/) · [PEP 544 — Protocols](https://peps.python.org/pep-0544/) · [PEP 589 — TypedDict](https://peps.python.org/pep-0589/) · [PEP 585 — Built-in generics](https://peps.python.org/pep-0585/)

---

## Зачем типизация в динамическом языке

В лекции 0 мы разобрали что Python динамически типизирован — тип проверяется в момент выполнения. Аннотации типов этого не меняют.

!!! quote "PEP 484 — Type Hints"
    *This PEP aims to provide a standard syntax for type annotations, opening up Python code to easier static analysis and refactoring, potential runtime type checking, and code generation utilizing type information. It should also be noted that Python will remain a dynamically typed language, and the authors have no desire to ever make type hints mandatory, even by convention.*

Аннотации типов — это **подсказки для инструментов**, а не ограничения для интерпретатора. Python их не проверяет и не исполняет во время работы программы:

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")   # "helloworld" — Python не возражает
```

Аннотации дают:

- **Статический анализ** — `mypy`, `pyright` находят ошибки до запуска
- **IDE-поддержку** — автодополнение, навигация, рефакторинг
- **Документацию** — сигнатура функции говорит что принимает и возвращает
- **Runtime-валидацию** — через Pydantic и подобные библиотеки

---

## Базовые аннотации

Аннотации записываются через `:` для параметров и переменных, через `->` для возвращаемого значения:

```python
# функции
def greet(name: str) -> str:
    return f"Hello, {name}"

def divide(a: float, b: float) -> float:
    return a / b

# переменные (PEP 526)
count: int = 0
name: str
items: list[str] = []
```

Аннотации хранятся в `__annotations__`:

```python
print(greet.__annotations__)
# {'name': <class 'str'>, 'return': <class 'str'>}
```

---

## Встроенные обобщённые типы

До Python 3.9 для аннотаций нужно было импортировать типы из `typing`. Начиная с Python 3.9 встроенные типы стали напрямую поддерживать параметризацию:

```python
# Python 3.9+
def process(items: list[int]) -> dict[str, int]:
    ...

# до 3.9 нужно было:
from typing import List, Dict
def process(items: List[int]) -> Dict[str, int]:
    ...
```

Параметризация работает для `list`, `dict`, `set`, `frozenset`, `tuple`, `type` и других встроенных типов.

```python
# tuple — фиксированной длины
def get_point() -> tuple[int, int]:
    return (1, 2)

# tuple произвольной длины
def get_items() -> tuple[int, ...]:
    return (1, 2, 3, 4)

# вложенные
def get_registry() -> dict[str, list[tuple[int, str]]]:
    ...
```

---

## Optional и Union

**`Optional[X]`** — значение может быть `X` или `None`. Это сокращение для `Union[X, None]`:

```python
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None   # явный None — это нормально

# Python 3.10+ — через |
def find_user(user_id: int) -> str | None:
    ...
```

**`Union[X, Y]`** — значение может быть одним из нескольких типов:

```python
from typing import Union

def parse(value: Union[str, bytes]) -> str:
    if isinstance(value, bytes):
        return value.decode()
    return value

# Python 3.10+
def parse(value: str | bytes) -> str:
    ...
```

Когда использовать `Optional` vs возвращать исключение — зависит от семантики. `Optional` сигнализирует что "ничего не найдено" — нормальный исход. Исключение — для ошибочных ситуаций.

---

## Any

`Any` — специальный тип совместимый с любым другим. Отключает проверку:

```python
from typing import Any

def process(data: Any) -> Any:
    return data   # тип не проверяется
```

!!! quote "PEP 484 — Type Hints"
    *The type system supports unions, generic types, and a special type named Any which is consistent with (i.e. assignable to and from) all types. This latter feature is taken from the idea of gradual typing.*

`Any` полезен при постепенном добавлении типизации в существующий код. Но злоупотребление им лишает смысла всю аннотацию.

---

## Callable

`Callable[[ArgTypes], ReturnType]` — аннотация для функций как объектов:

```python
from typing import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

apply(lambda x, y: x + y, 1, 2)   # 3

# функция без аргументов возвращающая строку
def get_greeting() -> str: ...
setter: Callable[[], str] = get_greeting

# функция с произвольными аргументами
def log(func: Callable[..., Any]) -> Callable[..., Any]: ...
```

---

## TypeVar — переменные типа

!!! quote "docs.python.org / typing — TypeVar"
    *Type variables exist primarily for the benefit of static type checkers. They serve as the parameters for generic types as well as for generic function definitions.*

`TypeVar` — параметр типа. Позволяет выразить что тип входа и выхода функции связаны:

```python
from typing import TypeVar

T = TypeVar("T")

def identity(x: T) -> T:
    return x   # возвращает тот же тип что получил

result = identity(42)     # result: int
result = identity("hi")   # result: str
```

Без `TypeVar` это пришлось бы писать как `Any -> Any` — теряя информацию о связи типов.

### TypeVar с ограничениями

```python
from typing import TypeVar

# только str или bytes
AnyStr = TypeVar("AnyStr", str, bytes)

def concat(a: AnyStr, b: AnyStr) -> AnyStr:
    return a + b

concat("hello", "world")   # OK — str + str
concat(b"foo", b"bar")     # OK — bytes + bytes
concat("foo", b"bar")      # ошибка — нельзя смешивать
```

### TypeVar с bound

`bound` задаёт верхнюю границу — тип должен быть подклассом указанного:

```python
from typing import TypeVar

class Animal:
    def speak(self) -> str: ...

AnimalT = TypeVar("AnimalT", bound=Animal)

def make_speak(animal: AnimalT) -> AnimalT:
    print(animal.speak())
    return animal   # возвращает тот же подтип
```

---

## Generic — обобщённые классы

`Generic[T]` — базовый класс для создания параметризованных классов:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T:
        return self._items[-1]

    def is_empty(self) -> bool:
        return not self._items


stack: Stack[int] = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())   # 2

stack.push("hello")  # mypy: Argument of type "str" is not assignable to "int"
```

### Несколько параметров типа

```python
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class Mapping(Generic[K, V]):
    def __init__(self) -> None:
        self._data: dict[K, V] = {}

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)


m: Mapping[str, int] = Mapping()
m.set("age", 30)
m.get("age")   # int | None
```

---

## Protocol — структурная типизация

!!! quote "docs.python.org / typing — Protocol"
    *Such classes are primarily used with static type checkers that recognize structural subtyping (static duck-typing).*

`Protocol` — механизм **структурной типизации** (duck typing со статической проверкой). Класс удовлетворяет протоколу если у него есть нужные методы — без явного наследования.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...
    def resize(self, factor: float) -> None: ...


class Circle:
    def draw(self) -> None:
        print("Drawing circle")

    def resize(self, factor: float) -> None:
        self.radius *= factor


class Square:
    def draw(self) -> None:
        print("Drawing square")

    def resize(self, factor: float) -> None:
        self.side *= factor


def render(shape: Drawable) -> None:
    shape.draw()


render(Circle())   # OK — Circle реализует Drawable
render(Square())   # OK — Square реализует Drawable
```

`Circle` и `Square` не наследуют от `Drawable` — они просто имеют нужные методы. Это и есть duck typing: "если ходит как утка и крякает как утка — это утка".

### Protocol vs ABC

| | Protocol | ABC (Abstract Base Class) |
|---|---|---|
| Тип совместимости | структурная | номинальная |
| Нужно явное наследование | нет | да |
| Проверка | статическая (mypy) | runtime (`isinstance`) |
| Когда использовать | для внешних классов | для иерархий под вашим контролем |

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

# с @runtime_checkable можно использовать isinstance
print(isinstance(Circle(), Drawable))   # True
```

---

## TypedDict

`TypedDict` — словарь с фиксированными ключами и типами значений:

```python
from typing import TypedDict

class Point(TypedDict):
    x: float
    y: float

class UserProfile(TypedDict):
    name: str
    age: int
    email: str

# при runtime это обычный dict
p: Point = {"x": 1.0, "y": 2.0}
print(type(p))   # <class 'dict'>

# mypy проверит ключи и типы
u: UserProfile = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
}
```

С необязательными ключами:

```python
from typing import TypedDict, NotRequired

class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]   # необязательный ключ

config: Config = {"host": "localhost", "port": 8080}   # OK
```

`TypedDict` полезен когда работаете с JSON-подобными структурами и хотите статическую проверку без создания полноценного класса.

---

## Аннотации в реальном коде

### Как читать аннотированный код библиотек

Откроем [django/db/models/query.py](https://github.com/django/django/blob/main/django/db/models/query.py) — сигнатура метода `filter`:

```python
def filter(self, *args: Any, **kwargs: Any) -> "QuerySet[_MT]":
    ...
```

- `*args: Any` — позиционные аргументы любого типа (Q-объекты)
- `**kwargs: Any` — именованные аргументы любого типа (условия фильтрации)
- `-> "QuerySet[_MT]"` — возвращает `QuerySet` параметризованный типом модели. Строка в кавычках — форвардная ссылка, класс ещё не определён в этот момент

`_MT` — это `TypeVar` определённый где-то выше:

```python
_MT = TypeVar("_MT", bound="Model")
```

Ограничен `Model` — значит `QuerySet[_MT]` может быть только `QuerySet[Book]`, `QuerySet[User]` и т.д., но не `QuerySet[str]`.

### Pydantic как пример runtime-типизации

Pydantic использует аннотации типов для валидации **во время выполнения**:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0, lt=150)
    email: str

# Pydantic проверяет типы при создании экземпляра
user = User(name="Alice", age=30, email="alice@example.com")

User(name="Alice", age="not a number", email="x")
# ValidationError: age — value is not a valid integer
```

Под капотом Pydantic читает `__annotations__` класса и строит валидаторы через дескрипторы — то что мы разобрали в лекции 8.

---

## Постепенная типизация

!!! quote "PEP 484 — Type Hints"
    *It should also be noted that Python will remain a dynamically typed language, and the authors have no desire to ever make type hints mandatory, even by convention.*

Типизацию можно добавлять постепенно — это называется **gradual typing**. Нетипизированный код совместим с типизированным через `Any`.

Типичный подход:

1. Начать с аннотаций публичного API — функций и методов
2. Добавить аннотации к внутренним функциям
3. Добавить аннотации к переменным где тип неочевиден
4. Настроить `mypy` в строгом режиме

```ini
# mypy.ini
[mypy]
python_version = 3.12
strict = True
warn_return_any = True
warn_unused_ignores = True
```

`# type: ignore` — подавить ошибку mypy для конкретной строки. Использовать как последнее средство с комментарием почему:

```python
result = some_dynamic_call()  # type: ignore[no-untyped-call]  # legacy API
```

---

## Домашнее задание

Создайте файл `hw10.py`. Сдача через PR, ветка: `hw10/фамилия`.

**1.** Напишите обобщённую функцию `first(items: list[T]) -> T | None` которая возвращает первый элемент списка или `None` если список пуст. Напишите `last` аналогично. Проверьте что mypy выводит правильные типы для `first([1, 2, 3])` и `first(["a", "b"])`.

**2.** Определите `Protocol` с именем `Serializable` с методами `to_dict() -> dict[str, Any]` и `from_dict(data: dict[str, Any]) -> Self`. Напишите два класса которые реализуют этот протокол без явного наследования — `User` и `Product`. Напишите функцию `serialize_all(items: list[Serializable]) -> list[dict[str, Any]]`.

**3.** Напишите `TypedDict` для конфигурации HTTP-запроса: обязательные поля `url: str` и `method: str`, необязательные `headers: dict[str, str]`, `body: str`, `timeout: int`. Напишите функцию `make_request(config: RequestConfig) -> dict[str, Any]` которая имитирует выполнение запроса.
