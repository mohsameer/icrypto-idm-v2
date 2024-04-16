import requests
import base64
import json
import logging
from couchbase.cluster import Cluster, ClusterOptions, QueryOptions, ClusterTimeoutOptions
from couchbase.auth import PasswordAuthenticator
from datetime import timedelta
import ldap
import pyodbc
import csv
import hashlib
from jproperties import Properties

configs = Properties()

with open('env.properties', 'rb') as config_file:
    configs.load(config_file)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p",
)

s = hashlib.sha3_256()
logging.info(s.name)
logging.info(s.digest_size)

DRY_RUN=configs.get("DRY_RUN").data

logging.info("DRY_RUN %s", DRY_RUN)

IDM_USERNAME=configs.get("IDM_USERNAME").data
IDM_PASSWORD=configs.get("IDM_PASSWORD").data
IDM_AUTH_HEADER_VALUE = f"Basic " + base64.b64encode(f"{IDM_USERNAME}:{IDM_PASSWORD}".encode("utf-8")).decode("ascii")
IDM_SEARCH_URL=configs.get("IDM_SEARCH_URL").data

logging.info("IDM_USERNAME %s", IDM_USERNAME)
logging.info("IDM_PASSWORD %s", IDM_PASSWORD)
logging.info("IDM_AUTH_HEADER_VALUE %s", IDM_AUTH_HEADER_VALUE)
logging.info("IDM_SEARCH_URL %s", IDM_SEARCH_URL)

CB_URL=configs.get("CB_URL").data
CB_USER=configs.get("CB_USER").data
CB_PASS=configs.get("CB_PASS").data
CB_BUCKET=configs.get("CB_BUCKET").data

logging.info("CB_URL %s", CB_URL)
logging.info("CB_USER %s", CB_USER)
logging.info("CB_PASS %s", CB_PASS)
logging.info("CB_BUCKET %s", CB_BUCKET)

LDAP_HOST=configs.get("LDAP_HOST").data
LDAP_BIND_DN=configs.get("LDAP_BIND_DN").data
LDAP_PASSWORD=configs.get("LDAP_PASSWORD").data

logging.info("LDAP_HOST %s", LDAP_HOST)
logging.info("LDAP_BIND_DN %s", LDAP_BIND_DN)
logging.info("LDAP_PASSWORD %s", LDAP_PASSWORD)

IAA_URL=configs.get("IAA_URL").data
IAA_USER=configs.get("IAA_USER").data

logging.info("IAA_URL %s", IAA_URL)
logging.info("IAA_USER %s", IAA_USER)

HR_USER=configs.get("HR_USER").data
HR_URL=configs.get("HR_URL").data
HR_PASSWORD=configs.get("HR_PASSWORD").data
HR_DATABASE=configs.get("HR_DATABASE").data

logging.info("HR_USER %s", HR_USER)
logging.info("HR_URL %s", HR_URL)
logging.info("HR_PASSWORD %s", HR_PASSWORD)
logging.info("HR_DATABASE %s", HR_DATABASE)

global ldap_conn
global cb_cluster
global hr_conn
global hr_cursor

def connectLDAP():
    logging.info("LDAP connecting...")
    ldap_conn = ldap.initialize(LDAP_HOST)
    ldap_conn.set_option(ldap.OPT_REFERRALS,0)
    ldap_conn.simple_bind_s(LDAP_BIND_DN, LDAP_PASSWORD)
    logging.info("LDAP connected")

def connectCOUCHBASE():
    logging.info("COUCHBASE connecting...")
    timeout_options=ClusterTimeoutOptions(query_timeout=timedelta(seconds=72000))
    cb_cluster = Cluster(CB_URL, ClusterOptions(PasswordAuthenticator(CB_USER, CB_PASS), timeout_options=timeout_options))
    cb_bucket = cb_cluster.bucket(CB_BUCKET)
    logging.info("COUCHBASE connected")

def connectHRFEED():
    logging.info("HR_FEED connecting...")
    hr_conn = pyodbc.connect("DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={0}; database={1}; \
        trusted_connection=yes;UID={2};PWD={3}".format(HR_URL,HR_DATABASE,HR_USER,HR_PASSWORD))
    hr_cursor = hr_conn.cursor()
    logging.info("HR_FEED connected")

