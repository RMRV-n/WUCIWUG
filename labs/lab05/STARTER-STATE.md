# Исходные проверки ЛР5

Успешных проверок: **18**. Ожидаемых падений: **9**.

Не завершены использование переданных зависимостей, сборка и основной путь операции. Проверки вызывают разные конфигурации и ошибающегося исполнителя; ошибка не должна превращаться в успешный результат или повторную операцию.

Падения ниже связаны с конкретными требованиями [TASK.md](TASK.md). После обязательной части все они должны пройти. Бонус проверяется отдельно и не входит в эти числа.

## Новые последовательности и конфигурации

- `tests.test_progression::test_progression_dependency_error_does_not_debit_or_retry`
- `tests.test_progression::test_progression_extra_lab05`
- `tests.test_progression::test_progression_withdrawal_refusal_then_success`

## Предметный контракт и общий интерфейс

- `tests.test_contract::test_balance_changes_once_and_persists`
- `tests.test_contract::test_default_policy_refusal_does_not_debit`
- `tests.test_contract::test_dependency_failure_preserves_balance`
- `tests.test_contract::test_injection_copy_and_mandatory_funds`
- `tests.test_contract::test_policy_used_by_service`
- `tests.test_review_contract::test_review_wrong_policy_result_does_not_debit`

## Порядок проверки

Из корня проекта: `python check.py lab05`. Сначала прочитайте первый traceback и ожидаемый результат сценария. Не отключайте тесты, которые пока не проходят.

Ошибка импорта или установки не относится к заданию. Если исходный набор результатов отличается, сохраните вывод и сообщите преподавателю; не удаляйте решения и служебные файлы.
