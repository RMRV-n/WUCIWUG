from abc import ABC, abstractmethod
from decimal import Decimal, localcontext
from app.support.types import CheckResult, result_code, decimal_value
from app.support.errors import DomainError
from app.domain.money import Money


class WithdrawalRule(ABC):
    @abstractmethod
    def check(self, account, amount):
        raise NotImplementedError


class MaximumWithdrawalRule(WithdrawalRule):
    def __init__(self, maximum):
        if not isinstance(maximum, Money):
            raise DomainError("INVALID_CONFIG")
        self._maximum = maximum

    def check(self, account, amount):
        amount.same_currency(self._maximum)
        if amount.amount > self._maximum.amount:
            return CheckResult(False, "WITHDRAWAL_LIMIT_EXCEEDED")
        return CheckResult(True)


class MinimumBalanceRule(WithdrawalRule):
    def __init__(self, reserve):
        if not isinstance(reserve, Money):
            raise DomainError("INVALID_CONFIG")
        self._reserve = reserve

    def check(self, account, amount):
        amount.same_currency(self._reserve)
        with localcontext() as ctx:
            ctx.prec = 28
            remaining = account.balance.amount - amount.amount
        if remaining < self._reserve.amount:
            return CheckResult(False, "MINIMUM_BALANCE_REQUIRED")
        return CheckResult(True)
