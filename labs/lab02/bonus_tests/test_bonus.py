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

def test_close_composed_invariant():
    from app.domain.account import Account
    item=Account("A","C",money("1"))
    error("NONZERO_BALANCE",item.close)
    item.withdraw(money("1"))
    item.close()
    error("ACCOUNT_CLOSED",lambda:item.deposit(money("1")))
