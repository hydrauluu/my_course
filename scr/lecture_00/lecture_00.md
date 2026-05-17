# Лекция 0. Объекты, типы, ссылки

> 📖 Документация: [Objects, values and types](https://docs.python.org/3/reference/datamodel.html#objects-values-and-types) · [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html) · [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)

---

## Объект

!!! quote "docs.python.org / datamodel — 3.1. Objects, values and types"
    *Objects are Python's abstraction for data. All data in a Python program is represented by objects or by relations between objects. Even code is represented by objects.*

В Python **всё является объектом**. Число, строка, список, функция, класс, модуль, `None` — всё без исключения. Это не метафора и не упрощение — это буквально то, как устроен язык на уровне интерпретатора.

### Identity, type, value

У каждого объекта есть ровно три характеристики.

**Identity** — уникальный идентификатор объекта. Присваивается в момент создания и никогда не меняется на протяжении всей жизни объекта. Можно думать о нём как об адресе объекта в памяти.

!!! quote "docs.python.org / datamodel"
    *An object's identity never changes once it has been created; you may think of it as the object's address in memory. The `is` operator compares the identity of two objects; the `id()` function returns an integer representing its identity.*

```python
x = 42
print(id(x))  # например: 140234567891234
```

Оператор `is` сравнивает именно identity, а не значение. `a is b` — это то же самое что `id(a) == id(b)`.

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True — одинаковые значения
print(a is b)   # False — разные объекты
```

**Type** — определяет какие операции допустимы над объектом и какие значения он может принимать. Возвращается функцией `type()`. Тип объекта, как и его identity, не меняется после создания.

!!! quote "docs.python.org / datamodel"
    *An object's type determines the operations that the object supports (e.g., "does it have a length?") and also defines the possible values for objects of that type. The `type()` function returns an object's type (which is an object itself).*

```python
print(type(42))        # <class 'int'>
print(type("hello"))   # <class 'str'>
print(type([1, 2]))    # <class 'list'>
```

Обратите внимание: сам тип — тоже объект. `int`, `str`, `list` — это объекты типа `type`.

```python
print(type(int))       # <class 'type'>
print(type(str))       # <class 'type'>
print(type(type))      # <class 'type'>
```

Тип есть у любого объекта, включая функции и `None`:

```python
print(type(print))     # <class 'builtin_function_or_method'>
print(type(None))      # <class 'NoneType'>
```

**Value** — содержимое объекта. В зависимости от типа может меняться или нет — об этом ниже.

### Сборщик мусора

Объекты в Python никогда не уничтожаются явно. Когда объект становится недостижимым (на него не остаётся ни одной ссылки) — интерпретатор может его удалить.

!!! quote "docs.python.org / datamodel"
    *Objects are never explicitly destroyed; however, when they become unreachable they may be garbage-collected.*

В CPython используется подсчёт ссылок: у каждого объекта есть счётчик, сколько имён на него указывают. Когда счётчик падает до нуля — объект удаляется. Подробнее к этому вернёмся в лекции про управление памятью.

---

## Переменная

Переменная в Python — это **имя, которое указывает на объект**. Не ячейка памяти с копией значения, а именно ссылка.

Оператор присваивания `=` не копирует объект. Он связывает имя с объектом.

```python
x = 42     # имя x связывается с объектом 42
y = x      # имя y связывается с тем же объектом

print(x is y)          # True
print(id(x) == id(y))  # True — оба имени смотрят на один объект
```

При переприсваивании имя просто начинает указывать на другой объект. Исходный объект при этом не меняется.

```python
x = 42     # объект 42 создан, x указывает на него
y = x      # y указывает на тот же объект
x = 100    # создан новый объект 100, x переключился на него
           # y по-прежнему смотрит на 42

print(y)   # 42
print(id(y) == id(42))  # True — объект никуда не делся
```

### Несколько имён, один объект

Из документации — важный нюанс про неизменяемые объекты:

!!! quote "docs.python.org / datamodel"
    *After `a = 1; b = 1`, a and b may or may not refer to the same object with the value one, depending on the implementation. This is because `int` is an immutable type, so the reference to `1` can be reused.*

CPython кеширует небольшие целые числа (обычно от -5 до 256) и интернирует строки, поэтому `a = 1; b = 1` даст `a is b == True`. Но это деталь реализации, на которую не стоит полагаться.

```python
a = 1000
b = 1000
print(a is b)   # False — за пределами кеша создаются разные объекты

a = 5
b = 5
print(a is b)   # True — CPython кеширует малые int
```

Для списков гарантия другая:

!!! quote "docs.python.org / datamodel"
    *After `c = []; d = []`, c and d are guaranteed to refer to two different, unique, newly created empty lists. (Note that `e = f = []` assigns the same object to both e and f.)*

```python
c = []
d = []
print(c is d)   # False — всегда разные объекты

e = f = []
print(e is f)   # True — одно и то же присваивание
```

---

## Изменяемые и неизменяемые объекты

!!! quote "docs.python.org / datamodel"
    *The value of some objects can change. Objects whose value can change are said to be mutable; objects whose value is unchangeable once they are created are called immutable.*

### Неизменяемые (immutable)

`int`, `float`, `str`, `tuple`, `bool`, `bytes` — их значение нельзя изменить после создания. Любая операция которая "изменяет" такой объект на самом деле создаёт новый.

```python
s = "hello"
print(id(s))        # например: 140234567891234

s = s + " world"
print(id(s))        # другой адрес — это уже новый объект "hello world"
```

```python
t = (1, 2, 3)
# t[0] = 10  →  TypeError: 'tuple' object does not support item assignment
```

### Изменяемые (mutable)

`list`, `dict`, `set` — их содержимое можно менять на месте. Объект при этом остаётся тем же самым.

```python
lst = [1, 2, 3]
print(id(lst))   # например: 140234567000001

lst.append(4)
print(id(lst))   # тот же адрес — объект не изменился, только содержимое
```

### Изменяемый объект внутри неизменяемого

Документация указывает на важный нюанс:

!!! quote "docs.python.org / datamodel"
    *The value of an immutable container object that contains a reference to a mutable object can change when the latter's value is changed; however the container is still considered immutable, because the collection of objects it contains cannot be changed. So, immutability is not strictly the same as having an unchangeable value, it is more subtle.*

```python
t = (1, [2, 3], 4)   # tuple содержит список
t[1].append(99)       # список можно изменить
print(t)              # (1, [2, 3, 99], 4) — tuple "изменился"
print(id(t[1]))       # но id списка тот же — это всё тот же объект
```

Tuple по-прежнему неизменяемый: он содержит ссылку на тот же список. Сама ссылка не изменилась — изменилось содержимое объекта на который она указывает.

!!! warning "Важно"
    Это различие напрямую влияет на поведение при передаче аргументов в функцию. Вернёмся к этому в лекции 3.

---

## Динамическая типизация

В Python тип привязан к **объекту**, а не к имени. Одно и то же имя может в разные моменты указывать на объекты разных типов — интерпретатор не запрещает это.

```python
x = 42        # x → объект int
x = "hello"   # x → объект str
x = [1, 2]    # x → объект list
```

Тип проверяется не заранее при написании кода, а в **момент выполнения операции**. Если операция недопустима для данного типа — возникает исключение именно тогда, когда Python доходит до этой строки.

```python
def add(a, b):
    return a + b

add(1, 2)        # 3 — работает
add("a", "b")    # "ab" — тоже работает, str поддерживает +
add(1, "b")      # TypeError — только в момент вызова
```

Это отличает Python от языков со статической типизацией (C, Java, Rust), где несоответствие типов обнаруживается компилятором до запуска программы.

---

## Исключения

!!! quote "docs.python.org / tutorial / errors"
    *There are (at least) two distinguishable kinds of errors: syntax errors and exceptions.*

**Синтаксическая ошибка** обнаруживается до запуска — парсер не может разобрать код:

```python
while True print("hello")
# SyntaxError: invalid syntax
```

**Исключение** возникает во время выполнения — когда синтаксически верный код сталкивается с ситуацией которую не может обработать.

### Как читать traceback

!!! quote "docs.python.org / tutorial / errors"
    *The last line of the error message indicates what happened. Exceptions come in different types, and the type is printed as part of the message. The string printed as the exception type is the name of the built-in exception that occurred. The rest of the line provides detail based on the type of exception and what caused it. The preceding part of the error message shows the context where the exception occurred, in the form of a stack traceback.*

```python
def foo():
    return 1 / 0

def bar():
    return foo()

bar()
```

```
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    bar()
  File "main.py", line 5, in bar
    return foo()
  File "main.py", line 2, in foo
    return 1 / 0
ZeroDivisionError: division by zero
```

Traceback читается **снизу вверх**:

- последняя строка — тип исключения и его текст
- выше — стек вызовов от места где упало до точки входа
- каждый уровень показывает файл, номер строки, имя функции и саму строку кода

### Иерархия исключений

!!! quote "docs.python.org / exceptions"
    *In Python, all exceptions must be instances of a class that derives from BaseException. In a try statement with an except clause that mentions a particular class, that clause also handles any exception classes derived from that class.*

Исключения — это классы, выстроенные в иерархию наследования. Это важно: когда вы перехватываете `Exception` — вы перехватываете и все его подклассы. Подробнее про наследование разберём в лекции про ООП.

```
BaseException
├── SystemExit               # sys.exit()
├── KeyboardInterrupt        # Ctrl+C
├── GeneratorExit
└── Exception
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── LookupError
    │   ├── IndexError       # индекс за пределами последовательности
    │   └── KeyError         # ключ не найден в словаре
    ├── AttributeError       # у объекта нет такого атрибута
    ├── NameError            # имя не определено
    │   └── UnboundLocalError
    ├── TypeError            # операция над объектом неподходящего типа
    ├── ValueError           # тип верный, но значение недопустимо
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    └── RuntimeError
```

Полная иерархия — в [документации](https://docs.python.org/3/library/exceptions.html#exception-hierarchy).

### Основные исключения и когда они возникают

Каждое исключение несёт конкретный смысл. Читайте их — они говорят именно то, что произошло.

=== "TypeError"
    Операция применена к объекту неподходящего типа:
    ```python
    "hello" + 5
    # TypeError: can only concatenate str (not "int") to str

    len(42)
    # TypeError: object of type 'int' has no len()
    ```

=== "ValueError"
    Тип правильный, но значение недопустимо:
    ```python
    int("abc")
    # ValueError: invalid literal for int() with base 10: 'abc'

    import math
    math.sqrt(-1)
    # ValueError: math domain error
    ```

=== "NameError"
    Имя не определено в текущей области видимости:
    ```python
    print(undefined_variable)
    # NameError: name 'undefined_variable' is not defined
    ```

=== "AttributeError"
    У объекта нет такого атрибута или метода:
    ```python
    x = 42
    x.append(1)
    # AttributeError: 'int' object has no attribute 'append'
    ```

=== "IndexError / KeyError"
    Несуществующий индекс или ключ:
    ```python
    [1, 2, 3][10]
    # IndexError: list index out of range

    {"a": 1}["b"]
    # KeyError: 'b'
    ```

=== "ZeroDivisionError"
    Деление на ноль:
    ```python
    1 / 0
    # ZeroDivisionError: division by zero
    ```

### Перехват исключений

```python
try:
    x = int(input("Введите число: "))
except ValueError as e:
    print(f"Ошибка: {e}")
```

Конструкция `try/except` позволяет обработать исключение вместо того чтобы дать программе упасть. Переменная после `as` содержит сам объект исключения — его можно вывести или исследовать.

Можно перехватывать несколько исключений:

```python
try:
    result = data[key] / count
except KeyError:
    print("Ключ не найден")
except ZeroDivisionError:
    print("Делитель равен нулю")
except (TypeError, ValueError) as e:
    print(f"Ошибка типа или значения: {e}")
```

!!! danger "Правило"
    Всегда перехватывайте **конкретное** исключение. Голый `except:` или `except Exception:` скрывает реальные проблемы: вы не поймёте что именно пошло не так, а отладка станет в разы сложнее.

### raise

Исключение можно вызвать явно:

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Делитель не может быть нулём")
    return a / b
```

---

## Домашнее задание

Создайте файл `hw00.py`. Сдача через PR, ветка: `hw00/фамилия`.

**1.** Выведите `Hello, World!` через `print`.

**2.** Напишите 6 фрагментов кода — каждый намеренно вызывает своё исключение. Каждый оберните в `try/except`, выведите тип исключения и его текст. Используйте 6 разных классов из иерархии выше.

**3.** Создайте список и строку. Через `id()` покажите что происходит с адресом при `.append()` у списка и при конкатенации строки. Добавьте комментарии объясняющие почему адреса ведут себя по-разному.
