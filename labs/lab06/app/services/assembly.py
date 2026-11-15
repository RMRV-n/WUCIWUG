from app.services.account_service import AccountService
from app.support.types import Repository
from app.domain.money import money
from app.domain.withdrawal import MaximumWithdrawalRule, MinimumBalanceRule

def build_service(repository=None, rules=None):
    repository = repository if repository is not None else Repository("account_id")
    return AccountService(repository, [MaximumWithdrawalRule(money("500")), MinimumBalanceRule(money("50"))] if rules is None else rules)
