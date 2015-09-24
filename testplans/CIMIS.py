import psycopg2,sys,json
'''
Steps for using this test:
1) fill in creds.json with the db name, db username, db user password, IP, and port of the UCSB CEC cloud.  Details on these values can be found here: https://docs.google.com/document/d/1pLy9exK_w0Rf9pWjBi6xIHS8a5IRQhhoGuzbRZU11zM/edit
2) Also in this file (creds.json) modify the values for the table names: scs_tablename, wsn_tablename, and wsnhr_tablename. Details on these values can be found here: https://docs.google.com/document/d/17r06koVTgnMili2JgptbuHoWTBT9SwBv9LzPh6G68GU/edit
3) Run via python CIMIS.py
'''

'''
TEST
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
DEBUG = False
max_tests = 5
current_test = 0

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
max_zips = 3 #this much match number of zip variables below
zip1 = 93221
zip2 = 95616
zip3 = 93710
zips = '{0},{1},{2}'.format(zip1,zip2,zip3)
max_stations = 4 #this much match number of stat variables below
sta1=86
sta2=169
sta3=6
sta4=80
stations = '{0},{1},{2},{3}'.format(sta1,sta2,sta3,sta4)
print 'CIMIS Zips ({0}) and Stations ({1}) defined for sample fields.'.format(zips,stations)

current_test += 1
print 'Test {0}/{1} passed.'.format(current_test,max_tests) 

#read in the credentials (service and secret) from simple json file
try:
    with open('creds.json') as data_file:
        data = json.load(data_file)
        creds_db = data['db']
        creds_user = data['user']
        creds_pwd = data['password']
        creds_ip = data['IP']
        creds_port = data['port']
        creds_scs = data['scs_tablename']
        creds_wsn = data['wsn_tablename']
        creds_wsnhr = data['wsnhr_tablename']
except:
    print 'Error accessing creds.json file or with its file format.  It must contain the IP, port, login, and password and be in the same directory as this program.'
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)

params = {
  'database': creds_db,
  'user': creds_user,
  'password': creds_pwd,
  'host': creds_ip,
  'port': creds_port,
}
scstable = creds_scs
wsntable = creds_wsn
wsnhrtable = creds_wsnhr

#access remote GSN database on UCSB CEC Cloud
conn = None
try:
    conn = psycopg2.connect(**params)
except:
    print 'Unable to connect to the remote GSN database on the UCSB CEC Cloud'
    print 'Check your settings in creds.json'
    print params
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)

cur = conn.cursor()

testdate = '2015-09-01'
#1b.	Ensure the GSN/CIMIS connector has been configured for those stations.
#2)	Verify ET via spatial API has been loaded for those locations
scscols = 'date,zip,eto'
datecol = 'date'
zipcol = 'zip'
tablename = scstable
sql = "SELECT {cols} FROM {tab} WHERE to_date({datecol},'YYYY-MM-DD')=to_date('{tdate}','YYYY-MM-DD') and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3})".format(cols=scscols,tab=tablename,datecol=datecol,tdate=testdate,tcol=zipcol,z1=zip1,z2=zip2,z3=zip3)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL: {0}'.format(sql)
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)


if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)

current_test += 1
if cur.rowcount == max_zips:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed.'.format(current_test,max_tests)
if DEBUG:
    for row in cur:
        print row

#3)	Verify ET and daily station data has been loaded for those stations
wsncols = 'date,station,asce_eto,eto'
datecol = 'date'
stationcol = 'station'
tablename = wsntable
sql = "SELECT {cols} FROM {tab} WHERE to_date({datecol},'YYYY-MM-DD')=to_date('{tdate}','YYYY-MM-DD') and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3} or {tcol}={z4})".format(cols=wsncols,tab=tablename,datecol=datecol,tdate=testdate,tcol=stationcol,z1=sta1,z2=sta2,z3=sta3,z4=sta4)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL: {0}'.format(sql)
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)


if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} passed.'.format(current_test,max_tests) 
    sys.exit(1)

current_test += 1
if cur.rowcount == max_stations:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed.'.format(current_test,max_tests)
if True:
    for row in cur:
        print row
