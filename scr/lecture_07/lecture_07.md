# Лекция 7. ООП — часть 2: наследование и исключения

> 📖 Документация: [Classes — Inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance) · [The Python 2.3 MRO](https://docs.python.org/3/howto/mro.html) · [Built-in Exceptions](https://docs.python.org/3/library/exceptions.html) · [super()](https://docs.python.org/3/library/functions.html#super)

---

## Наследование

!!! quote "docs.python.org / tutorial — Inheritance"
    *Of course, a derived class can override any methods of its base class. Because methods have no special privileges when calling other methods of the same object, a method of a base class that calls another method defined in the same base class may end up calling a method of a derived class that overrides it. (For C++ programmers: all methods in Python are effectively virtual.)*

Наследование — механизм при котором один класс (**подкласс**, **derived class**) получает атрибуты и методы другого класса (**базового**, **base class**).

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError("Подклассы должны реализовать speak()")

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"


class Dog(Animal):
    def speak(self):
        return f"{self.name} говорит: Гав!"


class Cat(Animal):
    def speak(self):
        return f"{self.name} говорит: Мяу!"


dog = Dog("Rex")
cat = Cat("Whiskers")

print(dog.speak())   # Rex говорит: Гав!
print(cat.speak())   # Whiskers говорит: Мяу!
print(repr(dog))     # Dog(name='Rex') — __repr__ унаследован из Animal
```

### isinstance и issubclass

```python
print(isinstance(dog, Dog))      # True
print(isinstance(dog, Animal))   # True — Dog является Animal
print(isinstance(dog, Cat))      # False

print(issubclass(Dog, Animal))   # True
print(issubclass(Dog, Cat))      # False
print(issubclass(Dog, Dog))      # True — класс является подклассом себя
```

### Все классы наследуют от object

!!! quote "docs.python.org / datamodel"
    *A class instance has a namespace implemented as a dictionary which is the first place in which attribute references are searched. When an attribute is not found there, and the instance's class has an attribute by that name, the search continues with the class attributes.*

В Python 3 все классы неявно наследуют от `object`. Именно оттуда берутся `__repr__`, `__str__`, `__hash__`, `__eq__` и другие методы по умолчанию:

```python
class Empty:
    pass

print(Empty.__bases__)    # (<class 'object'>,)
print(Empty.__mro__)      # (<class '__main__.Empty'>, <class 'object'>)
```

---

## super()

`super()` возвращает прокси-объект который делегирует вызовы методов следующему классу в MRO. Это правильный способ вызвать метод родительского класса.

```python
class Animal:
    def __init__(self, name):
        self.name = name


class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)   # вызываем __init__ родителя
        self.breed = breed       # добавляем свой атрибут

    def __repr__(self):
        return f"Dog(name={self.name!r}, breed={self.breed!r})"


dog = Dog("Rex", "Labrador")
print(dog)   # Dog(name='Rex', breed='Labrador')
```

Без `super().__init__(name)` атрибут `self.name` не был бы инициализирован — `Animal.__init__` не вызвался бы.

### Переопределение и расширение методов

```python
class Animal:
    def describe(self):
        return f"Я животное по имени {self.name}"


class Dog(Animal):
    def describe(self):
        base = super().describe()          # получаем результат родителя
        return f"{base}, порода {self.breed}"   # расширяем его


dog = Dog("Rex", "Labrador")
print(dog.describe())
# Я животное по имени Rex, порода Labrador
```

---

## MRO — Method Resolution Order

!!! quote "docs.python.org / howto / mro"
    *Given a class C in a complicated multiple inheritance hierarchy, it is a non-trivial task to specify the order in which methods are overridden. The list of the ancestors of a class C, including the class itself, ordered from the nearest ancestor to the furthest, is called the linearization of C. The Method Resolution Order (MRO) is the set of rules that construct the linearization.*

MRO — порядок в котором Python ищет метод при обращении к нему. Python использует алгоритм **C3-линеаризации**, который гарантирует:

- Подкласс всегда предшествует родителю
- Порядок базовых классов сохраняется
- Никаких противоречий в иерархии

### Одиночное наследование

```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")

