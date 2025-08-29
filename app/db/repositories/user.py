from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id):
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def change_balance(self, user_id, delta_current=0.0, delta_max=0.0):
        async with self.session.begin():
            user = await self.get(user_id)
            if not user:
                raise ValueError("User not found")

            new_max = max(user.balance_max + delta_max, 0.0)
            new_current = max(min(user.balance_current + delta_current, new_max), 0.0)

            user.balance_max = new_max
            user.balance_current = new_current
            self.session.add(user)