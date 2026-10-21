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

def test_custom_code():
    from app.domain.account import Account
    from app.domain.withdrawal import MaximumWithdrawalRule
    rule=MaximumWithdrawalRule(money("1"),code="CUSTOM")
    assert rule.check(Account("A","C",money("10")),money("2")).code=="CUSTOM"