class C(B):
    pass

obj = C()
obj.method()        # B — нашли в B раньше чем в A
print(C.__mro__)
# (<class 'C'>, <class 'B'>, <class 'A'>, <class 'object'>)
```

### Множественное наследование и Diamond Problem

```python
class Base:
    def method(self):
        print("Base")

class Left(Base):
    def method(self):
        print("Left")
        super().method()

class Right(Base):
    def method(self):
        print("Right")
        super().method()

class Child(Left, Right):
    def method(self):
        print("Child")
        super().method()


Child().method()
# Child
# Left
# Right
# Base
```

MRO для `Child`:

```python
print(Child.__mro__)
# (<class 'Child'>, <class 'Left'>, <class 'Right'>, <class 'Base'>, <class 'object'>)
```

C3 гарантирует что `Base.method()` вызовется **ровно один раз** — именно для этого `super()` работает через MRO, а не напрямую к родителю.

### Посмотреть MRO

```python
print(Child.__mro__)      # tuple — атрибут класса
print(Child.mro())        # list — метод класса
```

### Противоречивая иерархия

Если C3 не может построить непротиворечивый порядок — Python поднимает `TypeError` при определении класса:

```python
class A: pass
class B: pass
class C(A, B): pass
class D(B, A): pass

class E(C, D): pass
# TypeError: Cannot create a consistent MRO for bases A, B
```

`C` требует `A` перед `B`, `D` требует `B` перед `A` — противоречие.

---

## Исключения — это наследование в действии

Вернёмся к исключениям из лекции 0, теперь с пониманием ООП.

Все исключения — это классы. Иерархия исключений — это иерархия наследования:

```python
print(ZeroDivisionError.__mro__)
# (<class 'ZeroDivisionError'>,
#  <class 'ArithmeticError'>,
#  <class 'Exception'>,
#  <class 'BaseException'>,
#  <class 'object'>)
```

Именно поэтому `except ArithmeticError` перехватывает и `ZeroDivisionError`, и `OverflowError`, и `FloatingPointError` — это всё подклассы `ArithmeticError`.

### Собственные исключения

Правильный способ — наследоваться от подходящего встроенного исключения:

```python
class AppError(Exception):
    """Базовое исключение приложения."""
    pass


class ValidationError(AppError):
    """Ошибка валидации входных данных."""

    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class DatabaseError(AppError):
    """Ошибка работы с базой данных."""
    pass


class NotFoundError(DatabaseError):
    """Запись не найдена."""

    def __init__(self, model, pk):
        self.model = model
        self.pk = pk
        super().__init__(f"{model} с id={pk} не найден")
```

Использование:

```python
def get_user(user_id):
    if not isinstance(user_id, int):
        raise ValidationError("user_id", "должен быть целым числом")
    if user_id <= 0:
        raise ValidationError("user_id", "должен быть положительным")
    # ... работа с БД
    raise NotFoundError("User", user_id)


try:
    get_user("abc")
except ValidationError as e:
    print(f"Ошибка валидации поля '{e.field}': {e.message}")
except NotFoundError as e:
    print(f"Не найдено: {e}")
except AppError as e:
    print(f"Ошибка приложения: {e}")
```

### Иерархия перехватывает подклассы

```python
try:
    get_user(999)
except AppError:   # перехватит и NotFoundError, и ValidationError
    print("Любая ошибка приложения")
```

Более специфичные `except` должны идти **раньше** более общих — иначе общий перехватит всё:

```python
try:
    ...
except NotFoundError:    # сначала специфичное
    ...
except DatabaseError:    # потом общее
    ...
except AppError:         # потом ещё более общее
    ...
```

### try/except/else/finally

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Ошибка значения: {e}")
except (TypeError, AttributeError) as e:
    print(f"Ошибка типа: {e}")
else:
    # выполняется если исключения не было
    print(f"Успех: {result}")
finally:
    # выполняется всегда — с исключением или без
    cleanup()
```

`else` — часто упускаемая конструкция. Код в `else` выполняется только если `try` завершился без исключений. Это чище чем помещать код после `try/except`, потому что явно показывает: "это выполняется только при успехе".

