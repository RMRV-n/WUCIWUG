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
