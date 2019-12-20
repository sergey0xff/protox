.PHONY: protobuf protobuf-dev protox

protobuf:
	python3 -m grpc_tools.protoc --proto_path=protobuf_src --python_out=protobuf_out ./protobuf_src/*.proto

protobuf-dev:
	python3 -m grpc_tools.protoc --proto_path=protobuf_src --python_out=protobuf_out ./protobuf_src/dev.proto

protox:
	protoc \
		--proto_path=protobuf_src \
		--plugin=protoc-gen-protox=./protox/plugin/protox_gen.py\
		--protox_out=. \
		--protox_opt=base_package=app/protobuf\
		./protobuf_src/hello_protox.proto