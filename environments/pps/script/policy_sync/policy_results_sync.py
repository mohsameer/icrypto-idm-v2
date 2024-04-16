import json
import sys
import requests
import logging
from urllib.parse import urljoin, urlencode, urlparse, urlunparse
from elasticsearch import Elasticsearch
import elasticsearch
import base64

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)
es_logger = elasticsearch.logger
es_logger.setLevel(elasticsearch.logging.WARNING)

# IDM Details - read only user
IDM_AUTH_HEADER_VALUE = "Basic " + base64.b64encode("user:password".encode("ascii")).decode("ascii")
IDM_SEARCH_URL = "http://localhost:8080/midpoint/ws/services/scim2/Users?"
STEP = 30

# Elastic
ELASTIC_URL="http://localhost:9200"
ELASTIC_INDEX_NAME="policy-results"

DELETE_PREVIOUS_INDEX=True

elastic_index_mapping = {
    "mappings": {
        "properties": {
            "firstName": {
                "type": "text" # formerly "string"
            },
            "lastName": {
                "type": "text"
            }
        }
    }
}

elastic_index_mapping = {
    "mappings": {
        "dynamic": True
    }
}

def get_from_idm_by_user_id(startIndex, count):
    try:
        query_params = {
            "startIndex":startIndex,
            "count":count,
            "attributes":"enrollmentPolicyResult,id",
            "filter": "enrollmentPolicyResult pr"
        }
        response = requests.get(IDM_SEARCH_URL + urlencode(query_params),
                                 headers={"Authorization": IDM_AUTH_HEADER_VALUE})
        if response.status_code != 200:
            logging.error(response.status_code)
            logging.error(response.text)
            logging.error("Response not 200")
            return 0,{}
        data = {}
        resurces = response.json()
        totalResults = resurces["totalResults"]
        if resurces["totalResults"] > 0:
            for resource in resurces["Resources"]:
                if "urn:ietf:params:scim:schemas:extension:custom:2.0:User" in resource["schemas"]:
                    data[resource["id"]] = json.loads(resource["urn:ietf:params:scim:schemas:extension:custom:2.0:User"]["enrollmentPolicyResult"])
            # return user data found in idm as presented above
        return totalResults,data
    except Exception as e:
        # dumb retry for connectivity exception
        logging.error(e)
        raise

def connect_elastic():
    es = Elasticsearch(ELASTIC_URL)
    return es


processed_count = 0
total_results = 1
es = connect_elastic()
if DELETE_PREVIOUS_INDEX:
    logging.info(f"Deleting index: {ELASTIC_INDEX_NAME}")
    es.indices.delete(index=ELASTIC_INDEX_NAME, ignore=[400, 404])
if not es.indices.exists(index=ELASTIC_INDEX_NAME):
    es.indices.create(index=ELASTIC_INDEX_NAME)
while total_results > processed_count:
    if processed_count % 100 == 0:
        logging.info(f"Processed count: {processed_count}")
    total_results, policies = get_from_idm_by_user_id(processed_count + 1, STEP)
    if total_results == 0:
        logging.info("No results found")
        break
    # For testing from local file
    # with open("policy.json") as f:
    #     policy = json.load(f)
    #     policies = {"test123": policy}
    #     totalResults =0
    processed_count += len(policies)
    for id in policies:
        es.index(index=ELASTIC_INDEX_NAME, id=id, body=policies[id])


