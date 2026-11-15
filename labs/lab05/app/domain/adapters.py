from app.domain.withdrawal import WithdrawalRule
from app.support.types import CheckResult, currency
from app.support.errors import DomainError

class LegacyWithdrawalAdapter(WithdrawalRule):
    def __init__(self, legacy, code="EUR"):
        self._legacy = legacy
        self._currency = currency(code)

    def check(self, account, amount):
        # 1. Проверяем валюту (обязательная проверка перед вызовом legacy)
        if amount.currency != self._currency:
            raise DomainError("CURRENCY_MISMATCH")
        
        # 2. Вызываем legacy-метод accepts() с суммой (Decimal)
        if not self._legacy.accepts(amount.amount):
            return CheckResult(False, "WITHDRAWAL_LIMIT_EXCEEDED")
        
        return CheckResult(True)