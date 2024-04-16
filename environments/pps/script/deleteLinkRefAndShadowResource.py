import psycopg
import re

RESOURCE_TO_UNLINK= 'dabfcbe2-42c2-4611-8df0-745cbb224148'
DB_HOST='172.17.0.1'
DB_NAME='midpoint'
DB_USER='midpoint'
DB_PASS='test123'

PATTERN='linkRef oid="([a-zA-Z0-9_.-]*)"'

connstr = f"user={DB_USER} password={DB_PASS} host={DB_HOST} port=5432 dbname={DB_NAME}"

def get_shadow_to_delete(conn, shadow_oids):
    shadows_to_delete = []
    with conn.cursor() as cursor_shadow:
        for shadow_oid in shadow_oids:
            shadow_query = f"select resourceref_targetoid from m_shadow where oid = '{shadow_oid}';"
            cursor_shadow.execute(shadow_query)
            results_shadow = cursor_shadow.fetchall()
            for resource_oid in results_shadow:
                if resource_oid[0] == RESOURCE_TO_UNLINK:
                    shadows_to_delete.append(shadow_oid)
    return shadows_to_delete

def delete_shadow(conn, shadow_oid):
    print(f"Delete shadow {shadow_oid}")
    if shadow_oid is not None and shadow_oid != "":
        with conn.cursor() as cur:
            delete_query = f"delete from m_shadow where oid = '{shadow_oid}';"
            cur.execute(delete_query)

def modify_reflink(conn, shadow_oid, oid, fullobject):
    print(f"Delete refLink for shadow {shadow_oid} for user {oid}")
    xml_str = fullobject.decode('utf-8')
    regex = re.compile(f"<linkRef oid=\"{shadow_oid}\".*/>", re.MULTILINE)
    result_text = regex.sub('', xml_str)
    query = f"UPDATE m_object SET fullobject = (%s) where objecttypeclass=10 and oid='{oid}'"
    with conn.cursor() as cur:
        cur.execute(query,(result_text.encode(),))

# Connect to the database
with psycopg.connect(connstr) as conn:

    # Create a cursor object
    with conn.cursor() as cursor:

        query = "select oid,fullobject from m_object where objecttypeclass = 10;"
        cursor.execute(query)

        # Fetch the results
        results = cursor.fetchall()

        # Do something with the results
        for row in results:
            oid = row[0]
            xml_object = row[1]
            matches = re.findall(PATTERN, xml_object.decode('utf-8'),re.DOTALL)
            shadows_to_delete = get_shadow_to_delete(conn, matches)
            for shadow_oid in shadows_to_delete:
                modify_reflink(conn, shadow_oid, oid, xml_object)
                delete_shadow(conn, shadow_oid)
