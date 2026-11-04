import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from app import api
from app.support.errors import DomainError


def code(expected, operation):
    with pytest.raises(DomainError) as caught:
        operation()
    assert caught.value.code == expected

from app.domain.account import Account
from app.domain.money import money

def test_progression_withdrawal_refusal_then_success():
    service = api.create()
    account = Account("A", "C", money("200"))
    service.register(account)
    assert service.withdraw("A", money("30")) == money("170")
    code("INSUFFICIENT_FUNDS", lambda: service.withdraw("A", money("171")))
    assert account.balance == money("170")
    assert service.withdraw("A", money("20")) == money("150")
