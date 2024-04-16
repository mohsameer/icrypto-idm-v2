#!/bin/sh

if [[ -z "${SKIP_IMPORT_OBJECTS}" ]]; then
  rm -rf $CONSUL_OBJECT_LOCATION
fi

# Consul template loads IDM config as well as XMLs such as IDM resources, roles ...
consul-template \
    -log-level info \
    -template $CONSUL_TEMPLATE_LOCATION':'$CONSUL_CONFIG_LOCATION \
    -template $CONSUL_OBJECT_TEMPLATE_LOCATION':'$CONSUL_OBJECT_LOCATION \
    -wait 5s \
    -consul-retry \
    -consul-retry-attempts 999 \
    -consul-addr $CONSUL_HOST:$CONSUL_PORT \
    -once

if [[ -z "${SKIP_VAULT}" ]]; then
  export REPO_PASSWORD_FILE=${MP_DIR}/var/mp_database_password.txt
  export MP_KEYSTORE_PASSWORD_FILE=${MP_DIR}/var/mp_keystore_password.txt
#  This part loads secrets from vault into XML templates
  if [[ -z "${SKIP_IMPORT_OBJECTS}" ]]; then
    XML_OBJECTS=$(find /opt/midpoint/var/post-initial-objects/ -name "*.xml")
    for file in $XML_OBJECTS; do
         echo -e "template { \n source = \"$file\" \n destination = \"$file\" \n }" >> $VAULT_CONF_LOCATION
    done
  fi
  vault agent -address="$VAULT_ADDR" -config $VAULT_CONF_LOCATION
fi

if [[ -z "${SKIP_RESOURCE_REMOVAL}" ]]; then
  ( sleep 300 ; rm  -r /opt/midpoint/var/post-initial-objects/*.done ) &
fi

chmod a+x /opt/midpoint/bin/midpoint.sh
/opt/midpoint/bin/midpoint.sh container
