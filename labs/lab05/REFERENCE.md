# Account: справка для ЛР5

Счёт хранит остаток в одной валюте. Деньги изменяются только после проверки суммы, состояния счёта и правил списания.

Здесь перечислены типы текущей работы. Что требуется реализовать и какие файлы можно менять, указано в [TASK.md](TASK.md).

## Предметные объекты и исполнители

| Тип и конструктор | Публичные действия и свойства | Файл |
|---|---|---|
| `Account(account_id, customer_id, balance)` | `account_id`, `customer_id`, `balance`, `status`, `check_withdrawal(amount)`, `withdraw(amount)`, `deposit(amount)`, `block()`, `close()` | `app/domain/account.py` |
| `LegacyWithdrawalAdapter(legacy, code='EUR')` | `check(account, amount)` | `app/domain/adapters.py` |
| `Money(amount, currency='EUR')` | `amount`, `currency`, `same_currency(other)`, `add(other)`, `subtract(other)` | `app/domain/money.py` |
| `WithdrawalRule()` | `check(account, amount)` | `app/domain/withdrawal.py` |
| `MaximumWithdrawalRule(maximum)` | `check(account, amount)` | `app/domain/withdrawal.py` |
| `MinimumBalanceRule(reserve)` | `check(account, amount)` | `app/domain/withdrawal.py` |

Свойства читаются без скобок. Поля объекта-значения не меняются присваиванием; результат операции создаётся отдельно. Для наследника без собственного конструктора показаны аргументы конструктора базового класса.

## Вызов сервиса

| Метод | Сигнатура |
|---|---|
| `__init__` | `AccountService(repository, rules=())` |
| `register` | `register(account)` |
| `get` | `get(account_id)` |
| `check` | `check(account_id, amount)` |
| `withdraw` | `withdraw(account_id, amount)` |
| `deposit` | `deposit(account_id, amount)` |
| `preview_withdrawals` | `preview_withdrawals(account_id, amounts)` |
| `allowed_amounts` | `allowed_amounts(account_id, amounts)` |

`app/api.py` — готовая внешняя граница; не изменяйте её. Вызов попадает в сервис из указанного модуля. Подробные примеры создания входных объектов находятся в открытых тестах текущей папки.

В `app/services/assembly.py` находятся стандартные конфигурации. Переданный объект сохраняется, а отсутствие обозначается `None`. Пустой список или словарь не равен отсутствию настройки. Копия контейнера не означает копирования исполнителей.

Сигнатура сборки: `build_service(repository=None, rules=None)`.

## Готовые результаты и ошибки

`DomainError` находится в `app/support/errors.py`; код доступен через `error.code`. В разрешённых методах используйте готовые проверки, а не новую иерархию исключений.

`CheckResult(True)` означает разрешение. `CheckResult(False, code)` означает отказ, а не изменение статуса объекта. Некорректный тип результата правила вызывает `INVALID_RESULT`. При записи или списании сервис преобразует предусмотренный отказ в `DomainError` до изменения данных.

`Money` хранит `Decimal` и валюту. Для учебных данных используются EUR и USD. Заданная сумма создаётся готовой `money("10", "EUR")`; арифметика выполняется готовыми методами Money. Курс и коэффициент не округляются как денежная сумма. В Account денежный модуль — `app/domain/money.py`, в остальных вариантах он предоставлен в `app/support/`.

## Проверка поведения

`tests/test_contract.py` и `tests/test_review_contract.py` проверяют предметные правила. `tests/test_progression.py` проверяет последовательности обращений и настройки текущей работы. Ни один результат теста не является командой менять защищённый API или тесты.

Ожидаемый стартовый результат — в [STARTER-STATE.md](STARTER-STATE.md). Проверка из корня проекта: `python check.py lab05`.
