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

def account(balance="100", key="ACC-1"):
    return api.make(key, "C1", money(balance))

def prepared():
    service = api.create()
    item = account()
    invoke(service,"register",item)
    return service,item

def test_balance_changes_once_and_persists():
    service,item=prepared()
    invoke(service,"register",account("200","ACC-2"))
    assert invoke(service,"deposit","ACC-1",money("20")) == money("120")
    assert invoke(service,"withdraw","ACC-1",money("30")) == money("90")
    assert api.view(invoke(service,"get","ACC-1"))["balance"] == money("90")
    assert api.view(invoke(service,"get","ACC-2"))["balance"] == money("200")

def test_read_only_check():
    service,item=prepared()
    before=api.view(item)
    assert invoke(service,"check","ACC-1",money("10")).allowed
    assert api.view(item)==before

def test_default_policy_refusal_does_not_debit():
    service,item=prepared()
    error("MINIMUM_BALANCE_REQUIRED",lambda:invoke(service,"withdraw","ACC-1",money("60")))
    assert api.view(item)["balance"]==money("100")

@pytest.mark.parametrize("text", ["-1", "1.001", "NaN", "Infinity"])
def test_money_rejects_invalid_values(text):
    from app.domain.money import Money
    error("INVALID_AMOUNT", lambda:Money(Decimal(text),"EUR"))

def test_full_balance_and_overdraft_boundary():
    item=account()
    error("INSUFFICIENT_FUNDS",lambda:item.withdraw(money("100.01")))
    assert item.balance==money("100")
    assert item.withdraw(money("100"))==money("0")

@pytest.mark.parametrize("method", ["deposit", "withdraw"])
def test_zero_and_currency_are_not_valid_operations(method):
    item=account()
    error("INVALID_AMOUNT",lambda:getattr(item,method)(money("0")))
    error("CURRENCY_MISMATCH",lambda:getattr(item,method)(money("1","USD")))
    assert item.balance==money("100")

def test_blocked_account_and_read_only_balance():
    item=account()
    item.block()
    error("ACCOUNT_BLOCKED",lambda:item.withdraw(money("1")))
    with pytest.raises(AttributeError):
        item.balance=money("0")

from app.domain.withdrawal import WithdrawalRule,MaximumWithdrawalRule,MinimumBalanceRule

def test_abc_is_abstract():
    with pytest.raises(TypeError):
        WithdrawalRule()

@pytest.mark.parametrize("amount,allowed", [("500",True),("500.01",False)])
def test_cap_boundary(amount,allowed):
    result=MaximumWithdrawalRule(money("500")).check(account("1000"),money(amount))
    assert result==CheckResult(allowed,None if allowed else "WITHDRAWAL_LIMIT_EXCEEDED")

@pytest.mark.parametrize("amount,allowed", [("50",True),("50.01",False)])
def test_reserve_boundary(amount,allowed):
    result=MinimumBalanceRule(money("50")).check(account(),money(amount))
    assert result==CheckResult(allowed,None if allowed else "MINIMUM_BALANCE_REQUIRED")

def test_policy_currency_and_zero_reserve():
    error("CURRENCY_MISMATCH",lambda:MaximumWithdrawalRule(money("1","USD")).check(account(),money("1")))
    assert MinimumBalanceRule(money("0")).check(account(),money("100")).allowed

def test_policy_used_by_service(monkeypatch):
    monkeypatch.setattr(MaximumWithdrawalRule,"check",lambda *args:CheckResult(False,"CONTROL"))
    service,item=prepared()
    error("CONTROL",lambda:service.withdraw("ACC-1",money("1")))
    assert item.balance==money("100")
