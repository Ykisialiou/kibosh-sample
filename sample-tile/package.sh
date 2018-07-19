#!/usr/bin/env bash
set -e

rm -rf ./resources/kibosh.zip

pushd src
zip -r kibosh.zip .
popd

mv ./src/kibosh.zip ./resources/
zip -u ./resources/kibosh.zip kibosh.linux

tile build
