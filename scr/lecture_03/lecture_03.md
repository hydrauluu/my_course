# Лекция 3. Функции, замыкания, области видимости

> 📖 Документация: [Function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions) · [More Control Flow — Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) · [Execution model — Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding) · [Glossary — closure variable](https://docs.python.org/3/glossary.html#term-closure-variable)

---

## Функция как объект

В лекции 0 мы установили что всё в Python — объект. Функция не исключение.

```python
def greet(name):
    return f"Hello, {name}"

print(type(greet))   # <class 'function'>
print(id(greet))     # адрес в памяти
```

Функция — объект типа `function`. Её можно присвоить другому имени, передать как аргумент, вернуть из другой функции, положить в список.

```python
say_hello = greet         # второе имя для того же объекта
print(say_hello("Alice")) # Hello, Alice

funcs = [greet, print, len]
for f in funcs:
    print(type(f))
```

Это не трюк и не частный случай — это прямое следствие того что функция является объектом. Всё что можно делать с любым объектом, можно делать и с функцией.

---

## Параметр vs аргумент

Это различие важно зафиксировать раз и навсегда.

!!! quote "docs.python.org / glossary"
    **parameter** — *A named entity in a function (or method) definition that specifies an argument (or in some cases, arguments) that the function can accept.*

    **argument** — *A value passed to a function (or method) when calling the function. Arguments are assigned to the named local variables called parameters.*

**Параметр** — имя в определении функции. Существует в момент написания кода.

**Аргумент** — объект который передаётся при вызове. Существует в момент выполнения.

```python
def add(a, b):   # a и b — параметры
    return a + b

add(1, 2)        # 1 и 2 — аргументы
```

### Виды параметров

!!! quote "docs.python.org / glossary — parameter"
    *There are five kinds of parameter: positional-or-keyword, positional-only, keyword-only, var-positional, var-keyword.*

```python
def f(pos_or_kw, /, pos_or_kw2, *, kw_only, **kwargs):
    pass
```

Разберём каждый вид:

**Позиционные или именованные** — обычные параметры, передаются и позиционно и по имени:

```python
def greet(name, greeting):
    return f"{greeting}, {name}"

greet("Alice", "Hello")           # позиционно
greet(name="Alice", greeting="Hi") # по имени
greet("Alice", greeting="Hi")     # смешанно
```

**Только позиционные** (до `/`) — нельзя передать по имени. Используются в стандартной библиотеке:

```python
def pos_only(a, b, /):
    return a + b

pos_only(1, 2)         # OK
pos_only(a=1, b=2)     # TypeError
```

**Только именованные** (после `*`) — нельзя передать позиционно:

```python
def kw_only(*, name, greeting="Hello"):
    return f"{greeting}, {name}"

kw_only(name="Alice")           # OK
kw_only("Alice")                # TypeError
```

**`*args`** — захватывает все лишние позиционные аргументы в кортеж:

```python
def variadic(*args):
    print(type(args))   # <class 'tuple'>
    for arg in args:
        print(arg)

variadic(1, 2, 3, 4)   # args = (1, 2, 3, 4)
```

**`**kwargs`** — захватывает все лишние именованные аргументы в словарь:

```python
def variadic_kw(**kwargs):
    print(type(kwargs))   # <class 'dict'>
    for key, value in kwargs.items():
        print(f"{key} = {value}")

variadic_kw(name="Alice", age=30)   # kwargs = {'name': 'Alice', 'age': 30}
```

Все виды вместе:

```python
def full(a, b, /, c, d, *args, e, f=10, **kwargs):
    pass
```

### Значения по умолчанию — важный нюанс

!!! quote "docs.python.org / tutorial — controlflow"
    *Important warning: The default value is evaluated only once. This makes a difference when the default is a mutable object such as a list, dictionary, or instances of most classes.*

```python
def append_to(element, lst=[]):   # lst создаётся один раз при определении
    lst.append(element)
    return lst

print(append_to(1))   # [1]
print(append_to(2))   # [1, 2] — тот же объект lst!
print(append_to(3))   # [1, 2, 3]
```

Это классическая ловушка. Правильный паттерн — использовать `None` как дефолт:

```python
def append_to(element, lst=None):
    if lst is None:
        lst = []       # новый список на каждый вызов
    lst.append(element)
    return lst
```

### Передача аргументов — передача ссылок

Аргументы передаются как ссылки — это прямое следствие лекции 0. Функция получает не копию объекта, а ссылку на него.

```python
def modify(lst):
    lst.append(4)      # изменяем объект по ссылке

data = [1, 2, 3]
modify(data)
print(data)   # [1, 2, 3, 4] — исходный список изменился
```

```python
def rebind(lst):
    lst = [99, 98, 97]  # переприсваивание — локальная ссылка

data = [1, 2, 3]
rebind(data)
print(data)   # [1, 2, 3] — исходный не изменился
```

В первом случае мы изменяем объект через ссылку. Во втором — перепривязываем локальное имя `lst` к новому объекту, исходная ссылка не затрагивается.

---

## Области видимости и правило LEGB

!!! quote "docs.python.org / glossary"
    *The scope of a name defines the region of a program where you can unambiguously access that name.*

Когда Python встречает имя, он ищет его в определённом порядке — **LEGB**:

| Уровень | Описание |
|---|---|
| **L** — Local | Локальная область текущей функции |
| **E** — Enclosing | Области видимости объемлющих функций (снаружи внутрь) |
| **G** — Global | Глобальная область модуля |
| **B** — Built-in | Встроенные имена Python (`len`, `print`, `int`, ...) |

Python останавливается на первом уровне где нашёл имя.

```python
x = "global"          # G

def outer():
    x = "enclosing"   # E для inner

    def inner():
        x = "local"   # L
        print(x)      # найдёт "local" — уровень L

    inner()
    print(x)          # найдёт "enclosing" — уровень E

outer()
print(x)              # найдёт "global" — уровень G
```

### NameError и LEGB

Если имя не найдено ни на одном уровне — `NameError`:

```python
def f():
    print(y)   # y нет ни в L, ни в E, ни в G, ни в B

f()   # NameError: name 'y' is not defined
```

### Коварная ловушка — UnboundLocalError

Как только Python видит **присваивание** имени внутри функции — он помечает это имя как локальное для всей функции, включая строки до присваивания:

```python
x = 10

def f():
    print(x)   # UnboundLocalError — Python уже знает что x локальная
    x = 20     # это присваивание делает x локальной во всей функции

f()
```

Это не ошибка интерпретатора — это намеренное поведение. Присваивание всегда создаёт локальную переменную, если явно не указано иное.

### global и nonlocal

**`global`** — объявляет что имя относится к глобальной области:

```python
count = 0

def increment():
    global count    # теперь count — это глобальная переменная
    count += 1

increment()
increment()
print(count)   # 2
```

**`nonlocal`** — объявляет что имя относится к ближайшей объемлющей области (не глобальной):

```python
def outer():
    count = 0

    def inner():
        nonlocal count   # count из outer
        count += 1
        return count

    return inner

inc = outer()
print(inc())   # 1
print(inc())   # 2
print(inc())   # 3
```

!!! warning "Важно"
    `global` и `nonlocal` — инструменты с узкой областью применения. Широкое использование глобальных переменных затрудняет понимание и тестирование кода. Предпочтительнее передавать состояние через аргументы и возвращаемые значения.

---

## Замыкание (closure)

!!! quote "docs.python.org / glossary — closure variable"
    *A free variable referenced from a nested scope that is defined in an outer scope rather than being resolved at runtime from the globals or builtin namespaces.*

Замыкание — это функция которая **помнит** переменные из объемлющей области видимости даже после того как эта область завершила выполнение.

```python
def make_adder(x):
    def adder(y):
        return x + y    # x — свободная переменная из make_adder
    return adder        # возвращаем функцию-объект

add5 = make_adder(5)    # make_adder выполнилась и завершилась
add10 = make_adder(10)

print(add5(3))    # 8 — adder помнит x=5
print(add10(3))   # 13 — adder помнит x=10
```

`make_adder` уже завершила выполнение, переменная `x` давно вышла бы из области видимости — но замыкание удерживает её живой.

Посмотреть что именно захватывает замыкание можно через `__closure__`:

```python
print(add5.__closure__)           # (<cell at 0x...>,)
print(add5.__closure__[0].cell_contents)   # 5
```

### Замыкание с изменяемым состоянием

Через `nonlocal` замыкание может не только читать, но и изменять захваченную переменную:

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())   # 1
print(counter())   # 2
print(counter())   # 3

