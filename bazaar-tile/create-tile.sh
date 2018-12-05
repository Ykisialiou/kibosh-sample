#!/usr/bin/env bash

kibosh_version=0.1.3
kibosh_release_path=./resources/kibosh-release-${kibosh_version}.tgz
if [ -f "${kibosh_release_path}" ]; then
    echo " kibosh release tgz already exists, skipping download"
else
    echo "kibosh release tgz doesn't exists, downloading"
    url=https://github.com/cf-platform-eng/kibosh/releases/download/${kibosh_version}/kibosh-release-${kibosh_version}.tgz
    wget ${url} -O "${kibosh_release_path}"
fi

routing_version=0.179.0
routing_release_path=./resources/routing-${routing_version}.tgz
if [ -f "${routing_release_path}" ]; then
    echo " routing release tgz already exists, skipping download"
else
    echo "routing release doesn't exists, downloading"
    url=https://github.com/cloudfoundry/routing-release/releases/download/${routing_version}/routing-${routing_version}.tgz
    wget ${url} -O "${routing_release_path}"
fi

tile build
