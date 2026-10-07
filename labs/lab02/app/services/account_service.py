from app.domain.account import Account
from app.domain.money import money
from app.support.types import checked, CheckResult
from app.support.errors import DomainError


class AccountService:
    def __init__(self, repository, rules=()):
        self._repository = repository
        self._rules = tuple(rules)

    def register(self, account):
        return self._repository.add(account)

    def get(self, account_id):
        return self._repository.get(account_id)

    def check(self, account_id, amount):
        account = self.get(account_id)
        result = account.check_withdrawal(amount)
        if not result.allowed:
            return result
        amount.same_currency(money("500"))
        if amount.amount > 500:
            return CheckResult(False, "WITHDRAWAL_LIMIT_EXCEEDED")
        if account.balance.amount - amount.amount < 50:
            return CheckResult(False, "MINIMUM_BALANCE_REQUIRED")
        return CheckResult(True)

    def withdraw(self, account_id, amount):
        result = self.check(account_id, amount)
        if not result.allowed:
            raise DomainError(result.code)
        return self.get(account_id).withdraw(amount)

    def deposit(self, account_id, amount):
        return self.get(account_id).deposit(amount)

def make_entity(*args, **kwargs):
    return Account(*args, **kwargs)


def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)


def view(entity):
    return {'account_id': entity.account_id, 'customer_id': entity.customer_id, 'balance': entity.balance, 'status': entity.status}


from app.support.types import Repository
from app.domain.money import money

def new_service(repository=None):
    return AccountService(repository if repository is not None else Repository("account_id"))
