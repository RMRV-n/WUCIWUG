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

from app.domain.withdrawal import WithdrawalRule
from app.services.account_service import AccountService
from app.support.types import Repository, CheckResult

def test_progression_dependency_error_does_not_debit_or_retry():
    calls = []
    class Once(WithdrawalRule):
        def check(self, account, amount):
            calls.append(amount)
            if len(calls) == 1: raise DomainError("TEMPORARY")
            return CheckResult(True)
    rules = [Once()]
    repo = Repository("account_id")
    item = repo.add(Account("A", "C", money("100")))
    service = AccountService(repo, rules)
    rules.clear()
    code("TEMPORARY", lambda: service.withdraw("A", money("10")))
    assert len(calls) == 1 and item.balance == money("100")
    assert service.withdraw("A", money("10")) == money("90") and len(calls) == 2

from app.domain.account import Account
from app.domain.money import money

def test_progression_extra_lab05():
    service = api.create()
    account = Account("A", "C", money("200"))
    service.register(account)
    rows = service.preview_withdrawals("A", (money("20"), money("180")))
    assert rows[0][1].allowed and rows[0][2] == money("180")
    assert not rows[1][1].allowed and rows[1][2] is None
    assert service.allowed_amounts("A", (money("20"), money("180"))) == (money("20"),)
    assert account.balance == money("200")