counter2 = make_counter()
print(counter2())  # 1 — независимое состояние
```

Каждый вызов `make_counter()` создаёт **новую** переменную `count` — у каждого счётчика своё независимое состояние.

### Классическая ловушка — позднее связывание

!!! quote "docs.python.org / glossary — closure variable"
    *Closure variables are not copies of the outer variable's value; they are references to the variable binding itself.*

Замыкание захватывает не значение переменной, а **ссылку на переменную**. Это приводит к неочевидному поведению в циклах:

```python
functions = []
for i in range(3):
    def f():
        return i       # захватывает ссылку на i, а не значение
    functions.append(f)

print([f() for f in functions])   # [2, 2, 2] — все видят последнее i
```

После цикла `i == 2`. Все три функции захватили одну и ту же переменную `i`, которая в конце равна 2.

Решение — захватить текущее значение через аргумент по умолчанию:

```python
functions = []
for i in range(3):
    def f(i=i):        # default argument вычисляется сейчас
        return i
    functions.append(f)

print([f() for f in functions])   # [0, 1, 2]
```

---

## Нотация Бэкуса-Наура

В документации Python описание синтаксиса дано в форме **BNF (Backus-Naur Form)** — формальной грамматики для описания языков.

Пример из документации:

!!! quote "docs.python.org / compound statements — function definitions

  ``` python
  funcdef:                   [decorators] "def" funcname [type_params] "(" [parameter_list] ")"
                            ["->" expression] ":" suite
  decorators:                decorator+
  decorator:                 "@" assignment_expression NEWLINE
  parameter_list:            defparameter ("," defparameter)* "," "/" ["," [parameter_list_no_posonly]]
                              | parameter_list_no_posonly
  parameter_list_no_posonly: defparameter ("," defparameter)* ["," [parameter_list_starargs]]
                            | parameter_list_starargs
  parameter_list_starargs:   "*" [star_parameter] ("," defparameter)* ["," [parameter_star_kwargs]]
                            | "*" ("," defparameter)+ ["," [parameter_star_kwargs]]
                            | parameter_star_kwargs
  parameter_star_kwargs:     "**" parameter [","]
  parameter:                 identifier [":" expression]
  star_parameter:            identifier [":" ["*"] expression]
  defparameter:              parameter ["=" expression]
  funcname:                  identifier
  ```

Как читать:

- `::=` — "определяется как"
- `|` — "или"
- `[...]` — необязательная часть
- `(...)` — группировка
- `*` — ноль или более повторений
- `+` — одно или более повторений
- `"def"` — литеральное ключевое слово

Это не страшно — это просто способ точно описать что допустимо в синтаксисе. Когда видите непонятную конструкцию в документации — читайте BNF как инструкцию.

---

## lambda

!!! quote "docs.python.org / tutorial — controlflow"
    *Lambda functions can be used wherever function objects are required. They are syntactically restricted to a single expression. Semantically, they are just syntactic sugar for a normal function definition.*

`lambda` — способ создать анонимную функцию из одного выражения:

```python
add = lambda a, b: a + b
print(add(1, 2))   # 3
```

Эквивалентно:

```python
def add(a, b):
    return a + b
