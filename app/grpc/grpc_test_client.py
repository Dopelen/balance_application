import grpc
from app.grpc import balance_pb2, balance_pb2_grpc

def run():
    # подключение к gRPC серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = balance_pb2_grpc.BalanceServiceStub(channel)

    # пример запроса ChangeBalance
    response = stub.ChangeBalance(
        balance_pb2.BalanceChange(
            user_id="00000000-0000-0000-0000-000000000001",
            delta_current=100,
            delta_max=50
        )
    )
    print("ChangeBalance response:", response.status)

if __name__ == "__main__":
    run()