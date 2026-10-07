# Проверка исходного кода

Успешных обязательных проверок: **8**. С ошибками: **5**.

Эти ошибки связаны с заданием. После выполнения обязательной части все проверки должны пройти.

## Проверки, которые пока не проходят

- `tests.test_contract::test_full_balance_and_overdraft_boundary`
- `tests.test_contract::test_money_rejects_invalid_values[-1]`
- `tests.test_contract::test_money_rejects_invalid_values[1.001]`
- `tests.test_contract::test_zero_and_currency_are_not_valid_operations[deposit]`
- `tests.test_contract::test_zero_and_currency_are_not_valid_operations[withdraw]`

Если список отличается или тесты не запускаются из-за ошибки установки или импорта, сообщите преподавателю. Не отключайте проверки.
