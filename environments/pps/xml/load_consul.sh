#!/bin/bash

CONSUL_TOKEN=$1
CONSUL_URL="http://localhost:8500/v1/kv/idm/objects/"

for file in $(find . -name "*.xml" -not -path "./deprecated/*"  -not -path "./backup*"); do
    fileabs=${file:2}
    echo "Loading $fileabs"
    curl -X PUT --header "X-Consul-Token: $CONSUL_TOKEN" --data-binary @$file $CONSUL_URL$fileabs
done