# Лекция 5. Итераторы и генераторы

> 📖 Документация: [Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types) · [yield expression](https://docs.python.org/3/reference/expressions.html#yield-expressions) · [Generator Types](https://docs.python.org/3/library/stdtypes.html#generator-types) · [itertools](https://docs.python.org/3/library/itertools.html) · [PEP 255 — Simple Generators](https://peps.python.org/pep-0255/) · [PEP 289 — Generator Expressions](https://peps.python.org/pep-0289/)

---

## Зачем нужны генераторы

В лекции 2 мы разобрали протокол итерации и написали собственный итератор как класс. Это работает, но многословно: нужно хранить состояние в атрибутах, писать `__iter__` и `__next__`, явно поднимать `StopIteration`.

Генераторы решают ту же задачу значительно проще — через обычную функцию с `yield`.

!!! quote "PEP 255 — Simple Generators"
    *When a producer function has a hard enough job that it requires maintaining state between values produced, most programming languages offer no pleasant and efficient solution beyond adding a callback function to the producer's argument list. A Python generator is a kind of Python iterator, but of an especially powerful kind.*

Ключевая идея: генератор — это **возобновляемая функция**. Она может приостановить выполнение, вернуть значение, и продолжить с того же места при следующем вызове.

---

## Генераторная функция

!!! quote "PEP 255 — Simple Generators"
    *A function that contains a yield statement is called a generator function. A generator function is an ordinary function object in all respects.*

Любая функция содержащая `yield` — генераторная. При вызове она **не выполняется** — она возвращает объект-генератор.

```python
def simple():
    print("шаг 1")
    yield 1
    print("шаг 2")
    yield 2
    print("шаг 3")
    yield 3
    print("конец")

gen = simple()     # функция не выполнилась — создался генератор
print(type(gen))   # <class 'generator'>
```

Выполнение происходит пошагово через `next()`:

```python
print(next(gen))   # шаг 1 → 1
print(next(gen))   # шаг 2 → 2
print(next(gen))   # шаг 3 → 3
print(next(gen))   # конец → StopIteration
```

Каждый вызов `next()` выполняет функцию до следующего `yield`, возвращает его значение и **замораживает** состояние — все локальные переменные, позицию в коде, стек вызовов.

!!! quote "PEP 255 — Simple Generators"
    *The big difference between yield and a return statement is that on reaching a yield the generator's state of execution is suspended and local variables are preserved. On the next call to the generator's `__next__()` method, the function will resume executing immediately after the yield statement.*

### Генератор реализует протокол итератора

Генератор автоматически реализует `__iter__` и `__next__` — его можно использовать в `for`, передавать в `zip`, `map`, `list()` и т.д.:

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

for x in countdown(5):
    print(x)   # 5, 4, 3, 2, 1

print(list(countdown(3)))   # [3, 2, 1]
print(sum(countdown(100)))  # 5050
```

### Сравнение с классовым итератором

Вот один и тот же итератор — через класс и через генератор:

=== "Класс"
    ```python
    class CountUp:
        def **init**(self, start, stop):
            self.current = start
            self.stop = stop

        def __iter__(self):
            return self

        def __next__(self):
            if self.current >= self.stop:
                raise StopIteration
            value = self.current
            self.current += 1
            return value
    ```

=== "Генератор"
    ```python
    def count_up(start, stop):
        current = start
        while current < stop:
            yield current
            current += 1
    ```

Результат одинаковый, генератор в разы короче. Состояние хранится в локальных переменных, а не в атрибутах объекта.

---

## Ленивые вычисления

Генераторы **не вычисляют всё сразу**. Каждое значение производится только когда его запрашивают через `next()`. Это называется ленивыми вычислениями.

```python
def infinite_counter(start=0):
    n = start
    while True:
        yield n
        n += 1

gen = infinite_counter()   # бесконечная последовательность
                           # в памяти — только текущее значение

print(next(gen))   # 0
print(next(gen))   # 1
print(next(gen))   # 2
# ... можно вызывать бесконечно
```

Сравните с созданием списка — `list(range(1_000_000))` занимает память пропорционально размеру. Генератор всегда занимает O(1) памяти независимо от количества элементов.

```python
# плохо — создаёт список из миллиона чисел в памяти
total = sum([x**2 for x in range(1_000_000)])

# хорошо — вычисляет по одному, O(1) память
total = sum(x**2 for x in range(1_000_000))
```

---

## yield — подробнее

### return в генераторе

`return` в генераторной функции поднимает `StopIteration`. Значение передаётся как атрибут исключения:

```python
def gen_with_return():
    yield 1
    yield 2
    return "done"   # StopIteration("done")

g = gen_with_return()
print(next(g))   # 1
print(next(g))   # 2
try:
    next(g)
except StopIteration as e:
    print(e.value)   # done
```

### yield from

`yield from` делегирует итерацию другому итерируемому объекту — как если бы вы написали `for x in iterable: yield x`, но эффективнее:

```python
def chain(*iterables):
    for it in iterables:
        yield from it   # передаём управление вложенному итератору

list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]
```

Рекурсивный обход дерева через `yield from`:

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # рекурсивно спускаемся
        else:
            yield item

list(flatten([1, [2, [3, 4]], [5, 6]]))   # [1, 2, 3, 4, 5, 6]
```

---

## Генераторные выражения

!!! quote "PEP 289 — Generator Expressions"
    *This PEP introduces generator expressions as a high performance, memory efficient generalization of list comprehensions. Many of the use cases do not need to have a full list created in memory. Instead, they only need to iterate over the elements one at a time.*

