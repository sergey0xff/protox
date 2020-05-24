PROTOC := docker run \
	--user $(shell id -u):$(shell id -g)  \
	--mount type=bind,src=$(shell pwd),target=/usr/src \
	-w /usr/src \
	srgt/protox-compiler \
	python -m grpc_tools.protoc

compile-proto:
	$(PROTOC) \
		--proto_path=protobuf_src \
		--protox_out=. \
		--protox_opt="--base-package=protobuf_out --grpclib --with-dependencies" \
		./protobuf_src/ping_service.proto

