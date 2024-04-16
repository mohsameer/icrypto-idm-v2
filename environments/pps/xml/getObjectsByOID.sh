#!/bin/bash

# This script downloads XMLs from IDM based on the provided type and oid below.

URL="https://qa-idm.pps.co.za"
AUTHN=$(echo -n "$1:$2" | base64 )
BACKUP_FOLDER="backup-qa"

resources=( "b002f100-e79e-489d-8837-aa7d70dcecf3" "eefb6b98-9ef8-4523-90ff-feb58563a624" "4c627e2a-01ab-4139-ba08-9d7c75a0a012" "f22df5b2-6daf-4bfd-ba52-f999966fb149" "dabfcbe2-42c2-4611-8df0-745cbb224148" "b3d2aa73-ba30-4a8c-986f-e0d577944484" "6d475d6b-8fa7-4fb0-b2de-f311b315339c" )
roles=( "e2c88fea-db21-11e5-80ba-d7b2f1159654" "e2c99fea-db21-22e5-91ba-d7b2f3355275" "dc6fbbfc-faec-445a-b345-bf56dae3ff10" "e2c88fea-db21-11e5-80ba-d7b2f1155264")
systemConfigurations=( "00000000-0000-0000-0000-000000000001" )
objectTemplates=( "c0c010c0-d34d-b33f-f00d-777222222333" )

mkdir -p $BACKUP_FOLDER
mkdir -p $BACKUP_FOLDER/resources
mkdir -p $BACKUP_FOLDER/roles
mkdir -p $BACKUP_FOLDER/systemConfigurations
mkdir -p $BACKUP_FOLDER/objectTemplates

for oid in "${resources[@]}"
do
   curl $URL/midpoint/ws/rest/resources/$oid --header "Authorization: Basic $AUTHN" > $BACKUP_FOLDER/resources/$oid.xml
done

for oid in "${roles[@]}"
do
   curl $URL/midpoint/ws/rest/roles/$oid --header "Authorization: Basic $AUTHN" > $BACKUP_FOLDER/roles/$oid.xml
done

for oid in "${systemConfigurations[@]}"
do
   curl $URL/midpoint/ws/rest/systemConfigurations/$oid --header "Authorization: Basic $AUTHN" > $BACKUP_FOLDER/systemConfigurations/$oid.xml
done

for oid in "${objectTemplates[@]}"
do
   curl $URL/midpoint/ws/rest/objectTemplates/$oid --header "Authorization: Basic $AUTHN" > $BACKUP_FOLDER/objectTemplates/$oid.xml
done


