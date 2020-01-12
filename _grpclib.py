import asyncio

import grpclib.server
from grpclib.client import Channel
from grpclib.encoding.base import CodecBase
from grpclib.utils import graceful_exit
from typing import Type

import protox
from app.protobuf.simple_service_grpclib import PingPongBase, PingPongStub
from app.protobuf.simple_service_pb import Request, Response


class PingPong(PingPongBase):
    async def unary_unary(self, stream: grpclib.server.Stream):
        _: Request = await stream.recv_message()
        await stream.send_message(Response())

    async def unary_stream(self, stream: grpclib.server.Stream):
        _: Request = await stream.recv_message()
        await stream.send_message(Response())

    async def stream_unary(self, stream: grpclib.server.Stream):
        _: Request = await stream.recv_message()
        await stream.send_message(Response())

    async def stream_stream(self, stream: grpclib.server.Stream):
        _: Request = await stream.recv_message()
        await stream.send_message(Response())


class ProtoxCodec(CodecBase):
    __content_subtype__ = 'proto'

    def encode(
        self,
        message: protox.Message,
        message_type: Type[protox.Message],
    ) -> bytes:
        if not isinstance(message, message_type):
            raise TypeError(
                'Message must be of type {!r}, not {!r}'.format(
                    message_type,
                    type(message),
                )
            )

        return message.to_bytes()

    def decode(
        self,
        data: bytes,
        message_type: Type[protox.Message],
    ) -> protox.Message:
        return message_type.from_bytes(data)


async def run_server(host, port):
    server = grpclib.server.Server(
        [PingPong()],
        codec=ProtoxCodec(),
    )

    with graceful_exit([server]):
        await server.start(host, port)
        print(f'Serving on {host}:{port}')
        await server.wait_closed()


async def main():
    host = 'localhost'
    port = 5051

    task = asyncio.create_task(
        run_server(host, port)
    )

    channel = Channel(host, port, codec=ProtoxCodec())
    greeter = PingPongStub(channel)

    await asyncio.sleep(1)
    response = await greeter.unary_unary(Request())
    print(response)

    channel.close()


if __name__ == '__main__':
    asyncio.run(main())
