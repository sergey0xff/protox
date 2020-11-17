#!/usr/bin/env bash
set -e

tmp_dir="$(mktemp -d -t proto-XXXXXXXXXX)"

python3.8 -m pip install . grpclib protobuf grpcio-tools
echo '+ Protox installed'

python3.8 -m grpc_tools.protoc \
  --proto_path=tests/code_gen_tests \
  --protox_out=$tmp_dir \
  --protox_opt="--with-dependencies" \
  tests/code_gen_tests/*.proto

echo '+ Protobuf messages compiled'

for filename in $tmp_dir/*.py; do
  python3.8 $filename
done

rm -rf $tmp_dir

echo '+ Tests completed'
