#!/usr/bin/env python3
import argparse
import shlex
import sys
from typing import Set

from protox.plugin.grpclib_code_generator import GrpclibCodeGenerator
from protox.plugin.index import Index
from protox.plugin.protobuf_code_generator import ProtobufCodeGenerator
from protox.well_known_types.plugin import CodeGeneratorRequest, CodeGeneratorResponse


def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Protox cli'
    )

    parser.add_argument(
        '--base-package',
        default='',
        type=str,
        help='Base python package directory relative to the root directory. E.g. app/protobuf, .'
    )
    parser.add_argument(
        '--with-dependencies',
        action='store_true',
        help='If enabled all imported .proto files are also generated',
    )

    parser.add_argument(
        '--grpclib',
        action='store_true',
        help='If enabled grpclib services are generated'
    )

    return parser


def main():
    data = sys.stdin.buffer.read()
    request = CodeGeneratorRequest.from_bytes(data)

    parameter = (request.parameter or '').strip('"\'')
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(
        shlex.split(parameter)
    )

    index = Index(
        request,
        args.base_package
    )

    files_to_generate: Set[str] = set(request.file_to_generate)

    files = [
        x for x in request.proto_file
        if not x.name.startswith('google/protobuf/')
    ]

    if not args.with_dependencies:
        files = [
            x for x in request.proto_file
            if x.name in files_to_generate
        ]

    code_generators = [
        ProtobufCodeGenerator(file, index)
        for file in files
    ]

    response_files = [
        x.generate()
        for x in code_generators
        if not x.empty()
    ]

    if args.grpclib:
        response_files += [
            GrpclibCodeGenerator(gen).generate()
            for gen in code_generators
            if gen.has_services()
        ]

    response = CodeGeneratorResponse(
        file=response_files
    )

    sys.stdout.buffer.write(
        response.to_bytes()
    )


if __name__ == '__main__':
    main()