Синтаксис как у списковых включений, но в круглых скобках — результат ленивый генератор, а не список:

```python
# списковое включение — создаёт весь список сразу
squares_list = [x**2 for x in range(10)]       # list

# генераторное выражение — ленивый генератор
squares_gen = (x**2 for x in range(10))        # generator

print(type(squares_list))   # <class 'list'>
print(type(squares_gen))    # <class 'generator'>
```

!!! quote "PEP 289 — Generator Expressions"
    *Generator expressions are especially useful with functions like `sum()`, `min()`, and `max()` that reduce an iterable input to a single value.*

```python
# когда результат сразу передаётся в функцию — скобки не нужны дважды
total = sum(x**2 for x in range(1000))
maximum = max(len(line) for line in open("file.txt"))
any_negative = any(x < 0 for x in numbers)
```

### Когда список, а когда генератор

| Ситуация | Что использовать |
|---|---|
| Нужно обойти один раз | генератор |
| Нужно обойти несколько раз | список |
| Большой или бесконечный объём данных | генератор |
| Нужна индексация `[i]` | список |
| Передаёте в `sum`, `max`, `any`, `all` | генератор |
| Нужно знать длину заранее | список |

---

## itertools — стандартная библиотека для итерации

!!! quote "docs.python.org / itertools"
    *This module implements a number of iterator building blocks inspired by constructs from APL, Haskell, and SML. Each has been recast in a form suitable for Python. The module standardizes a core set of fast, memory efficient tools that are useful by themselves or in combination.*

`itertools` — набор генераторов для работы с итерируемыми объектами. Все они ленивые.

### Бесконечные итераторы

```python
from itertools import count, cycle, repeat

# count(start, step) — бесконечный счётчик
for i in count(10, 2):
    if i > 20: break
    print(i)   # 10, 12, 14, 16, 18, 20

# cycle(iterable) — бесконечный цикл по элементам
for i, x in zip(range(7), cycle("ABC")):
    print(x)   # A B C A B C A

# repeat(obj, times) — повторить объект
list(repeat(42, 3))   # [42, 42, 42]
```

### Комбинаторные итераторы

```python
from itertools import combinations, permutations, product

list(combinations("ABC", 2))    # [('A','B'), ('A','C'), ('B','C')]
list(permutations("ABC", 2))    # [('A','B'), ('A','C'), ('B','A'), ...]
list(product("AB", repeat=2))   # [('A','A'), ('A','B'), ('B','A'), ('B','B')]
```

### Цепочки и группировка

```python
from itertools import chain, groupby, islice, takewhile, dropwhile

# chain — объединить несколько итерируемых
list(chain([1, 2], [3, 4], [5]))   # [1, 2, 3, 4, 5]

# islice — срез ленивого итератора
list(islice(count(), 5))   # [0, 1, 2, 3, 4]

# takewhile / dropwhile — взять/пропустить пока условие истинно
list(takewhile(lambda x: x < 5, [1, 3, 5, 2, 7]))   # [1, 3]
list(dropwhile(lambda x: x < 5, [1, 3, 5, 2, 7]))   # [5, 2, 7]

# groupby — группировать по ключу (требует сортировки!)
data = [("a", 1), ("a", 2), ("b", 3), ("b", 4)]
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [('a', 1), ('a', 2)]
# b [('b', 3), ('b', 4)]
```

---

## Читаем реальный код — Django QuerySet

Django QuerySet — один из лучших примеров ленивых вычислений в реальной библиотеке.

```python
# это НЕ выполняет запрос к базе данных
queryset = Book.objects.filter(author="Tolstoy")

# и это тоже — просто добавляет условие
queryset = queryset.filter(pages__gte=200)

# запрос выполняется только здесь — при итерации
for book in queryset:
    print(book.title)

# или при явном вычислении
books = list(queryset)
count = queryset.count()
```

Откроем `django/db/models/query.py` — метод `__iter__`:

```python
def __iter__(self):
    self._fetch_all()
    return iter(self._result_cache)
```

QuerySet реализует `__iter__` — поэтому работает в `for`. `_fetch_all()` выполняет SQL только если кеш пуст — результат запоминается. Это не чистый генератор, но та же идея: вычисление откладывается до момента когда оно действительно нужно.

Метод `iterator()` даёт настоящее ленивое поведение без кеша — полезно для больших выборок:

```python
# не загружает всё в память — идеально для миллиона записей
for book in Book.objects.all().iterator():
    process(book)
```

---

## Домашнее задание

Создайте файл `hw05.py`. Сдача через PR, ветка: `hw05/фамилия`.

**1.** Напишите генераторную функцию `running_average()` которая принимает итерируемый объект чисел и на каждом шаге выдаёт текущее среднее. Например для `[1, 3, 5, 7]` должна выдавать `1.0, 2.0, 3.0, 4.0`.

**2.** Напишите генераторную функцию `read_in_chunks(iterable, size)` которая разбивает любой итерируемый объект на куски заданного размера. Например `list(read_in_chunks(range(10), 3))` → `[[0,1,2], [3,4,5], [6,7,8], [9]]`. Реализуйте без `itertools`.

**3.** Используя `itertools.groupby` напишите функцию `compress_runs(lst)` которая сжимает последовательные повторы в пары `(элемент, количество)`. Например `[1,1,1,2,2,3]` → `[(1,3), (2,2), (3,1)]`.
