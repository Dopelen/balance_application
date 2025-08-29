import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import Transaction, TransactionStatus, User

class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def open_transaction(self, user_id, amount, timeout_seconds=3600):
        async with self.session.begin():
            # Получаем пользователя с блокировкой строки FOR UPDATE
            result = await self.session.execute(
                select(User).where(User.id == user_id).with_for_update()
            )
            user = result.scalar_one_or_none()
            if not user:
                raise ValueError("User not found")

            available = user.balance_current
            if amount > available:
                raise ValueError("Insufficient funds")

            # Блокируем средства
            user.balance_current -= amount

            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                status=TransactionStatus.OPEN,
                expires_at=datetime.datetime.utcnow() + datetime.timedelta(seconds=timeout_seconds)
            )
            self.session.add(transaction)
            self.session.add(user)
            return transaction

    async def commit_transaction(self, transaction_id):
        async with self.session.begin():
            result = await self.session.execute(
                select(Transaction).where(Transaction.id == transaction_id).with_for_update()
            )
            tx = result.scalar_one_or_none()
            if not tx or tx.status != TransactionStatus.OPEN:
                raise ValueError("Transaction not open or not found")

            tx.status = TransactionStatus.COMMITTED
            self.session.add(tx)

    async def cancel_transaction(self, transaction_id):
        async with self.session.begin():
            result = await self.session.execute(
                select(Transaction).where(Transaction.id == transaction_id).with_for_update()
            )
            tx = result.scalar_one_or_none()
            if not tx or tx.status != TransactionStatus.OPEN:
                raise ValueError("Transaction not open or not found")

            # Возвращаем средства пользователю
            user = await self.session.execute(
                select(User).where(User.id == tx.user_id).with_for_update()
            )
            user = user.scalar_one()
            user.balance_current += tx.amount

            tx.status = TransactionStatus.CANCELLED
            self.session.add(user)
            self.session.add(tx)
