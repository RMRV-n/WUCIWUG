import pytest
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
from app import api
from app.support.errors import DomainError
from app.support.types import Repository, CheckResult, Money, money


def error(code, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == code


def invoke(service, method, *args, **kwargs):
    return api.call(service, method, *args, **kwargs)

def test_legacy_cap():
    from app.domain.account import Account
    from app.domain.adapters import LegacyWithdrawalAdapter
    class Legacy:
        def accepts(self,value):
            return value<=10
    rule=LegacyWithdrawalAdapter(Legacy())
    assert rule.check(Account("A","C",money("100")),money("10.01")).code=="WITHDRAWAL_LIMIT_EXCEEDED"
