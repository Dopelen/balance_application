from pydantic import BaseModel
from uuid import UUID

class BalanceChange(BaseModel):
    delta_current: float = 0.0
    delta_max: float = 0.0

class TransactionOpen(BaseModel):
    user_id: UUID
    amount: float
    timeout_seconds: int = 3600

class TransactionAction(BaseModel):
    transaction_id: UUID