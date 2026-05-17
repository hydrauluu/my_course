# Лекция 4. Множества и словари

> 📖 Документация: [Mapping Types — dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) · [Set Types — set, frozenset](https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset) · [Data Model — __hash__](https://docs.python.org/3/reference/datamodel.html#object.__hash__)

---

## Хеш — основная идея

Прежде чем говорить о словарях и множествах, нужно понять что такое хеш. Именно на нём держится всё.

!!! quote "docs.python.org / datamodel — object.__hash__"
    *An object is hashable if it has a hash value which never changes during its lifetime (it needs a `__hash__()` method), and can be compared to other objects (it needs an `__eq__()` method). Hashable objects which compare equal should have the same hash value.*

Хеш — это целое число, которое вычисляется из содержимого объекта. Ключевые свойства:

- __Детерминированность__ — один и тот же объект всегда даёт одинаковый хеш
- __Быстрота__ — вычисляется за O(1) независимо от размера объекта
- __Компактность__ — всегда целое число

```python
print(hash("hello"))    # например: -3556844948564683008
print(hash(42))         # 42
print(hash((1, 2, 3)))  # 2528502973977326415

print(hash([1, 2, 3]))  # TypeError: unhashable type: 'list'
```

Список не хешируем — потому что он изменяемый. Если бы список изменился после того как его добавили в словарь как ключ, найти его стало бы невозможно.

!!! quote "docs.python.org / stdtypes — Immutable Sequence Types"
    *The only operation that immutable sequence types generally implement that is not also implemented by mutable sequence types is support for the `hash()` built-in. This support allows immutable sequences, such as tuple instances, to be used as dict keys and stored in set and frozenset instances. Attempting to hash an immutable sequence that contains unhashable values will result in TypeError.*

```python
hash((1, 2, 3))        # OK — tuple хешируем
hash((1, [2, 3]))      # TypeError — внутри изменяемый объект
```

### Как работает хеш-таблица

Dict и set реализованы как __хеш-таблицы__. При добавлении элемента Python:

1. Вычисляет `hash(key)`
2. По хешу определяет __слот__ (позицию в таблице) — `hash(key) % размер_таблицы`
3. Кладёт значение в этот слот

При поиске — то же самое: вычислить хеш, найти слот, проверить. Это даёт O(1) для операций `in`, `[]`, `.get()` независимо от размера словаря.

```python
# список — поиск O(n), нужно пройти все элементы
lst = list(range(1_000_000))
1_000_000 in lst   # медленно

# словарь / множество — поиск O(1)
d = {i: i for i in range(1_000_000)}
1_000_000 in d     # мгновенно
```

---

## Словарь (dict)

!!! quote "docs.python.org / stdtypes — Mapping Types"
    *A mapping object maps hashable values to arbitrary objects. Mappings are mutable objects. There is currently only one standard mapping type, the dictionary.*

    *A dictionary's keys are almost arbitrary values. Values that are not hashable, that is, values containing lists, dictionaries or other mutable types (that are compared by value rather than by object identity) may not be used as keys.*

Словарь — это не "список пар ключ-значение". Это __отображение__: структура данных которая по ключу мгновенно возвращает значение.

### Создание

```python
# литерал
d = {"name": "Alice", "age": 30}

# dict() из пар
d = dict([("name", "Alice"), ("age", 30)])

# dict() из именованных аргументов
d = dict(name="Alice", age=30)

# словарное включение
d = {i: i**2 for i in range(5)}   # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# пустой
d = {}
d = dict()
```

### Основные операции

```python
d = {"name": "Alice", "age": 30, "city": "Moscow"}

# доступ по ключу
print(d["name"])       # Alice
print(d["missing"])    # KeyError: 'missing'

# безопасный доступ
print(d.get("name"))          # Alice
print(d.get("missing"))       # None
print(d.get("missing", "?"))  # ? — дефолтное значение

# добавление и изменение
d["email"] = "alice@example.com"
d["age"] = 31

# удаление
del d["city"]
popped = d.pop("age")          # удалить и вернуть значение
d.pop("missing", None)         # не упадёт если ключа нет

# проверка наличия ключа
"name" in d      # True
"missing" in d   # False

# длина
len(d)   # количество пар
```

### Порядок в словаре

Начиная с Python 3.7 словари __гарантированно__ сохраняют порядок вставки — это часть спецификации языка, а не деталь реализации.

```python
d = {}
d["b"] = 2
d["a"] = 1
d["c"] = 3

print(list(d.keys()))   # ['b', 'a', 'c'] — порядок вставки
```

### Итерация

```python
d = {"name": "Alice", "age": 30}

# по ключам (по умолчанию)
for key in d:
    print(key)

# по значениям
for value in d.values():
    print(value)

# по парам
for key, value in d.items():
    print(f"{key}: {value}")
```

!!! quote "docs.python.org / stdtypes — Dictionary view objects"
    *The objects returned by `dict.keys()`, `dict.values()` and `dict.items()` are view objects. They provide a dynamic view on the dictionary's entries, which means that when the dictionary changes, the view reflects these changes.*

`d.keys()`, `d.values()`, `d.items()` — это __представления__ (views), а не копии. Они отражают текущее состояние словаря:

```python
d = {"a": 1, "b": 2}
keys = d.keys()

print(keys)   # dict_keys(['a', 'b'])
d["c"] = 3
print(keys)   # dict_keys(['a', 'b', 'c']) — представление обновилось
```

### Полезные методы

```python
d = {"a": 1, "b": 2}

# обновить из другого словаря
d.update({"c": 3, "a": 99})   # a перезапишется
print(d)   # {'a': 99, 'b': 2, 'c': 3}

# получить или установить дефолт
d.setdefault("d", 0)    # если 'd' нет — добавить с 0; вернуть значение
d.setdefault("a", 0)    # 'a' уже есть — ничего не менять

# слияние словарей (Python 3.9+)
merged = d | {"e": 5}    # новый словарь
d |= {"f": 6}            # обновить на месте
```

### Ключи — любые хешируемые объекты

```python
# числа
d = {1: "one", 2: "two", 1.0: "one point zero"}
print(d)   # {1: 'one point zero', 2: 'two'} — 1 и 1.0 один ключ!

# кортежи
coords = {(0, 0): "origin", (1, 0): "right", (0, 1): "up"}
print(coords[(1, 0)])   # right

# вызов с распаковкой кортежа
print(coords[1, 0])     # right — то же самое
```

Числа `1` и `1.0` равны (`1 == 1.0`) и имеют одинаковый хеш — поэтому они считаются одним ключом.

### defaultdict и Counter

В стандартной библиотеке есть полезные расширения словаря:

```python
from collections import defaultdict, Counter

# defaultdict — автоматически создаёт дефолтное значение
dd = defaultdict(list)
dd["fruits"].append("apple")    # не KeyError, list() вызывается автоматически
dd["fruits"].append("banana")
print(dd)   # defaultdict(<class 'list'>, {'fruits': ['apple', 'banana']})

# Counter — подсчёт элементов
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
c = Counter(words)
print(c)                    # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(c.most_common(2))     # [('apple', 3), ('banana', 2)]
```

---

## Множество (set)

!!! quote "docs.python.org / stdtypes — Set Types"
    *A set object is an unordered collection of distinct hashable objects. Common uses include membership testing, removing duplicates from a sequence, and computing mathematical operations such as intersection, union, difference, and symmetric difference.*

Множество — неупорядоченная коллекция __уникальных__ хешируемых объектов. Без дубликатов, без индексации, без порядка.

### Создание

```python
s = {1, 2, 3, 4, 5}
s = set([1, 2, 2, 3, 3])   # {1, 2, 3} — дубликаты убраны
s = set("hello")            # {'h', 'e', 'l', 'o'} — уникальные символы
s = set()                   # пустое множество — НЕ {}, {} это пустой dict!
```

### Основные операции

```python
s = {1, 2, 3}

s.add(4)        # добавить элемент
s.remove(2)     # удалить, KeyError если нет
s.discard(99)   # удалить, не падает если нет

2 in s          # False — проверка за O(1)
len(s)          # количество элементов
```

### Математические операции

```python
a = {1, 2, 3, 4, 5}
b = {3, 4, 5, 6, 7}

a | b           # объединение: {1, 2, 3, 4, 5, 6, 7}
a & b           # пересечение: {3, 4, 5}
a - b           # разность: {1, 2}
a ^ b           # симметричная разность: {1, 2, 6, 7}

a.issubset(b)      # является ли a подмножеством b
a.issuperset(b)    # является ли a надмножеством b
a.isdisjoint(b)    # нет ли общих элементов
```

### Типичные применения

__Удаление дубликатов:__

```python
lst = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(lst))
print(unique)   # [1, 2, 3, 4] — порядок не гарантирован
```

__Быстрая проверка принадлежности:__

```python
valid_statuses = {"active", "pending", "suspended"}

def is_valid(status):
    return status in valid_statuses   # O(1) вместо O(n) для списка
```

### frozenset

Неизменяемая версия множества — хешируема, может быть ключом словаря или элементом другого множества:

```python
fs = frozenset([1, 2, 3])
fs.add(4)   # AttributeError — frozenset не изменяемый

d = {frozenset([1, 2]): "pair"}   # OK — frozenset хешируем
```

---

## Точки как цепочки ссылок

Вернёмся к тому что мы знаем об объектах и ссылках — и посмотрим на атрибутный доступ через точку.

Когда вы пишете `a.b.c.d` — Python последовательно разрешает каждое имя:

1. Найти объект по имени `a`
2. Найти атрибут `b` у этого объекта — получить новый объект
3. Найти атрибут `c` у него — ещё один объект
4. Найти атрибут `d` у него — результат

Это буквально цепочка разыменований ссылок. Каждая точка — это переход по ссылке к следующему объекту.

```python
import os
print(os.path.sep)   # разберём что здесь происходит
```

- `os` — модуль, объект типа `module`
- `os.path` — атрибут `path` модуля `os`, сам является модулем
- `os.path.sep` — атрибут `sep` модуля `path`, строка с разделителем пути

Каждый шаг — обращение к атрибуту объекта. Никакой магии.

### Атрибуты хранятся в __dict__

У большинства объектов атрибуты хранятся во внутреннем словаре `__dict__`:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.__dict__)   # {'x': 1, 'y': 2}
```

Когда вы пишете `p.x` — Python смотрит в `p.__dict__["x"]`. Доступ по атрибуту — это в конечном счёте обращение к словарю.

---

## Читаем реальный код — Django ORM

Откроем реальный код и посмотрим как словари и хеши работают в практике.

В Django, когда вы пишете:

```python
Book.objects.filter(author="Tolstoy")
```

Вот что происходит внутри `filter()` — упрощённо:

```python
# django/db/models/query.py
def filter(self, *args, **kwargs):
    return self._filter_or_exclude(False, args, kwargs)

