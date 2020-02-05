import asyncio

from grpclib.client import Channel
from grpclib.server import Server
from grpclib.utils import graceful_exit

from app.my_service import MyService
from app.protobuf.service.ping_pb import PingResponse, PingRequest
from app.protobuf.service_grpclib import MyServiceStub

HOST = 'localhost'
PORT = 5051


async def create_client(server_started_event: asyncio.Event):
    await server_started_event.wait()

    channel = Channel(
        host=HOST,
        port=PORT
    )
    stub = MyServiceStub(channel)

    try:
        while True:
            response: PingResponse = await stub.ping(
                PingRequest(message='Hello there!')
            )
            print(f'Response: {response.message}')
            await asyncio.sleep(1)
    finally:
        channel.close()


async def main():
    server = Server([MyService()])
    server_started_event = asyncio.Event()

    asyncio.create_task(
        create_client(server_started_event)
    )

    with graceful_exit([server]):
        await server.start(
            host=HOST,
            port=PORT,
        )
        server_started_event.set()
        print(f'Serving on {HOST}:{PORT}')
        await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
