import grpclib.server

from app.protobuf.service.ping_pb import PingRequest, PingResponse
from app.protobuf.service_grpclib import MyServiceBase


class MyService(MyServiceBase):
    async def ping(self, stream: grpclib.server.Stream):
        request: PingRequest = await stream.recv_message()
        response = PingResponse(
            status=PingResponse.Status.OK,
            message=request.message[::-1]
        )
        await stream.send_message(response)