def getAllIDMEntriesFromCouchbaseBySAID(id):
    sql_query = 'select userId, saID, username, `password`, REPLACE(meta().id, "idm_", "") as id from `icrypto_persistent_ha` where saID = $1'
    row_iter = cb_cluster.query(sql_query,QueryOptions(positional_parameters=[id]))
    row_iter_results = []
    for row in row_iter:
        row_iter_results.append(row)
    return row_iter_results

def getAllIDMEntriesFromCouchbaseByUsername(username):
    sql_query = 'select userId, saID, username, `password`,  REPLACE(meta().id, "idm_", "") as id from `icrypto_persistent_ha` where username = $1'
    row_iter = cb_cluster.query(sql_query,QueryOptions(positional_parameters=[username]))
    row_iter_results = []
    for row in row_iter:
        row_iter_results.append(row)
    return row_iter_results

def getFromIDMByUserId(icryptoUserId):
    try:
        response = requests.post(IDM_SEARCH_URL,
                                 json={"filter": "icryptoUserId eq \"{id}\"".replace("{id}", icryptoUserId)},
                                 headers={"Authorization": IDM_AUTH_HEADER_VALUE})
        if response.json()["totalResults"] > 0:
            # return user data found in idm as presented above
            return response.json()["Resources"][0]["urn:ietf:params:scim:schemas:extension:custom:2.0:User"]
        else:
            # Not found in IDM
            return None
    except Exception as e:
        logging.error("Exception for icryptoUserId " + str(icryptoUserId) + ": " + str(e))
        raise

def getFromIAAByIdentity(idnumber):
    try:
        response = requests.post(IAA_URL,
                                 json={"idNumber": "{}".format(idnumber), "passportNumber": "{}".format(idnumber)},
                                 headers={"iv-user": IAA_USER}).json()
        return response
    except Exception as e:
        return None

def getFromLDAPByIdentity(idnumber):
    result = ldap_conn.search_s(
        'ou=Users,dc=ppspar,DC=PPSDMN',
        ldap.SCOPE_SUBTREE,
        '(|(identitynumber={})(passportnumber={}))'.format(idnumber, idnumber)
    )
    return result

def getFromLDAPByUsername(username):
    result = ldap_conn.search_s(
        'ou=Users,dc=ppspar,DC=PPSDMN',
        ldap.SCOPE_SUBTREE,
        '(uid={})'.format(username)
    )
    return result

def getFromLDAPPolicyDirectoryByUsername(username):
    result = ldap_conn.search_s(
        'cn=Users,SECAUTHORITY=DEFAULT',
        ldap.SCOPE_SUBTREE,
        '(principalName={})'.format(username)
    )
    return result

def getFromLDAPUserRolesByDN(userDN):
    result = ldap_conn.search_s(
        'dc=ppspar,DC=PPSDMN',
        ldap.SCOPE_SUBTREE,
        '(member={})'.format(userDN)
    )
    return result

def getFromHRByIdentity(idnumber):
    sql_query = 'select * from [stage_Workflow].[dbo].[VW_SCUBED_IDM_INTEGRATION] where [EmployeeSerial] is not null and [employeeIDNumber] = {};'.format(idnumber)
    rows = hr_cursor.execute(sql_query).fetchall()
    return rows

def hashPassword(password):
    s.update(str.encode(password))
    return s.hexdigest()

