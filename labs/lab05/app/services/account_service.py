from app.domain.account import Account
from app.support.types import checked, CheckResult
from app.support.errors import DomainError


class AccountService:
    def __init__(self, repository, rules=()):
        self._repository = repository
        # Сохраняем правила как tuple. Не создаём их здесь!
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
        for rule in self._rules:
            result = checked(rule.check(account, amount))
            if not result.allowed:
                return result
        return CheckResult(True)

    def withdraw(self, account_id, amount):
        # Шаг 2: Сначала проверяем
        result = self.check(account_id, amount)
        if not result.allowed:
            raise DomainError(result.code)
        # Если всё ок, списываем ровно один раз через метод счёта
        return self.get(account_id).withdraw(amount)

    def deposit(self, account_id, amount):
        return self.get(account_id).deposit(amount)

    def preview_withdrawals(self, account_id, amounts):
        # Шаг 4: Проверяем каждую сумму, но не списываем
        previews = []
        for amount in amounts:
            check_result = self.check(account_id, amount)
            if check_result.allowed:
                # Money.subtract возвращает НОВЫЙ объект, не меняя баланс счёта
                account = self.get(account_id)
                projected_balance = account.balance.subtract(amount)
            else:
                projected_balance = None
            previews.append((amount, check_result, projected_balance))
        return tuple(previews)

    def allowed_amounts(self, account_id, amounts):
        # Шаг 4: Выбираем только те суммы, которые прошли проверку
        previews = self.preview_withdrawals(account_id, amounts)
        return tuple(p[0] for p in previews if p[1].allowed)


def make_entity(*args, **kwargs):
    return Account(*args, **kwargs)


def invoke(service, method, *args, **kwargs):
    return getattr(service, method)(*args, **kwargs)


def view(entity):
    return {'account_id': entity.account_id, 'customer_id': entity.customer_id, 'balance': entity.balance, 'status': entity.status}