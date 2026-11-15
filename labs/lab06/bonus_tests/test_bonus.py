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

def test_can_close_is_read_only():
    from app.domain.account import Account
    item=Account("A","C",money("0"))
    assert item.can_close()
    assert item.status=="ACTIVE"
    item.close()
    assert not item.can_close()