def _filter_or_exclude(self, negate, args, kwargs):
    clone = self._chain()
    # kwargs это словарь {'author': 'Tolstoy'}
    # каждая пара ключ-значение — это условие фильтрации
    clone.query.add_q(Q(*args, **kwargs))
    return clone
```

`**kwargs` — словарь, который Django использует чтобы динамически строить SQL запросы. Ключи словаря — имена полей и операторы через `__` (`author`, `author__startswith`, `created__gte`).

```python
# все эти вызовы передают kwargs разной формы
Book.objects.filter(author="Tolstoy")
Book.objects.filter(author__startswith="Tol")
Book.objects.filter(pages__gte=200, author="Tolstoy")
```

Django разбирает ключи словаря строковыми методами — разбивает по `__`, определяет поле и оператор, строит SQL. Словарь здесь — основной способ передать произвольный набор условий.

---

## Домашнее задание

Создайте файл `hw04.py`. Сдача через PR, ветка: `hw04/фамилия`.

__1.__ Напишите функцию `word_count(text)` которая принимает строку и возвращает словарь где ключи — слова, значения — количество вхождений. Реализуйте двумя способами: через обычный `dict` с `.get()` и через `defaultdict`. Проверьте что результаты совпадают.

__2.__ Дан список списков, например `[[1, 2], [3, 4], [1, 5], [2, 4]]`. Напишите функцию которая группирует пары по первому элементу и возвращает словарь `{первый_элемент: [все вторые элементы]}`. Например: `{1: [2, 5], 2: [4], 3: [4]}`.

__3.__ Напишите функцию `find_duplicates(lst)` которая возвращает множество элементов которые встречаются в списке более одного раза. Используйте два множества — для уже встреченных и для дубликатов. Проверьте что `in` для множества работает быстрее чем для списка — сравните через `time.time()` на большом наборе данных.
