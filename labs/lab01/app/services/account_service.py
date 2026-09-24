# ЛР1: заготовленный сервис. Допишите отмеченный метод и подключите объекты.
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
        raise NotImplementedError("ЛР1: завершите AccountService.withdraw")

    def deposit(self, account_id, amount):
        return self.get(account_id).deposit(amount)


from app.support.types import Repository


from app.domain.money import money


# Ниже — прежний рабочий путь. Перенесите поведение, затем обновите
# make_entity, invoke, view и new_service: сигнатуры должны сохраниться.
from app.domain.money import money
from app.support.types import CheckResult
from app.support.errors import DomainError


def make_entity(account_id, customer_id, balance):
    return dict(account_id=account_id, customer_id=customer_id, balance=balance, status="ACTIVE")


def _new_legacy_service(repository):
    return {"repository": repository}


def view(account):
    return dict(account)


def invoke(service, method, *args):
    repository = service["repository"]
    if method == "register":
        return repository.add(args[0])
    account = repository.get(args[0])
    if method == "get":
        return account
    amount = args[1]
    if method == "deposit":
        account["balance"] = account["balance"].add(amount)
        return account["balance"]
    if amount.amount > account["balance"].amount:
        result = CheckResult(False, "INSUFFICIENT_FUNDS")
    elif amount.amount > 500:
        result = CheckResult(False, "WITHDRAWAL_LIMIT_EXCEEDED")
    elif account["balance"].amount - amount.amount < 50:
        result = CheckResult(False, "MINIMUM_BALANCE_REQUIRED")
    else:
        result = CheckResult(True)
    if method == "check":
        return result
    if not result.allowed:
        raise DomainError(result.code)
    account["balance"] = account["balance"].subtract(amount)
    return account["balance"]


from app.support.types import Repository

def new_service(repository=None):
    return _new_legacy_service(repository if repository is not None else Repository("account_id"))
