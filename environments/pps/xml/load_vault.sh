#!/bin/bash

VAULT_TOKEN=$1
SOURCE_FILE=$2
VAULT_URL="http://localhost:8200/v1/"


for data in $(cat $SOURCE_FILE); do
    key=$(echo $data | awk '{sub(/=/," ")}1' | awk '{print $1}')
    value=$(echo $data | awk '{sub(/=/," ")}1' | awk '{print $2}')
    echo "Loading $key $value"
    curl \
        -H "X-Vault-Token: $VAULT_TOKEN" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "{\"value\":\"$value\"}" \
        $VAULT_URL$key
done


