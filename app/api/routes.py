from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.balance_service import BalanceService
from app.api.schemas import BalanceChange, TransactionOpen, TransactionAction
from uuid import UUID

router = APIRouter()

@router.post("/user/{user_id}/balance")
async def change_balance(user_id: UUID, data: BalanceChange, session: AsyncSession = Depends(get_session)):
    service = BalanceService(session)
    try:
        await service.change_balance(user_id, data.delta_current, data.delta_max)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@router.post("/transaction/open")
async def open_transaction(data: TransactionOpen, session: AsyncSession = Depends(get_session)):
    service = BalanceService(session)
    try:
        tx = await service.open_transaction(data.user_id, data.amount, data.timeout_seconds)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"transaction_id": str(tx.id), "status": tx.status.value}

@router.post("/transaction/commit")
async def commit_transaction(data: TransactionAction, session: AsyncSession = Depends(get_session)):
    service = BalanceService(session)
    try:
        await service.commit_transaction(data.transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "committed"}

@router.post("/transaction/cancel")
async def cancel_transaction(data: TransactionAction, session: AsyncSession = Depends(get_session)):
    service = BalanceService(session)
    try:
        await service.cancel_transaction(data.transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "cancelled"}