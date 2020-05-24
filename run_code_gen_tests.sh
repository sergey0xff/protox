#!/usr/bin/env bash

tmp_dir="$(mktemp -d -t proto-XXXXXXXXXX)"

python3.8 -m pip install .
echo '+ Protox installed'

protoc \
  --proto_path=code_gen_tests \
  --protox_out=$tmp_dir \
  --protox_opt="--with-dependencies" \
  code_gen_tests/*.proto

echo '+ Protobuf messages compiled'

for filename in $tmp_dir/*.py; do
  python3.8 $filename
done

rm -rf $tmp_dir

echo '+ All tests passed'
