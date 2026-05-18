# Лекция 1. Циклы и управление потоком

> 📖 Документация: [Compound statements](https://docs.python.org/3/reference/compound_stmts.html) · [More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html) · [Expressions — Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)

---

## Составные инструкции

Прежде чем переходить к циклам, нужно понять что такое составная инструкция в Python вообще.

!!! quote "docs.python.org / compound statements"
    *Compound statements contain (groups of) other statements; they affect or control the execution of those other statements in some way. In general, compound statements span multiple lines, although in simple incarnations a whole compound statement may be contained in one line.*

Составная инструкция — это конструкция которая содержит внутри себя другие инструкции и управляет их выполнением. К ним относятся `if`, `while`, `for`, `try`, `with`, `match`, `def`, `class`. Всё что мы разбираем в этой лекции — составные инструкции.

Каждая составная инструкция состоит из одного или нескольких **заголовков** и **тела** (suite). Заголовок заканчивается двоеточием, тело — блок с отступом:

```
заголовок:
    тело
    тело
[необязательный заголовок]:
    тело
```

---

## Условные инструкции

### Истинность объектов

В Python любой объект можно использовать как условие. Каждый объект либо истинный (`True`), либо ложный (`False`) в булевом контексте.

!!! quote "docs.python.org / stdtypes — Truth Value Testing"
    *Any object can be tested for truth value, for use in an if or while condition or as operand of the Boolean operations below. By default, an object is considered true unless its class defines either a `__bool__()` method that returns False or a `__len__()` method that returns zero.*

Ложными (`False`) считаются:

- `None` и `False`
- Нулевые числа: `0`, `0.0`, `0j`
- Пустые последовательности и коллекции: `""`, `[]`, `()`, `{}`, `set()`
- Объекты у которых `__bool__()` возвращает `False` или `__len__()` возвращает `0`

Всё остальное — истинно.

```python
if []:
    print("не выполнится")

if [0]:
    print("выполнится — список непустой, хотя внутри 0")

if "":
    print("не выполнится")

if "False":
    print("выполнится — непустая строка всегда True")
```

Это используется повсеместно в реальном коде вместо явной проверки на `None` или длину:

```python
# вместо
if len(items) > 0:
    ...

# пишут
if items:
    ...
```

### Short-circuit evaluation

Логические операторы `and` и `or` в Python работают по принципу короткого замыкания — вычисление останавливается как только результат определён.

!!! quote "docs.python.org / expressions — Boolean operations"
    *The expression `x and y` first evaluates x; if x is false, its value is returned; otherwise, y is evaluated and the resulting value is returned.*
    *The expression `x or y` first evaluates x; if x is true, its value is returned; otherwise, y is evaluated and the resulting value is returned.*

Важно: `and` и `or` возвращают **один из операндов**, а не `True`/`False`.

```python
print(0 or "default")    # "default" — 0 ложный, вернули правый
print(5 or "default")    # 5 — 5 истинный, до правого не дошли
print([] and [1, 2])     # [] — [] ложный, до правого не дошли
print([1] and [1, 2])    # [1, 2] — [1] истинный, вернули правый
```

Это не просто теория — такой паттерн встречается в реальном коде постоянно:

```python
name = user_input or "anonymous"   # если пустая строка — берём дефолт
config = env_config or default_config
```

---

## Цикл while

!!! quote "docs.python.org / compound statements — while"
    ```
while_stmt ::= "while" assignment_expression ":" suite
                   ["else" ":" suite]
    ```
    *This repeatedly tests the expression and, if it is true, executes the first suite; if the expression is false (which may be the first time it is tested) the suite of the else clause, if present, is executed and the loop terminates.*

`while` выполняет тело цикла пока условие истинно. Условие проверяется **перед каждой итерацией**, включая первую — если условие изначально ложно, тело не выполнится ни разу.

```python
n = 5
while n > 0:
    print(n)
    n -= 1
# 5, 4, 3, 2, 1
```

```python
n = -1
while n > 0:
    print(n)   # не выполнится ни разу
```

### Бесконечный цикл

`while True` — намеренно бесконечный цикл. Выход из него только через `break`, `return` или исключение.

```python
while True:
    command = input("> ")
    if command == "quit":
        break
    print(f"Выполняю: {command}")
```

Это не антипаттерн — в реальном коде такая конструкция встречается регулярно, например в серверах, event loop, CLI инструментах.

---

## Цикл for

!!! quote "docs.python.org / compound statements — for"
    ```
for_stmt ::= "for" target_list "in" starred_list ":" suite
                 ["else" ":" suite]
    ```
    *The for statement is used to iterate over the elements of a sequence (such as a string, tuple or list) or other iterable object. The expression list is evaluated once; it should yield an iterable object. An iterator is created for that iterable.*

`for` в Python принципиально отличается от `for` в C или Java. Это не счётчик — это обход **любого итерируемого объекта**. Что именно является итерируемым и почему — разберём в лекции 2. Сейчас главное: `for` работает с любым объектом который умеет отдавать элементы по одному.

```python
for char in "hello":
    print(char)       # h, e, l, l, o

for item in [1, 2, 3]:
    print(item)       # 1, 2, 3

for key in {"a": 1, "b": 2}:
    print(key)        # a, b
```

### range()

Для числовых последовательностей используется `range()` — он возвращает не список, а ленивый объект который генерирует числа по требованию.

```python
range(5)          # 0, 1, 2, 3, 4
range(2, 8)       # 2, 3, 4, 5, 6, 7
range(0, 10, 2)   # 0, 2, 4, 6, 8  (шаг 2)
range(10, 0, -1)  # 10, 9, 8, ..., 1  (шаг -1)
```

```python
for i in range(5):
    print(i)
```

!!! note ""
    `range()` не создаёт список в памяти. `range(1_000_000)` занимает столько же памяти что и `range(5)`. Это важно — к этому вернёмся в лекции про итераторы.

### Переменная цикла

Переменная цикла (`i`, `item`, `char` и т.д.) — это обычное имя, которое на каждой итерации начинает указывать на следующий объект из последовательности.

!!! quote "docs.python.org / compound statements — for"
    *The suite may assign to the variable(s) in the target list; this does not affect the next item assigned to it.*

```python
for i in range(5):
    print(i)
    i = 100    # переприсваивание не влияет на следующую итерацию
# 0, 1, 2, 3, 4
```

После окончания цикла переменная **остаётся в области видимости** со значением последнего элемента:

```python
for i in range(5):
    pass

print(i)   # 4 — переменная доступна после цикла
```

Если последовательность пустая — переменная не создаётся вообще:

```python
for i in []:
    pass

print(i)   # NameError: name 'i' is not defined
```

### Нижнее подчёркивание как имя

Если значение переменной цикла не нужно — по соглашению используют `_`:

```python
for _ in range(5):
    print("hello")   # просто 5 раз
```

Это не синтаксис языка, а соглашение — `_` это обычное имя. Но оно сигнализирует читателю кода: *"значение здесь не используется намеренно"*.

---

## break и continue

!!! quote "docs.python.org / tutorial — break and continue"
    *The break statement, like in C, breaks out of the innermost enclosing for or while loop. The continue statement, also borrowed from C, continues with the next iteration of the loop.*

### break

`break` немедленно завершает **ближайший** цикл. Если циклы вложены — прерывается только внутренний.

```python
for i in range(10):
    if i == 5:
        break
    print(i)
# 0, 1, 2, 3, 4
```

```python
for i in range(3):
    for j in range(3):
        if j == 1:
            break        # прерывает только внутренний цикл
        print(i, j)
# 0 0
# 1 0
# 2 0
```

### continue

`continue` пропускает оставшуюся часть текущей итерации и переходит к следующей. В `while` — возвращается к проверке условия. В `for` — переходит к следующему элементу.

```python
for i in range(10):
    if i % 2 == 0:
        continue      # пропускаем чётные
    print(i)
# 1, 3, 5, 7, 9
```

---

## else у циклов

Это одна из особенностей Python которая часто удивляет — у `for` и `while` есть необязательная ветка `else`.

!!! quote "docs.python.org / tutorial — else clauses on loops"
    *If the loop finishes without executing the break, the else clause executes. In a for loop, the else clause is executed after the loop finishes its final iteration, that is, if no break occurred. In a while loop, it's executed after the loop's condition becomes false. In either kind of loop, the else clause is not executed if the loop was terminated by a break.*

Ветка `else` выполняется если цикл завершился **нормально** — то есть без `break`. Если был `break` — `else` пропускается.

```python
for i in range(10):
    if i == 5:
        break
else:
    print("break не случился")   # не выполнится
```

```python
for i in range(10):
    if i == 99:      # условие никогда не выполнится
        break
else:
    print("break не случился")   # выполнится
```

Классический паттерн — поиск элемента:

```python
target = 7
for i in range(10):
    if i == target:
        print(f"Нашли {target}")
        break
else:
    print(f"{target} не найден")
```

Без `else` пришлось бы заводить флаговую переменную:

```python
found = False
for i in range(10):
    if i == target:
        found = True
        break

if not found:
    print(f"{target} не найден")
```

`else` делает намерение явным — ветка выполняется именно тогда когда `break` не сработал.

!!! warning "Важно"
    `break` в теле цикла завершает цикл **без** выполнения `else`. Это же поведение: `return` и выброс исключения из тела цикла тоже пропускают `else`.

---

## Вложенные циклы и читаемость

Вложенные циклы быстро становятся нечитаемыми. В реальном коде глубокое вложение почти всегда сигнал что стоит вынести внутренний цикл в отдельную функцию.

```python
# три уровня — уже сложно читать
for i in range(n):
    for j in range(m):
        for k in range(p):
            ...
```

Как читать вложенные циклы в чужом коде: сначала понять что делает самый внешний, потом внутренний. Не пытаться держать в голове все уровни одновременно.

---

## Как читать циклы в реальном коде

Открываем документацию Python — раздел [Built-in Functions](https://docs.python.org/3/library/functions.html). Смотрим на `enumerate()`:

```python
enumerate(iterable, start=0)
```

Возвращает объект который отдаёт пары `(индекс, элемент)`. Типичное использование:

```python
seasons = ["весна", "лето", "осень", "зима"]

for i, season in seasons:      # TypeError — что здесь не так?
    print(i, season)
```

Запустите — получите исключение. Читайте его внимательно. Потом исправьте:

```python
for i, season in enumerate(seasons):
    print(i, season)
# 0 весна
# 1 лето
# ...
```

Здесь работает **распаковка** — каждый элемент который отдаёт `enumerate` это кортеж `(i, season)`, и Python автоматически раскладывает его по двум именам. К этому вернёмся в лекции 2.

---

## Домашнее задание

Создайте файл `hw01.py`. Сдача через PR, ветка: `hw01/фамилия`.

**1.** Напишите цикл который выводит все числа от 1 до 100 кроме кратных 3. Используйте `continue`.

**2.** Напишите функцию `find_first(lst, predicate)` которая принимает список и функцию-предикат, и возвращает первый элемент для которого предикат возвращает `True`. Если такого элемента нет — возвращает `None`. Используйте `for/else`.

**3.** Напишите код который вызывает `NameError` из-за того что переменная цикла не была создана (цикл по пустой последовательности). Оберните в `try/except`, выведите текст исключения.
