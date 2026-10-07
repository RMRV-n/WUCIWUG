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
        if not isinstance(amount, Money):
            raise DomainError("INVALID_AMOUNT")
        if amount.amount <= 0:
            raise DomainError("INVALID_AMOUNT")
        if amount.currency != self._balance.currency:
            raise DomainError("CURRENCY_MISMATCH")

    def check_withdrawal(self, amount):
        self._validate_amount(amount)
        if self.status != "ACTIVE":
            return CheckResult(False, "ACCOUNT_" + self.status)
        if amount > self._balance:
            return CheckResult(False, "INSUFFICIENT_FUNDS")
        return CheckResult(True, None)

    def withdraw(self, amount):
        result = self.check_withdrawal(amount)
        if not result.allowed:
            raise DomainError(result.code)
        self._balance = self._balance.subtract(amount)
        return self._balance

    def deposit(self, amount):
        self._validate_amount(amount)
        if self.status != "ACTIVE":
            raise DomainError("ACCOUNT_" + self.status)
        self._balance = self._balance.add(amount)
        return self._balance

    def balance_after_withdrawal(self, amount) -> Money:
        """Возвращает возможный остаток после снятия, но не меняет счёт."""
        result = self.check_withdrawal(amount)
        if not result.allowed:
            raise DomainError(result.code)
        return self._balance.subtract(amount)

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