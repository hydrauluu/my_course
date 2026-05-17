# Лекция 2. Последовательности и протокол итерации

> 📖 Документация: [Sequence Types](https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range) · [Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types) · [Data Model — __iter__](https://docs.python.org/3/reference/datamodel.html#object.__iter__) · [PEP 234 — Iterators](https://peps.python.org/pep-0234/)

---

## Последовательности

!!! quote "docs.python.org / stdtypes — Sequence Types"
    *There are three basic sequence types: lists, tuples, and range objects. Additional sequence types tailored for processing of binary data and text strings are described in dedicated sections.*

Последовательность — это упорядоченная коллекция объектов, доступная по целочисленному индексу начиная с нуля. Все встроенные последовательности поддерживают единый набор операций — __sequence protocol__.

### Общие операции над последовательностями

Любая последовательность `s` поддерживает:

| Операция | Результат |
|---|---|
| `s[i]` | i-й элемент |
| `s[i:j]` | срез от i до j |
| `s[i:j:k]` | срез с шагом k |
| `len(s)` | длина |
| `min(s)` | минимальный элемент |
| `max(s)` | максимальный элемент |
| `x in s` | True если x есть в s |
| `x not in s` | True если x нет в s |
| `s + t` | конкатенация |
| `s * n` | n копий s |
| `s.index(x)` | индекс первого вхождения x |
| `s.count(x)` | количество вхождений x |

```python
lst = [10, 20, 30, 40, 50]

print(lst[0])      # 10 — первый элемент
print(lst[-1])     # 50 — последний (отрицательные индексы с конца)
print(lst[1:3])    # [20, 30] — срез
print(lst[::2])    # [10, 30, 50] — каждый второй
print(30 in lst)   # True
```

### Изменяемые последовательности

`list` дополнительно поддерживает операции изменения:

```python
lst = [1, 2, 3]

lst[0] = 10           # замена элемента
lst.append(4)         # добавить в конец
lst.insert(1, 99)     # вставить по индексу
lst.pop()             # удалить и вернуть последний
lst.pop(0)            # удалить и вернуть по индексу
lst.remove(99)        # удалить первое вхождение значения
lst.reverse()         # развернуть на месте
del lst[0]            # удалить по индексу
del lst[1:3]          # удалить срез
```

### Срезы

Срез `s[i:j:k]` — мощный инструмент для работы с последовательностями. Все три параметра необязательны.

```python
s = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

s[2:7]      # [2, 3, 4, 5, 6] — от индекса 2 до 7 (не включая)
s[:3]       # [0, 1, 2] — с начала до 3
s[7:]       # [7, 8, 9] — от 7 до конца
s[:]        # копия всего списка
s[::-1]     # [9, 8, 7, ..., 0] — в обратном порядке
s[1::2]     # [1, 3, 5, 7, 9] — нечётные индексы
```

Отрицательные индексы считаются с конца:

```python
s[-1]       # 9 — последний
s[-3:]      # [7, 8, 9] — последние три
s[:-2]      # [0, 1, 2, ..., 7] — все кроме последних двух
```

!!! note "Как работает индексация"
    `s[-i]` эквивалентно `s[len(s) - i]`. То есть `s[-1]` это `s[len(s) - 1]` — последний элемент.

### Ссылки внутри контейнеров

Список хранит не объекты, а __ссылки__ на объекты. Это прямое следствие того что мы разбирали в лекции 0.

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a           # c — ещё одно имя для того же объекта

c.append(4)
print(a)        # [1, 2, 3, 4] — a тоже изменился, это один объект
print(b)        # [1, 2, 3] — b отдельный объект, не изменился
```

```python
lst = [[1, 2], [3, 4]]
copy = lst[:]   # поверхностная копия списка

copy.append([5, 6])
print(lst)      # [[1, 2], [3, 4]] — внешний список не изменился

copy[0].append(99)
print(lst)      # [[1, 2, 99], [3, 4]] — внутренний список изменился!
```

Срез `[:]` создаёт __поверхностную копию__ — новый список, но элементы внутри это те же самые объекты. Изменение вложенного изменяемого объекта затронет оба списка.

### Распаковка

Python позволяет распаковать любую последовательность в отдельные имена:

```python
a, b, c = [1, 2, 3]
print(a, b, c)   # 1 2 3

x, y = (10, 20)
first, *rest = [1, 2, 3, 4, 5]
print(first)     # 1
print(rest)      # [2, 3, 4, 5]

*start, last = [1, 2, 3, 4, 5]
print(start)     # [1, 2, 3, 4]
print(last)      # 5
```

Если количество имён не совпадает с количеством элементов — `ValueError`:

```python
a, b = [1, 2, 3]
# ValueError: too many values to unpack (expected 2)
```

Распаковка работает в том числе в `for`:

```python
pairs = [(1, "a"), (2, "b"), (3, "c")]

for num, letter in pairs:
    print(num, letter)
```

---

## Протокол итерации

В лекции 1 мы видели что `for` работает со списками, строками, словарями, `range`. Почему? Что у них общего?

Ответ — они все реализуют __протокол итерации__.

!!! quote "docs.python.org / stdtypes — Iterator Types"
    *Python supports a concept of iteration over containers. This is implemented using two distinct methods; these are used to allow user-defined classes to support iteration.*

Протокол состоит из двух уровней: __итерируемый объект__ и __итератор__.

### Итерируемый объект (Iterable)

Объект является итерируемым если у него есть метод `__iter__()`. Этот метод должен возвращать итератор.

!!! quote "docs.python.org / datamodel — object.__iter__"
    *This method is called when an iterator is required for a container. This method should return a new iterator object that can iterate over all the objects in the container.*

```python
lst = [1, 2, 3]
it = iter(lst)       # вызывает lst.__iter__()
print(type(it))      # <class 'list_iterator'>
```

`iter()` — встроенная функция которая вызывает `__iter__()` объекта.

### Итератор (Iterator)

Итератор — объект который реализует два метода:

- `__iter__()` — возвращает самого себя
- `__next__()` — возвращает следующий элемент. Когда элементы закончились — поднимает `StopIteration`

!!! quote "docs.python.org / stdtypes — Iterator Types"
    *The iterator objects themselves are required to support the following two methods, which together form the iterator protocol:*
    *`iterator.__iter__()` — Return the iterator object itself.*
    *`iterator.__next__()` — Return the next item from the iterator. If there are no further items, raise the StopIteration exception.*

```python
lst = [1, 2, 3]
it = iter(lst)

print(next(it))   # 1  — вызывает it.__next__()
print(next(it))   # 2
print(next(it))   # 3
print(next(it))   # StopIteration
```

`next()` — встроенная функция которая вызывает `__next__()`.

### Как работает for изнутри

Теперь можно понять что именно делает `for` — это не магия, а конкретная последовательность шагов:

```python
for x in obj:
    print(x)
```

Эквивалентно:

```python
it = iter(obj)          # вызывает obj.__iter__()
while True:
    try:
        x = next(it)    # вызывает it.__next__()
        print(x)
    except StopIteration:
        break           # StopIteration → цикл завершён
```

!!! quote "PEP 234 — Iterators"
    *The Python bytecode generated for for loops is changed to use new opcodes, GET_ITER and FOR_ITER, that use the iterator protocol rather than the sequence protocol to get the next value for the loop variable.*

Именно поэтому `for` работает с любым объектом у которого есть `__iter__`. Список, строка, словарь, `range`, файл, ваш собственный класс — всё что реализует протокол.

### Итерируемое vs итератор

Это __не одно и то же__, и разница важна.

__Итерируемое__ (`list`, `str`, `tuple`) — можно обойти несколько раз, каждый раз создаётся новый итератор:

```python
lst = [1, 2, 3]

for x in lst:
    print(x)    # 1, 2, 3

for x in lst:
    print(x)    # 1, 2, 3 — снова работает
```

__Итератор__ — одноразовый, хранит состояние текущей позиции:

```python
lst = [1, 2, 3]
it = iter(lst)

for x in it:
    print(x)    # 1, 2, 3

for x in it:
    print(x)    # ничего — итератор исчерпан
```

!!! quote "docs.python.org / stdtypes — Iterator Types"
    *Once an iterator's `__next__()` method raises StopIteration, it must continue to do so on subsequent calls. Implementations that do not obey this property are deemed broken.*

После того как итератор поднял `StopIteration` — он исчерпан навсегда.

### iter() с двумя аргументами

!!! quote "docs.python.org / functions — iter()"
    *If the second argument, sentinel, is given, then the first argument must be a callable object. The iterator created in this case will call callable with no arguments for each call to its `__next__()` method; if the value returned is equal to sentinel, StopIteration will be raised, otherwise the value will be returned.*

```python
# читать строки из файла пока не встретим пустую строку
with open("file.txt") as f:
    for line in iter(f.readline, ""):
        print(line)
```

---

## Собственный итератор

Понять протокол лучше всего написав его руками. Напишем итератор который считает от `start` до `stop`:

```python
class CountUp:
    def __init__(self, start, stop):
        self.current = start
        self.stop = stop

    def __iter__(self):
        return self          # итератор возвращает себя

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value


counter = CountUp(1, 5)

for n in counter:
    print(n)
# 1, 2, 3, 4
```

Обратите внимание: `__iter__` возвращает `self`. Это обязательное требование протокола — итератор должен быть итерируемым сам по себе, чтобы его можно было использовать в `for`.

```python
it = CountUp(1, 4)
print(next(it))   # 1
print(next(it))   # 2

for n in it:      # продолжаем с текущей позиции
    print(n)      # 3
```

### Протокол последовательности как альтернатива

!!! quote "docs.python.org / functions — iter()"
    *Without a second argument, the single argument must be a collection object which supports the iterable protocol (the `__iter__()` method), or it must support the sequence protocol (the `__getitem__()` method with integer arguments starting at 0).*

Есть и второй способ сделать объект итерируемым — реализовать `__getitem__()`. Python попробует вызывать его с индексами 0, 1, 2... пока не получит `IndexError`:

```python
class SimpleSeq:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, index):
        return self.data[index]   # IndexError если индекс за границей


