#!/bin/bash

URL="https://qa-idm.pps.co.za"
AUTHN=$(echo -n "$1:$2" | base64 )

mkdir -p backup
curl $URL/midpoint/ws/rest/resources --header "Authorization: Basic $AUTHN" > backup/resources.xml
curl $URL/midpoint/ws/rest/roles --header "Authorization: Basic $AUTHN" > backup/roles.xml
curl $URL/midpoint/ws/rest/objectTemplates --header "Authorization: Basic $AUTHN" > backup/templates.xml
curl $URL/midpoint/ws/rest/systemConfigurations --header "Authorization: Basic $AUTHN" > backup/systemConf.xml
curl $URL/midpoint/ws/rest/valuePolicies --header "Authorization: Basic $AUTHN" > backup/valuePolicies.xml

