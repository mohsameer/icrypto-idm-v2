#!/bin/bash

# This script uploads XMLs from BACKUP_FOLDER into the IDM

URL="http://localhost:8080"
AUTHN=$(echo -n "$1:$2" | base64 )
BACKUP_FOLDER="backup-local"

files=$(find $BACKUP_FOLDER -type f -name "*.xml")

for file in $files
do
    echo "Loading $file"
    path=$(echo $file | sed "s/$BACKUP_FOLDER\///" | sed 's/.xml//')
    curl -X PUT $URL/midpoint/ws/rest/$path -H "Content-Type: application/xml" --header "Authorization: Basic $AUTHN" -d @$file
done


