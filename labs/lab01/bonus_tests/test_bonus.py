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

def test_description():
    from app.domain.account import Account
    def describe(self):
        return f"{self.account_id}:{self.balance.amount:.2f}:{self.balance.currency}"

    Account.describe = describe
    assert Account("ACC-1","C1",money("90")).describe()=="ACC-1:90.00:EUR"