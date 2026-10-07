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
        pass  # ЛР2: сумма и валюта

    def check_withdrawal(self, amount):
        self._validate_amount(amount)
        if self.status != "ACTIVE":
            return CheckResult(False, "ACCOUNT_" + self.status)
        return CheckResult(True)

    def withdraw(self, amount):
        result = self.check_withdrawal(amount)
        if not result.allowed:
            raise DomainError(result.code)
        self._balance = self.balance.subtract(amount)
        return self.balance

    def deposit(self, amount):
        self._validate_amount(amount)
        if self.status != "ACTIVE":
            raise DomainError("ACCOUNT_" + self.status)
        self._balance = self.balance.add(amount)
        return self.balance

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
