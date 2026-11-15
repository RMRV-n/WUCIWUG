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

from app.domain.withdrawal import WithdrawalRuleGroup, WithdrawalRule
from app.support.types import CheckResult

def test_progression_group_order_snapshot_and_identity():
    calls = []
    class Rule(WithdrawalRule):
        def __init__(self, name, allowed=True): self.name, self.allowed = name, allowed
        def check(self, account, amount):
            calls.append(self.name)
            return CheckResult(True) if self.allowed else CheckResult(False, self.name)
    deny = Rule("DENIED", False)
    rules = [Rule("FIRST"), deny, Rule("NEVER")]
    group = WithdrawalRuleGroup(rules)
    rules.clear()
    assert group.check(object(), object()).code == "DENIED"
    assert calls == ["FIRST", "DENIED"]
    calls.clear()
    deny.name = "SAME_INSTANCE"
    assert group.check(object(), object()).code == "SAME_INSTANCE"
    assert calls == ["FIRST", "SAME_INSTANCE"]
    assert WithdrawalRuleGroup([]).check(object(), object()).allowed
    calls.clear()
    nested = WithdrawalRuleGroup([WithdrawalRuleGroup([Rule("A")]), Rule("B")])
    assert nested.check(object(), object()).allowed and calls == ["A", "B"]

def test_progression_group_bad_result_and_error():
    calls = []
    class Bad(WithdrawalRule):
        def check(self, account, amount): calls.append("bad"); return None
    code("INVALID_RESULT", lambda: WithdrawalRuleGroup([Bad()]).check(object(), object()))
    assert calls == ["bad"]
    class Broken(WithdrawalRule):
        def check(self, account, amount): raise DomainError("RULE_FAILED")
    code("RULE_FAILED", lambda: WithdrawalRuleGroup([Broken()]).check(object(), object()))
    code("INVALID_CONFIG", lambda: WithdrawalRuleGroup([object()]))


def test_progression_default_assembly_uses_group(monkeypatch):
    calls = []
    def check(self, *args):
        calls.append(args)
        return CheckResult(False, "GROUP_USED")
    monkeypatch.setattr(WithdrawalRuleGroup, "check", check)
    service = api.create()
    service.register(Account("A", "C", money("200")))
    assert service.check("A", money("10")).code == "GROUP_USED"
    assert len(calls) == 1

from app.domain.withdrawal import MinimumWithdrawalRule
from app.domain.account import Account
from app.domain.money import money

def test_progression_extra_lab06():
    account = Account("A", "C", money("100"))
    rule = MinimumWithdrawalRule(money("20"))
    assert rule.check(account, money("20")).allowed
    assert rule.check(account, money("19.99")).code == "WITHDRAWAL_TOO_SMALL"
    code("INVALID_CONFIG", lambda: MinimumWithdrawalRule(money("0")))
    assert account.balance == money("100")
