from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.user import UserRepository
from app.db.repositories.transaction import TransactionRepository

class BalanceService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.tx_repo = TransactionRepository(session)

    # Баланс пользователя
    async def change_balance(self, user_id, delta_current=0.0, delta_max=0.0):
        await self.user_repo.change_balance(user_id, delta_current, delta_max)

    # Транзакции
    async def open_transaction(self, user_id, amount, timeout_seconds=3600):
        return await self.tx_repo.open_transaction(user_id, amount, timeout_seconds)

    async def commit_transaction(self, transaction_id):
        await self.tx_repo.commit_transaction(transaction_id)

    async def cancel_transaction(self, transaction_id):
        await self.tx_repo.cancel_transaction(transaction_id)