s = SimpleSeq([10, 20, 30])

for x in s:
    print(x)   # 10, 20, 30
```

Это старый механизм (до PEP 234). В современном коде предпочитают `__iter__`.

---

## Полезные встроенные функции для итерации

Документация: [Built-in Functions](https://docs.python.org/3/library/functions.html)

### enumerate()

Возвращает пары `(индекс, элемент)`:

```python
seasons = ["весна", "лето", "осень", "зима"]

for i, season in enumerate(seasons):
    print(i, season)
# 0 весна
# 1 лето
# 2 осень
# 3 зима

for i, season in enumerate(seasons, start=1):
    print(i, season)
# 1 весна ...
```

### zip()

Объединяет несколько итерируемых объектов поэлементно. Останавливается на самом коротком:

```python
names = ["Alice", "Bob", "Carol"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
# Alice: 85
# Bob: 92
# Carol: 78
```

### reversed()

Возвращает итератор в обратном порядке. Работает с последовательностями (у которых есть `__len__` и `__getitem__`) или объектами с `__reversed__`:

```python
for x in reversed([1, 2, 3, 4]):
    print(x)   # 4, 3, 2, 1
```

### map() и filter()

Применяют функцию к каждому элементу итерируемого объекта. Возвращают __ленивые__ объекты — вычисление происходит по требованию:

```python
nums = [1, 2, 3, 4, 5]

doubled = map(lambda x: x * 2, nums)
print(list(doubled))    # [2, 4, 6, 8, 10]

evens = filter(lambda x: x % 2 == 0, nums)
print(list(evens))      # [2, 4]
```

### Списковые включения (list comprehension)

Компактный способ создать список через итерацию:

```python
# вместо
doubled = []
for x in range(10):
    doubled.append(x * 2)

# пишут
doubled = [x * 2 for x in range(10)]

# с условием
evens = [x for x in range(10) if x % 2 == 0]

# вложенное
matrix = [[i * j for j in range(3)] for i in range(3)]
```

---

## Домашнее задание

Создайте файл `hw02.py`. Сдача через PR, ветка: `hw02/фамилия`.

__1.__ Напишите собственный итератор `Fibonacci` который бесконечно генерирует числа Фибоначчи. Проверьте что он работает в `for` (с ограничением через `break`), и что `next()` можно вызывать вручную.

__2.__ Возьмите любой список и продемонстрируйте разницу между поверхностной копией `[:]` и оригиналом на вложенном изменяемом объекте — через `id()` и реальное изменение. Добавьте комментарии.

__3.__ Напишите функцию `my_zip(*iterables)` которая ведёт себя как встроенный `zip` — принимает несколько итерируемых объектов и возвращает итератор пар. Реализуйте как класс с `__iter__` и `__next__`.