def processFile(CSV_FILENAME):
    if not DRY_RUN:  
        connectCOUCHBASE()      
        connectLDAP()        
        connectHRFEED()

    IDNUMBER_LIST = []
    with open(CSV_FILENAME, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            IDNUMBER_LIST.append(row[0])
    logging.info("%d idnumbers read from CSV", len(IDNUMBER_LIST))    

    results_all = []    
    for idnumber in IDNUMBER_LIST:        
        results = {}
        results['issues'] = []
        results['csv_identity_number'] = idnumber

        if DRY_RUN:
            results['issues'].append("THIS IS DRY RUN")
            results_all.append(results)
            logging.info(results)
            continue

        # Check COUCHBASE by IDENTITY NUMBER
        cb_results_by_id_number = getAllIDMEntriesFromCouchbaseBySAID(idnumber)
        results['couchbase_number_of_records_by_identity'] = len(cb_results_by_id_number)
        if len(cb_results_by_id_number) != 1:
            results['issues'].append("INVALID NUMBER OF COUCHBASE RECORDS FOUND FOR IDENTITY NUMBER")
            continue
        results['couchbase_username'] = cb_results_by_id_number[0]['username']
        results['couchbase_userId'] = cb_results_by_id_number[0]['id']
        if 'password' in cb_results_by_id_number[0]:
            results['couchbase_password'] = cb_results_by_id_number[0]['password']
        else:
            results['issues'].append("PASSWORD NOT SET IT COUCHBASE")

        # Check COUCHBASE by USERNAME
        cb_results_by_username = getAllIDMEntriesFromCouchbaseByUsername(results['couchbase_username'])
        results['couchbase_number_of_records_by_username'] = len(cb_results_by_username)
        if len(cb_results_by_username) != 1:
            results['issues'].append("INVALID NUMBER OF COUCHBASE RECORDS FOUND FOR USERNAME")
            continue

        # Check IDM by ICRYPTO USER ID
        idm_result_by_userId = getFromIDMByUserId(results['couchbase_userId'])
        if idm_result_by_userId is None:
            results['issues'].append("NO IDM ACCOUNT FOUND FOR ICRYPTOUSERID")
            continue
        results['idm_username'] = idm_result_by_userId['username']
        results['idm_identity_number'] = idm_result_by_userId['saID']

        # Check IAA by IDENTITY NUMBER
        iaa_result_by_id_number = getFromIAAByIdentity(results['idm_identity_number'])
        if iaa_result_by_id_number is None:
            results['iaa_number_of_records_by_identity'] = 0
        elif iaa_result_by_id_number and len(iaa_result_by_id_number) != 1:
            results['issues'].append("INVALID NUMBER OF IAA USER RECORDS FOUND FOR IDENTITY NUMBER")
            results['iaa_number_of_records_by_identity'] = len(iaa_result_by_id_number)
        else:
            results['iaa_identity_number'] = iaa_result_by_id_number[0]['idNumber']
            results['iaa_passport_number'] = iaa_result_by_id_number[0]['passportNumber']

        # Check LDAP by IDENTITY NUMBER
        ldap_result_by_id_number = getFromLDAPByIdentity(results['idm_identity_number'])
        results['ldap_number_of_records_by_identity'] = len(ldap_result_by_id_number)
        if len(ldap_result_by_id_number) != 1:
            results['issues'].append("INVALID NUMBER OF LDAP USER RECORDS FOUND FOR IDENTITY NUMBER")
            continue
        else:
            results['ldap_dn'] = ldap_result_by_id_number[0][0]
            results['ldap_username'] = ldap_result_by_id_number[0][1]['uid'][0].decode("utf-8")
            if 'userPassword' in ldap_result_by_id_number[0][1]:
                results['ldap_password'] = hashPassword(ldap_result_by_id_number[0][1]['userPassword'][0].decode("utf-8"))
            else:
                results['issues'].append("PASSWORD NOT SET IN LDAP")

        # Check LDAP by USERNAME
        ldap_result_by_username = getFromLDAPByUsername(results['idm_username'])
        results['ldap_number_of_records_by_username'] = len(ldap_result_by_username)
        if len(ldap_result_by_username) != 1:
            results['issues'].append("INVALID NUMBER OF LDAP USER RECORDS FOUND FOR USERNAME")
            continue

        # Check LDAP user groups by DN
        ldap_result_by_groups = getFromLDAPUserRolesByDN(results['ldap_dn'])
        results['ldap_number_of_roles_by_dn'] = len(ldap_result_by_groups)
        if len(ldap_result_by_groups) != 1:
            results['issues'].append("LDAP USER IN MORE OR LESS THAN 1 ROLE")
        results['ldap_roles'] = []
        for role in ldap_result_by_groups:
            results['ldap_roles'].append(role[0])

        # Check HR_FEED by IDENTITY NUMBER
        hr_result_by_id_number = getFromHRByIdentity(results['idm_identity_number'])
        results['hr_records_count'] = len(hr_result_by_id_number)

        # misc
        if 'couchbase_password' in results and 'ldap_password' in results and results['couchbase_password'] != results['ldap_password']:
            results['issues'].append("PASSWORD MISSMATCH BETWEEN IDM AND LDAP")

        if results['couchbase_username'] != results['ldap_username']:
            results['issues'].append("USERNAME MISSMATCH BETWEEN IDM AND LDAP")
        results_all.append(results)
        logging.info(results)
    
    return results_all
