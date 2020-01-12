import abc
import typing

import grpclib.const
import grpclib.client
import grpclib.server

import app.protobuf.simple_service_pb as \
    simple_service_pb


class PingPongBase(abc.ABC):
    @abc.abstractmethod
    async def unary_unary(self, stream: grpclib.server.Stream):
        pass

    @abc.abstractmethod
    async def unary_stream(self, stream: grpclib.server.Stream):
        pass

    @abc.abstractmethod
    async def stream_unary(self, stream: grpclib.server.Stream):
        pass

    @abc.abstractmethod
    async def stream_stream(self, stream: grpclib.server.Stream):
        pass

    def __mapping__(self) -> typing.Mapping[str, grpclib.const.Handler]:
        return {
            '/services.ping_pong.PingPong/UnaryUnary': grpclib.const.Handler(
                self.unary_unary,
                grpclib.const.Cardinality.UNARY_UNARY,
                simple_service_pb.Request,
                simple_service_pb.Response,
            ),
            '/services.ping_pong.PingPong/UnaryStream': grpclib.const.Handler(
                self.unary_stream,
                grpclib.const.Cardinality.UNARY_STREAM,
                simple_service_pb.Request,
                simple_service_pb.Response,
            ),
            '/services.ping_pong.PingPong/StreamUnary': grpclib.const.Handler(
                self.stream_unary,
                grpclib.const.Cardinality.STREAM_UNARY,
                simple_service_pb.Request,
                simple_service_pb.Response,
            ),
            '/services.ping_pong.PingPong/StreamStream': grpclib.const.Handler(
                self.stream_stream,
                grpclib.const.Cardinality.STREAM_STREAM,
                simple_service_pb.Request,
                simple_service_pb.Response,
            ),
        }


class PingPongStub:
    def __init__(self, channel: grpclib.client.Channel):
        self.unary_unary = grpclib.client.UnaryUnaryMethod(
            channel,
            '/services.ping_pong.PingPong/UnaryUnary',
            simple_service_pb.Request,
            simple_service_pb.Response,
        )
        self.unary_stream = grpclib.client.UnaryStreamMethod(
            channel,
            '/services.ping_pong.PingPong/UnaryStream',
            simple_service_pb.Request,
            simple_service_pb.Response,
        )
        self.stream_unary = grpclib.client.StreamUnaryMethod(
            channel,
            '/services.ping_pong.PingPong/StreamUnary',
            simple_service_pb.Request,
            simple_service_pb.Response,
        )
        self.stream_stream = grpclib.client.StreamStreamMethod(
            channel,
            '/services.ping_pong.PingPong/StreamStream',
            simple_service_pb.Request,
            simple_service_pb.Response,
        )
