from app import api
from app.support.errors import DomainError
from app.support.types import money
from decimal import Decimal
import pytest

def error(code, action):
    with pytest.raises(DomainError) as exc:
        action()
    assert exc.value.code == code

from app.domain.account import Account

def preview_account():
    item = Account("A", "C", money("100"))
    assert hasattr(item, "balance_after_withdrawal"), "Реализуйте бонусный метод balance_after_withdrawal"
    return item

@pytest.mark.parametrize("amount,expected", [("30", "70"), ("100", "0")])
def test_bonus_preview_does_not_debit(amount, expected):
    item = preview_account()
    assert item.balance_after_withdrawal(money(amount)) == money(expected)
    assert item.balance == money("100")
    assert item.withdraw(money("30")) == money("70")
    assert item.balance_after_withdrawal(money("10")) == money("60")
    assert item.balance == money("70")

@pytest.mark.parametrize("amount,code", [("0", "INVALID_AMOUNT"), ("100.01", "INSUFFICIENT_FUNDS")])
def test_bonus_preview_refusal_is_atomic(amount, code):
    item = preview_account()
    error(code, lambda: item.balance_after_withdrawal(money(amount)))
    error("CURRENCY_MISMATCH", lambda: item.balance_after_withdrawal(money("1", "USD")))
    item.block()
    error("ACCOUNT_BLOCKED", lambda: item.balance_after_withdrawal(money("1")))
    assert item.balance == money("100")