```

Типичное применение — передать короткую функцию как аргумент:

```python
pairs = [(1, "one"), (2, "two"), (3, "three")]
pairs.sort(key=lambda pair: pair[1])
print(pairs)   # [(1, 'one'), (3, 'three'), (2, 'two')]

nums = [3, 1, 4, 1, 5, 9]
nums.sort(key=lambda x: -x)   # сортировка по убыванию
```

`lambda` тоже создаёт замыкание и подчиняется тем же правилам LEGB:

```python
def make_multiplier(n):
    return lambda x: x * n   # n захвачена из make_multiplier

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
```

---

## Домашнее задание

Создайте файл `hw03.py`. Сдача через PR, ветка: `hw03/фамилия`.

**1.** Напишите функцию `make_validator(min_val, max_val)` которая возвращает функцию-валидатор. Валидатор принимает число и возвращает `True` если оно в диапазоне `[min_val, max_val]`, иначе `False`. Продемонстрируйте что два разных валидатора имеют независимое состояние.

**2.** Воспроизведите и исправьте ловушку позднего связывания: создайте список из трёх функций в цикле, каждая должна возвращать свой индекс. Покажите неправильный вариант (все возвращают одно) и правильный.

**3.** Напишите функцию с сигнатурой `def log(func, *args, **kwargs)` которая вызывает `func` с переданными аргументами, выводит имя функции (`func.__name__`), аргументы и результат, и возвращает результат. Проверьте на нескольких разных функциях.
