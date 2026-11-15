from decimal import Decimal
from app.services.account_service import AccountService
from app.support.types import Repository
from app.domain.money import money
from app.domain.withdrawal import (
    MaximumWithdrawalRule,
    MinimumBalanceRule,
    MaximumShareRule,
    WithdrawalRuleGroup,
)


def build_service(repository=None, rules=None):
    repository = repository if repository is not None else Repository("account_id")

    if rules is None:
        standard_group = WithdrawalRuleGroup((
            MaximumWithdrawalRule(money("500")),
            MinimumBalanceRule(money("50")),
            MaximumShareRule(Decimal("0.50")),
        ))
        rules = [standard_group]

    return AccountService(repository, rules)