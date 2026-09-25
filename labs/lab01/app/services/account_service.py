# ЛР1: заготовленный сервис. Допишите отмеченный метод и подключите объекты.
from app.domain.account import Account
from app.domain.money import money
from app.support.types import checked, CheckResult, Repository
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
        # 1. Проверяем, разрешено ли снятие средств
        result = self.check(account_id, amount)
        if not result.allowed:
            raise DomainError(result.code)
        
        # 2. Получаем аккаунт и вызываем его метод withdraw 
        # (возвращаем новый баланс, чтобы соответствовать поведению легаси-кода)
        account = self.get(account_id)
        return account.withdraw(amount)

    def deposit(self, account_id, amount):
        return self.get(account_id).deposit(amount)


# ==========================================
# Ниже — адаптация прежнего рабочего пути.
# Сигнатуры функций сохранены, но внутри 
# теперь используется ООП-подход.
# ==========================================

def make_entity(account_id, customer_id, balance):
    # Создаём настоящий ООП-объект Account вместо словаря
    return Account(account_id=account_id, customer_id=customer_id, balance=balance)


def view(account):
    # Возвращаем словарное представление объекта Account
    # (используем getattr для безопасности, если вдруг атрибуты называются чуть иначе)
    return {
        "account_id": getattr(account, "account_id", None),
        "customer_id": getattr(account, "customer_id", None),
        "balance": getattr(account, "balance", None),
        "status": getattr(account, "status", "ACTIVE"),
    }


def invoke(service, method, *args):
    # service теперь это экземпляр AccountService.
    # Мы просто делегируем вызовы нужным методам сервиса.
    if method == "register":
        return service.register(args[0])
    if method == "get":
        return service.get(args[0])
    if method == "deposit":
        return service.deposit(args[0], args[1])
    if method == "check":
        return service.check(args[0], args[1])
    if method == "withdraw":
        return service.withdraw(args[0], args[1])
    
    raise ValueError(f"Неизвестный метод: {method}")


def new_service(repository=None):
    # Создаём и возвращаем новый ООП-сервис
    repo = repository if repository is not None else Repository("account_id")
    return AccountService(repo)