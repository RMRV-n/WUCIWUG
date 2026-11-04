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

def test_deposit_delegates(monkeypatch):
    from app.domain.account import Account
    item=Account("A","C",money("10"))
    service=api.create()
    service.register(item)
    calls=[]
    original=Account.deposit
    def deposit(self,amount):
        calls.append(amount)
        return original(self,amount)
    monkeypatch.setattr(Account,"deposit",deposit)
    service.deposit("A",money("1"))
    assert calls==[money("1")]
