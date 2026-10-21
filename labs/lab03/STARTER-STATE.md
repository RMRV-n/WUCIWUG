# Исходные проверки ЛР3

Успешных проверок: **14**. Ожидаемых падений: **8**.

Не завершены общий интерфейс, алгоритмы исполнителей и основной метод сервиса. Поэтому один незаполненный метод может вызвать несколько падений — это не несколько независимых задач.

Падения ниже связаны с конкретными требованиями [TASK.md](TASK.md). После обязательной части все они должны пройти. Бонус проверяется отдельно и не входит в эти числа.

## Новые последовательности и конфигурации

- `tests.test_progression::test_progression_withdrawal_refusal_then_success`

## Предметный контракт и общий интерфейс

- `tests.test_contract::test_abc_is_abstract`
- `tests.test_contract::test_balance_changes_once_and_persists`
- `tests.test_contract::test_cap_boundary[500.01-False]`
- `tests.test_contract::test_default_policy_refusal_does_not_debit`
- `tests.test_contract::test_policy_used_by_service`
- `tests.test_contract::test_read_only_check`
- `tests.test_contract::test_reserve_boundary[50.01-False]`

## Порядок проверки

Из корня проекта: `python check.py lab03`. Сначала прочитайте первый traceback и ожидаемый результат сценария. Не отключайте тесты, которые пока не проходят.

Ошибка импорта или установки не относится к заданию. Если исходный набор результатов отличается, сохраните вывод и сообщите преподавателю; не удаляйте решения и служебные файлы.
