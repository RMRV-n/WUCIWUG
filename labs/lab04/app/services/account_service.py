from app.domain.account import Account
from app.domain.money import money
from app.domain.withdrawal import MaximumWithdrawalRule, MinimumBalanceRule
from app.support.types import checked, CheckResult
from app.support.errors import DomainError


class AccountService:
    def __init__(self, repository, rules=()):
        self._repository = repository
        # Оставляем правила по умолчанию, если не переданы свои
        self._rules = tuple(rules) if rules else (MaximumWithdrawalRule(money("500")), MinimumBalanceRule(money("50")))

    def register(self, account):
        return self._repository.add(account)

    def get(self, account_id):
        return self._repository.get(account_id)

    def check(self, account_id, amount):
        account = self.get(account_id)
        
        # 1. Делегируем обязательную проверку счёту (вместо дублирования)
        result = account.check_withdrawal(amount)
        if not result.allowed:
            return result
        
        # 2. Проверяем дополнительные правила
        for rule in self._rules:
            result = checked(rule.check(account, amount))
            if not result.allowed:
                return result
        
        return CheckResult(True)

    def withdraw(self, account_id, amount):
        result = self.check(account_id, amount)
        if not result.allowed:
            raise DomainError(result.code)
        
        account = self.get(account_id)
        # 3. Меняем баланс ТОЛЬКО через метод счёта
        return account.withdraw(amount)

    def deposit(self, account_id, amount):
        account = self.get(account_id)
        # 4. (Бонус) Пополняем через метод счёта, не лезем в _balance напрямую
        return account.deposit(amount)


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