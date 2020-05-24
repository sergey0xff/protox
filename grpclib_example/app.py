import asyncio

import grpclib
from grpclib.client import Channel
from grpclib.server import Server
from grpclib.utils import graceful_exit

from protobuf_out.ping_service_grpclib import MyServiceBase, MyServiceStub
from protobuf_out.ping_service_pb import PingRequest, PingResponse

HOST = 'localhost'
PORT = 5051


class MyService(MyServiceBase):
    async def ping(self, stream: grpclib.server.Stream):
        request: PingRequest = await stream.recv_message()
        counter = request.counter + 1
        print(f'[Server]: {counter}')
        await stream.send_message(
            PingResponse(
                status=PingResponse.Status.OK,
                counter=counter,
            )
        )


async def create_client(
    server_started_event: asyncio.Event
):
    channel = Channel(
        host=HOST,
        port=PORT
    )
    stub = MyServiceStub(channel)
    counter = 0

    # explicitly wait for server start
    await server_started_event.wait()
    try:
        while True:
            print(f'[Client]: {counter}')
            response: PingResponse = await stub.ping(
                PingRequest(counter=counter)
            )
            counter = response.counter + 1
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
