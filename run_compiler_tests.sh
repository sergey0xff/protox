#!/usr/bin/env bash

tmp_dir="$(mktemp -d -t proto-XXXXXXXXXX)"

protoc \
  --proto_path=compiler_tests \
  --protox_out=$tmp_dir \
  --protox_opt="--with-dependencies" \
  compiler_tests/*.proto

for filename in $tmp_dir/*.py; do
  python3.7 $filename
done

rm -rf $tmp_dir
