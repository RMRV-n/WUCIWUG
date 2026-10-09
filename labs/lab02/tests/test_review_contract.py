import pytest
from decimal import Decimal
from datetime import date, datetime, timezone, timedelta
from app import api
from app.support.errors import DomainError


def assert_code(code, action):
    with pytest.raises(DomainError) as caught:
        action()
    assert caught.value.code == code

from app.support.types import money

from app.domain.account import Account
from app.domain.money import Money

def test_review_money_exactness_equality_and_read_only_fields():
    assert Money(Decimal("1.000"),"EUR") == money("1")
    assert money("1") != money("1","USD")
    assert_code("INVALID_AMOUNT",lambda:Money(1.0,"EUR"))
    amount = money("1")
    with pytest.raises((AttributeError,TypeError)): amount.amount = Decimal("2")
    with pytest.raises((AttributeError,TypeError)): amount.currency = "USD"

def test_review_closed_and_blocked_deposit_are_atomic():
    item = Account("A","C",money("0"))
    item.block()
    assert_code("ACCOUNT_BLOCKED",lambda:item.deposit(money("1")))
    assert item.balance == money("0")
    item.close()
    assert_code("ACCOUNT_CLOSED",lambda:item.deposit(money("1")))
    assert_code("INVALID_STATE",item.close)
    assert item.balance == money("0")
