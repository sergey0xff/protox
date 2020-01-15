.PHONY: protobuf protobuf-dev protox

#protobuf:
#	python3 -m grpc_tools.protoc --proto_path=protobuf_src --python_out=protobuf_out ./protobuf_src/*.proto
#
#protobuf-dev:
#	python3 -m grpc_tools.protoc --proto_path=protobuf_src --python_out=protobuf_out ./protobuf_src/dev.proto

protox:
	protoc \
		--proto_path=protobuf_src \
		--plugin=protoc-gen-protox=./protox/plugin/__init__.py\
		--protox_out=. \
		--protox_opt=--base-package-dir=app/protobuf\
		./protobuf_src/hello_protox.proto


protox-service:
	protoc \
		--proto_path=protobuf_src \
		--plugin=protoc-gen-protox=./protox/plugin/__init__.py\
		--protox_out=. \
		--protox_opt="--base-package-dir=app/protobuf --grpclib --gen-deps" \
		./protobuf_src/dev.proto
