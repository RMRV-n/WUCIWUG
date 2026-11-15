from app.support.types import CheckResult, checked
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


class MaximumShareRule(WithdrawalRule):
    def __init__(self, share=Decimal("0.50")):
        decimal_value(share, "INVALID_CONFIG")
        if not 0 < share <= 1:
            raise DomainError("INVALID_CONFIG")
        self._share = share

    def check(self, account, amount):
        amount.same_currency(account.balance)
        limit = account.balance.amount * self._share
        if amount.amount > limit:
            return CheckResult(False, "WITHDRAWAL_SHARE_EXCEEDED")
        return CheckResult(True)


class WithdrawalRuleGroup(WithdrawalRule):
    """Последовательность правил: первый отказ, без изменения входных объектов."""

    def __init__(self, rules):
        self._rules = tuple(rules)
        for rule in self._rules:
            if not isinstance(rule, WithdrawalRule):
                raise DomainError("INVALID_CONFIG")

    def check(self, account, amount):
        for rule in self._rules:
            result = rule.check(account, amount)
            if not isinstance(result, CheckResult):
                raise DomainError("INVALID_RESULT")
            if not result.allowed:
                return result
        return CheckResult(True)


class MinimumWithdrawalRule(WithdrawalRule):
    def __init__(self, minimum):
        if not isinstance(minimum, Money) or minimum.amount <= 0:
            raise DomainError("INVALID_CONFIG")
        self._minimum = minimum

    def check(self, account, amount):
        amount.same_currency(self._minimum)
        if amount.amount < self._minimum.amount:
            return CheckResult(False, "WITHDRAWAL_TOO_SMALL")
        return CheckResult(True)