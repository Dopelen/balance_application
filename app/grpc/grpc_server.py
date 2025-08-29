import asyncio
import grpc
from app.db.session import async_session
from app.services.balance_service import BalanceService
from app.grpc import balance_pb2, balance_pb2_grpc
from uuid import UUID

class BalanceServicer(balance_pb2_grpc.BalanceServiceServicer):
    """Реализация gRPC сервиса для работы с балансом и транзакциями."""

    async def ChangeBalance(self, request, context):
        async with async_session() as session:
            service = BalanceService(session)
            await service.change_balance(
                UUID(request.user_id),
                request.delta_current,
                request.delta_max
            )
        return balance_pb2.BalanceResponse(status="ok")

    async def OpenTransaction(self, request, context):
        async with async_session() as session:
            service = BalanceService(session)
            tx = await service.open_transaction(
                UUID(request.user_id),
                request.amount,
                request.timeout_seconds
            )
        return balance_pb2.TransactionResponse(
            transaction_id=str(tx.id),
            status=tx.status.value
        )

    async def CommitTransaction(self, request, context):
        async with async_session() as session:
            service = BalanceService(session)
            await service.commit_transaction(UUID(request.transaction_id))
        return balance_pb2.BalanceResponse(status="committed")

    async def CancelTransaction(self, request, context):
        async with async_session() as session:
            service = BalanceService(session)
            await service.cancel_transaction(UUID(request.transaction_id))
        return balance_pb2.BalanceResponse(status="cancelled")


async def serve():
    """Запуск gRPC сервера на порту 50051."""
    server = grpc.aio.server()
    balance_pb2_grpc.add_BalanceServiceServicer_to_server(BalanceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server listening on port 50051...")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())