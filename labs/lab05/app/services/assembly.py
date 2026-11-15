from app.services.account_service import AccountService
from app.support.types import Repository
from app.domain.money import money
from app.domain.withdrawal import MaximumWithdrawalRule, MinimumBalanceRule

def build_service(repository=None, rules=None):
    # Если репозиторий не передан, создаём дефолтный
    repository = repository if repository is not None else Repository("account_id")
    
    # ВАЖНО: проверяем именно на None! 
    # Если передали rules=[] (пустой список), мы должны оставить его пустым, а не заменять.
    if rules is None:
        rules = (
            MaximumWithdrawalRule(money("500")),
            MinimumBalanceRule(money("50"))
        )
        
    return AccountService(repository, rules)