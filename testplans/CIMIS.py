import psycopg2,sys,json

'''
1)	Configure the system to have data for the same area
a.	Creating some sample fields near CIMIS stations. The stations to be used will be #86 and #169 in Visalia near the southern test sites and station #6 in Davis near the northern test sites. Station #80 at Fresno State will be used as reference location.
b.	Ensure the GSN/CIMIS connector has been configured for those stations.
2)	Verify ET via spatial API has been loaded for those locations
3)	Verify ET and daily station data has been loaded for those stations
4)	Ensure historical data for 2014 and 2015 is loaded
5)	Extract both datasets into csv format for the period March-September 2015
6)	Create excel file with data comparison and computing the difference %
7)	Verify the difference is acceptable
8)	Run the automated data collection for both systems for two weeks to test new data collection.
9)	Repeat the data extraction and comparison to verify both approaches work to collect data across time
'''

#1) Sample fields near CIMIS stations
''' Email from Stan/PowWow 9/21/15
"name","lat","long"
"CIMIS 86",36.360630441166,-119.059344166572
zip: 93221
"CIMIS 86 Nearby",36.3603400441902,-119.061592492476
zip: 93221
"CIMIS 6",38.5357723817152,-121.776633863283
zip: 95616
"CIMIS 80",36.8197469944076,-119.744297433601
zip: 95616
'''
zips = '93221,95616,93710'
stations = '86,169,6,80'

#read in the credentials (service and secret) from simple json file
try:
    with open('creds.json') as data_file:
        data = json.load(data_file)
        creds_db = data['db']
        creds_user = data['user']
        creds_pwd = data['password']
        creds_ip = data['IP']
        creds_port = data['port']
except:
    print 'Error accessing creds.json file or with its file format.  It must contain the IP, port, login, and password and be in the same directory as this program.'
    sys.exit(1)

params = {
  'database': creds_db,
  'user': creds_user,
  'password': creds_pwd,
  'host': creds_ip,
  'port': creds_port
}
scstable = 'cimis_scs5'
wsntable = 'cimis_wsn4'
wsnhrtable = 'cimis_wsnhr4'
conn = psycopg2.connect(**params)
cur = conn.cursor()
tablename = scstable
retn = cur.execute('SELECT * FROM {0}'.format(tablename))
if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    sys.exit(1)
for row in cur:
    print row

