FROM python:3.10.6

RUN apt-get update \
    && apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev unixodbc-dev \
	&& pip install python-ldap requests couchbase pyodbc flask jproperties psycopg2
	
COPY . /

RUN mkdir reports

CMD ["python3", "server.py"]