# ЛР1: поля, конструктор и служебные проверки даны преподавателем.
# Завершите отмеченные методы; API пока использует старые функции.
from app.support.types import identifier, positive, CheckResult
from app.support.errors import DomainError
from app.domain.money import Money, money


class Account:
    def __init__(self, account_id, customer_id, balance):
        self._account_id = identifier(account_id)
        self._customer_id = identifier(customer_id)
        if not isinstance(balance, Money):
            raise DomainError("INVALID_AMOUNT")
        self._balance = balance
        self._status = "ACTIVE"

    @property
    def account_id(self):
        return self._account_id

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def balance(self):
        return self._balance

    @property
    def status(self):
        return self._status

    def _validate_amount(self, amount):
        positive(amount)
        self.balance.same_currency(amount)

    def check_withdrawal(self, amount):
        self._validate_amount(amount)
        if self.status != "ACTIVE":
            return CheckResult(False, "ACCOUNT_" + self.status)
        if amount.amount > self.balance.amount:
            return CheckResult(False, "INSUFFICIENT_FUNDS")
        return CheckResult(True)

    def withdraw(self, amount):
        raise NotImplementedError("ЛР1: завершите Account.withdraw")

    def deposit(self, amount):
        raise NotImplementedError("ЛР1: завершите Account.deposit")

    def block(self):
        if self.status != "ACTIVE":
            raise DomainError("INVALID_STATE")
        self._status = "BLOCKED"

    def close(self):
        if self.status not in ("ACTIVE", "BLOCKED"):
            raise DomainError("INVALID_STATE")
        if self.balance.amount != 0:
            raise DomainError("NONZERO_BALANCE")
        self._status = "CLOSED"
