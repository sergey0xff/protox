compile-proto:
	protoc \
		--proto_path=protobuf_src \
		--protox_out=. \
		--protox_opt="--base-package=app/protobuf --grpclib --with-dependencies" \
		./protobuf_src/service.proto

