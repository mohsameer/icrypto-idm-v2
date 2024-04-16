import psycopg2
import psycopg2.extras
import datetime
import csv
import re
import json

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
MOBILE_REGEX = re.compile(r"^(\+)?(0|27)( )?([5-9])([0-9])( )?([0-9]{3})( )?([0-9]{4})$")
ID_NUMBER_REGEX = re.compile(r"(((\d{2}((0[13578]|1[02])(0[1-9]|[12]\d|3[01])|(0[13456789]|1[012])(0[1-9]|[12]\d|30)|02(0[1-9]|1\d|2[0-8])))|([02468][048]|[13579][26])0229))(( |-)(\d{4})( |-)([01]8((( |-)\d{1})|\d{1}))|(\d{4}[01]8\d{1}))")


report_time = datetime.datetime.now()
report_time_formatted = report_time.strftime('%Y%m%d%H%M%S')
print("Starting generation of reports at ", report_time)

postgress_connection = None
users_data = None
try:
	postgress_connection = psycopg2.connect(database="midpoint", user='midpoint', password='XXXXXXXXXXXXXX', host='localhost', port= '5432')
	cursor = postgress_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	cursor.execute("select version()")
	version = cursor.fetchone()
	print("Postgress connected: ", version['version'])

	cursor.execute("""select
                     t.familyname_norm as familyname,
                     t.givenname_norm as givenname,
                     t.telephonenumber as mobile,
                     t.emailaddress as email,
                     max(case when (t.ext_name ='saID') then t.stringvalue end) as said,
                     max(case when (t.ext_name ='sparkleData') then t.stringvalue end) as sparkledata,
                     max(case when (t.ext_name ='profitData') then t.stringvalue end) as profitdata,
                     max(case when (t.ext_name ='hrFeedData') then t.stringvalue end) as hrfeeddata,
                     max(case when (t.ext_name ='iaaData') then t.stringvalue end) as iaadata,
                     max(case when (t.ext_name ='hrEmployeeIsActive') then t.stringvalue end) as hremployeeisactive,
                     max(case when (t.ext_name ='hrIsStaff') then t.stringvalue end) as hrisstaff,
                     max(case when (t.ext_name ='isSTI') then t.stringvalue end) as issti,
                     STRING_AGG(case when (t.ext_name = 'mobiles') then t.stringvalue end, ';') as mobiles,
                     STRING_AGG(case when (t.ext_name = 'emails') then t.stringvalue end, ';') as emails
                     from (select
                         u.oid,
                          u.familyname_norm,
                          u.givenname_norm,
                          SPLIT_PART(item.itemname, '#', 2) as ext_name,
                          ext.stringvalue,
                         f.telephonenumber,
                         f.emailaddress

                        from m_user as u
                          inner join m_object_ext_string as ext
                            on u.OID = ext.owner_oid
                          left join m_ext_item as item
                            on ext.item_id = item.id
                          left join m_focus as f
                            on f.oid = u.OID
                       ) as t
                   group by t.oid, t.familyname_norm,t.givenname_norm, t.telephonenumber, t.emailaddress""")
	users_data = cursor.fetchall()
	print("Users read count: ", str(len(users_data)))
except Exception as error:
	print(error)
	exit()
finally:
	if postgress_connection:
		postgress_connection.close()

no_mobile_number = []
no_email_address = []
invalid_mobile_number = []
invalid_email_address = []
invalid_saID_number = []
no_familyname = []
no_givenname = []
account_on_sparkle_and_profit = []
on_profit_missing_partyid = []
on_profit_missing_sn = []
on_sparkle_missing_surname = []
multiple_surnames = []
hr_feed_inactive = []

# Enrich rows
for row in users_data:
	row['OnHRData'] = ('Yes' if row['hrfeeddata'] else 'No')
	row['OnSparkle'] = ('Yes' if row['sparkledata'] else 'No')
	row['OnIAA'] = ('Yes' if row['iaadata'] else 'No')
	row['OnProFit'] = ('Yes' if row['profitdata'] else 'No')
	row['OnBothProFitAndSparkle'] = ('Yes' if row['profitdata'] and row['sparkledata'] else 'No')

for row in users_data:
	if not row['mobile'] and not row['mobiles']:
		no_mobile_number.append(row)
	elif row['mobile'] and not MOBILE_REGEX.match(row['mobile']):
		invalid_mobile_number.append(row)
	if not row['email'] and not row['emails']:
		no_email_address.append(row)
	elif row['email'] and not EMAIL_REGEX.match(row['email']):
		invalid_email_address.append(row)
	# TODO: check for passport number or vat registration
	if not ID_NUMBER_REGEX.match(row['said']):
		invalid_saID_number.append(row)
	if not row['familyname']:
		no_familyname.append(row)
	if not row['givenname']:
		no_givenname.append(row)

	row_profit_data = None
	if row['profitdata']:
		row_profit_data = json.loads(row['profitdata'])
	row_sparkle_data = None
	if row['sparkledata']:
		row_sparkle_data = json.loads(row['sparkledata'])
	
	#account_on_sparkle_and_profit
	if row_profit_data and row_sparkle_data:
		account_on_sparkle_and_profit.append(row)
	#on_profit_missing_partyid
	if row_profit_data and row_profit_data[0]:
		if 'partyid' not in row_profit_data[0] or not row_profit_data[0]['partyid']:
			on_profit_missing_partyid.append(row)
	#multiple_surnames
	#on_profit_missing_sn
	#on_sparkle_missing_surname
	tmp_surname = None
	if row_profit_data and row_profit_data[0]:
		if 'sn' in row_profit_data[0] and row_profit_data[0]['sn']:
			tmp_surname = row_profit_data[0]['sn']
		else:
			on_profit_missing_sn.append(row)
	if row_sparkle_data:
		for record in row_sparkle_data:
			if 'surname' in record and record['surname']:
				if not tmp_surname:
					tmp_surname = record['surname']
				elif tmp_surname.lower() != record['surname'].lower() and row not in multiple_surnames:
					multiple_surnames.append(row)
			elif row not in on_sparkle_missing_surname:
				on_sparkle_missing_surname.append(row)




def generate_csv_from_array(name, dict_array):
	with open(report_time_formatted + "_" + name + ".csv", 'w', encoding='utf8', newline='') as output_file:
		print("Saving report ", name, " total records: ", str(len(dict_array)))
		fc = csv.DictWriter(output_file, fieldnames=set().union(*(d.keys() for d in dict_array)))
		fc.writeheader()
		fc.writerows(dict_array)

generate_csv_from_array("UsersAll", users_data)
generate_csv_from_array("UsersMissingMobileNumber", no_mobile_number)
generate_csv_from_array("UsersInvalidMobileNumber", invalid_mobile_number)
generate_csv_from_array("UsersMissingEmailAddress", no_email_address)
generate_csv_from_array("UsersInvalidEmailAddress", invalid_email_address)
generate_csv_from_array("UsersInvalidIDField", invalid_saID_number)
generate_csv_from_array("UsersMissingGivenName", no_givenname)
generate_csv_from_array("UsersMissingFamilyName", no_familyname)
generate_csv_from_array("UsersOnProfitAndSparkle", account_on_sparkle_and_profit)
generate_csv_from_array("UsersOnProfitMissingPartyid", on_profit_missing_partyid)
generate_csv_from_array("UsersOnProfitMissingSurname", on_profit_missing_sn)
generate_csv_from_array("UsersOnSparkleMissingSurname", on_sparkle_missing_surname)
generate_csv_from_array("UsersMultipleSurnames", multiple_surnames)

print("Time elapsed: ", datetime.datetime.now() - report_time)
