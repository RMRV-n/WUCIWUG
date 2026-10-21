from abc import ABC, abstractmethod
from decimal import Decimal, localcontext
from app.support.types import CheckResult, result_code, decimal_value
from app.support.errors import DomainError
from app.domain.money import Money


class WithdrawalRule(ABC):
    """Абстрактный базовый класс для правил списания."""
    
    @abstractmethod
    def check(self, account, amount):
        raise NotImplementedError


class MaximumWithdrawalRule(WithdrawalRule):
    """Правило: сумма списания не должна превышать максимум."""
    
    def __init__(self, maximum, code="WITHDRAWAL_LIMIT_EXCEEDED"):
        if not isinstance(maximum, Money):
            raise DomainError("INVALID_CONFIG")
        self._maximum = maximum
        self._code = code

    def check(self, account, amount):
        try:
            amount.same_currency(self._maximum)
        except DomainError:
            raise DomainError("CURRENCY_MISMATCH")
        
        if amount.amount > self._maximum.amount:
            return CheckResult(False, self._code)
        
        return CheckResult(True)


class MinimumBalanceRule(WithdrawalRule):
    """Правило: после списания на счету должен остаться минимум reserve."""
    
    def __init__(self, reserve):
        if not isinstance(reserve, Money):
            raise DomainError("INVALID_CONFIG")
        self._reserve = reserve

    def check(self, account, amount):
        try:
            amount.same_currency(self._reserve)
        except DomainError:
            raise DomainError("CURRENCY_MISMATCH")
        
        with localcontext() as ctx:
            ctx.prec = 28
            remaining = account.balance.amount - amount.amount
        
        if remaining < self._reserve.amount:
            return CheckResult(False, "MINIMUM_BALANCE_REQUIRED")
        
        return CheckResult(True)