### raise from — цепочки исключений

```python
def parse_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Неверный формат конфига: {path}") from e
```

`raise X from Y` создаёт **цепочку исключений** — оригинальное исключение сохраняется в `__cause__`. Traceback покажет оба:

```
ConfigError: Неверный формат конфига: config.json

The above exception was the direct cause of the following exception:
...
json.decoder.JSONDecodeError: ...
```

Это позволяет не терять информацию об исходной причине ошибки.

---

## Композиция vs наследование

Наследование — не единственный способ повторного использования кода. Часто **композиция** (объект содержит другой объект) предпочтительнее.

!!! quote "Принцип"
    Предпочитайте композицию наследованию, если не выполняется отношение **"является"** (is-a). Наследование — для отношения "является". Композиция — для отношения "содержит" или "использует".

```python
# Наследование — Dog является Animal ✓
class Dog(Animal):
    pass

# Плохое наследование — Engine не является Car ✗
class Car(Engine):
    pass

# Правильно — Car содержит Engine ✓
class Car:
    def __init__(self):
        self.engine = Engine()
        self.transmission = Transmission()
```

Пример — логирование:

```python
# Плохо — наследование ради переиспользования
class LoggedUserService(Logger):
    def get_user(self, uid): ...

# Хорошо — композиция
class UserService:
    def __init__(self, logger):
        self.logger = logger   # зависимость передаётся снаружи

    def get_user(self, uid):
        self.logger.info(f"Запрос пользователя {uid}")
        ...
```

Второй вариант легче тестировать (можно подменить логгер), не привязывает к конкретной реализации и не создаёт искусственного отношения наследования.

---

## Читаем реальный код — иерархия исключений Django

Откроем [django/core/exceptions.py](https://github.com/django/django/blob/main/django/core/exceptions.py):

```python
class ObjectDoesNotExist(Exception):
    """Базовое исключение для Model.DoesNotExist."""
    silent_variable_failure = True


class MultipleObjectsReturned(Exception):
    """Запрос вернул несколько объектов, хотя ожидался один."""
    pass


class ValidationError(Exception):
    """Ошибка валидации."""

    def __init__(self, message, code=None, params=None):
        super().__init__(message, code, params)
        # ... инициализация атрибутов
        self.message = message
        self.code = code
        self.params = params
```

Каждая модель Django автоматически получает свой вложенный класс `DoesNotExist`:

```python
# это происходит в метаклассе ModelBase (лекция 9)
class Book(Model):
    pass

# теперь доступно:
Book.DoesNotExist       # подкласс ObjectDoesNotExist
Book.MultipleObjectsReturned
```

Это позволяет писать:

```python
try:
    book = Book.objects.get(id=1)
except Book.DoesNotExist:
    # специфично для Book
    ...
except ObjectDoesNotExist:
    # перехватит DoesNotExist любой модели
    ...
```

---

## Домашнее задание

Создайте файл `hw07.py`. Сдача через PR, ветка: `hw07/фамилия`.

**1.** Постройте иерархию исключений для банковского приложения: `BankError` → `AccountError` (недостаточно средств, счёт заморожен) и `TransactionError` (неверная сумма, неверная валюта). Напишите функцию `transfer(amount, from_account, to_account)` которая поднимает разные исключения в разных ситуациях. Обработайте их с сохранением информации через `raise X from Y`.

**2.** Напишите три класса: `Shape` с методом `area()` который поднимает `NotImplementedError`, `Circle(Shape)` и `Rectangle(Shape)` с реализацией. Добавьте `__repr__`. Напишите функцию `total_area(shapes)` которая принимает список фигур и возвращает суммарную площадь — она должна работать с любым подклассом `Shape`.

**3.** Выведите и объясните в комментариях MRO для следующей иерархии: `A`, `B(A)`, `C(A)`, `D(B, C)`. Используйте `D.__mro__`. Напишите в каждом классе метод `greet()` который вызывает `super().greet()` — и покажите в каком порядке они вызываются при `D().greet()`.
