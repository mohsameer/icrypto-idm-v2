import requests
import csv
import threading

IDM_AUTH_HEADER_VALUE = "Basic QWRtaW5pc3RyYXRvcjpiZ3RqTmpGN3lOd2Y2d3RA"
IDM_SEARCH_URL = "https://idm.pps.co.za/midpoint/ws/services/scim2/Users/.search"
IDM_SEARCH_BODY = '{ "filter": }'
IDM_DELETE_URL = "https://idm.pps.co.za/midpoint/ws/services/scim2/Users/{id}"

CSV_FILENAME = "sti_cleanup.csv"

THREADS_NUMBER = 5
IDNUMBER_LIST = []

with open(CSV_FILENAME, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        IDNUMBER_LIST.append(row[0])
def deleteByIdNumbers(idnumbers):
    for idnumber in idnumbers:
        try:
            response = requests.post(IDM_SEARCH_URL,
                                     json={"filter": "saID eq \"{id}\"".replace("{id}", idnumber)},
                                     headers={"Authorization": IDM_AUTH_HEADER_VALUE})
            if(response.json()["totalResults"] == 1):
                idm_id = response.json()["Resources"][0]["id"]
                response_delete = requests.delete(IDM_DELETE_URL.replace("{id}", idm_id),
                                                  headers={"Authorization": IDM_AUTH_HEADER_VALUE})
                print("Deleting " + idm_id + ", result: " + str(response_delete.status_code))
            else:
                print("ERROR: more or less than one result for id " + idnumber)
        except Exception as e:
            print("Exception for idnumber " + str(idnumber) + ": " + str(e))
            deleteByIdNumbers([idnumber])

THREADS = []
for x in range(THREADS_NUMBER):
    start = int(0 + (len(IDNUMBER_LIST)/THREADS_NUMBER) * x)
    end = int((len(IDNUMBER_LIST)/THREADS_NUMBER) * (x+1) - 1)
    print("T" + str(x) + " start:" + str(start))
    print("T" + str(x) + " end:" + str(end))
    t = threading.Thread(target=deleteByIdNumbers, args=(IDNUMBER_LIST[start:end],))
    t.start()
    THREADS.append(t)

for t in THREADS:
    t.join()

