### Load IDM configurations
1. Prepare secrets.prop according to the environment.
2. Run load_vault.sh to put secrets into the vault. Go to UI and check if secrets are imported.
3. Run load_consul.sh to load XML IDM configurations into Consul. Go to UI and check if configurations are imported.
4. Remove SKIP_IMPORT_OBJECTS envirnoment variable from docker deployment file.