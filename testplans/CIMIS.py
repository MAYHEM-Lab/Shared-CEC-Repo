import psycopg2,sys,json,csv
from datetime import datetime, date, timedelta
'''
Steps for using this test:
1) fill in creds.json with the db name, db username, db user password, IP, and port of the UCSB CEC cloud.  Details on these values can be found here: https://docs.google.com/document/d/1pLy9exK_w0Rf9pWjBi6xIHS8a5IRQhhoGuzbRZU11zM/edit
2) Also in this file (creds.json) modify the values for the table names: scs_tablename, wsn_tablename, and wsnhr_tablename. Details on these values can be found here: https://docs.google.com/document/d/17r06koVTgnMili2JgptbuHoWTBT9SwBv9LzPh6G68GU/edit
3) Also in this file enter the csv filename to use for spatial and station data respectively (for step 5 below).  WARNING, these files will be overwritten!
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
Manual step
7)	Verify the difference is acceptable
Manual step
8)	Run the automated data collection for both systems for two weeks to test new data collection.
DONE for UCSB CEC Cloud / GSN 9/24/15
9)	Repeat the data extraction and comparison to verify both approaches work to collect data across time
'''
DEBUG = False
max_tests = 7
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
zip: 95710
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
        creds_scsfile = data['spatial_csv_fname']
        creds_wsnfile = data['station_csv_fname']
except:
    print 'Error accessing creds.json file or with its file format.  It must contain the IP, port, login, and password and be in the same directory as this program.'
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
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
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
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
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)


if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)

current_test += 1
if cur.rowcount == max_zips:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed. Zips found {2}, zips expected {3}'.format(current_test,max_tests,cur.rowcount,max_zips)
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
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)


if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)

current_test += 1
if cur.rowcount == max_stations:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests)
if DEBUG:
    for row in cur:
        print row

#4)	Ensure historical data for 2014 and 2015 is loaded: spatial CIMIS
tablename = scstable
sdate = '2014-01-01'
#yesterdays date:
edate = '{0}'.format((datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d'))
sql = "SELECT count(*) FROM {tab} WHERE (to_date({datecol},'YYYY-MM-DD')>=to_date('{sdate}','YYYY-MM-DD') and to_date({datecol},'YYYY-MM-DD')<=to_date('{edate}','YYYY-MM-DD')) and eto>-1 and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3})".format(cols=wsncols,tab=tablename,datecol=datecol,sdate=sdate,edate=edate,tcol=zipcol,z1=zip1,z2=zip2,z3=zip3)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)

if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)

count = cur.fetchone()[0]
if count is None:
    print 'Error extracting count from SQL query {0}'.format(sql)
    print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
    sys.exit(1)

sdt2 = datetime.strptime('2015-01-01','%Y-%m-%d')
sdt = datetime.strptime(sdate,'%Y-%m-%d')
edt = datetime.strptime(edate,'%Y-%m-%d')
#+1day b/c inclusive
dys = (edt-sdt+timedelta(days=1)).days
measurements = count/max_zips

current_test += 1
if dys == measurements:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed.'.format(current_test,max_tests)
if DEBUG:
    print 'count: {0}'.format(count)

#4)	Ensure historical data for 2014 and 2015 is loaded: WSN
tablename = wsntable
sdate = '2014-01-01'
#yesterdays date:
edate = '{0}'.format((datetime.now()-timedelta(days=1)).strftime('%Y-%m-%d'))
sql = "SELECT count(*) FROM {tab} WHERE (to_date({datecol},'YYYY-MM-DD')>=to_date('{sdate}','YYYY-MM-DD') and to_date({datecol},'YYYY-MM-DD')<=to_date('{edate}','YYYY-MM-DD')) and asce_eto>-1 and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3} or {tcol}={z4})".format(cols=wsncols,tab=tablename,datecol=datecol,sdate=sdate,edate=edate,tcol=stationcol,z1=sta1,z2=sta2,z3=sta3,z4=sta4)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

count = cur.fetchone()[0]
if count is None:
    print 'Error extracting count from SQL query {0}'.format(sql)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

sdt2 = datetime.strptime('2015-01-01','%Y-%m-%d')
sdt = datetime.strptime(sdate,'%Y-%m-%d')
edt = datetime.strptime(edate,'%Y-%m-%d')
#subtracting 3 days (and adding 1 for inclusive) for which CIMIS doesn't have data 7/13/14 and 6/7/14 and 05/31/14 for any station
dys = (edt-sdt+timedelta(days=-2)).days
measurements = count/(max_stations)
if DEBUG:
    print sql
    print 'count:',measurements
    print 'days: ',dys
    print 'days since jan 1 2015: ',(edt-sdt2).days
    sdt = datetime.strptime('2014-07-01','%Y-%m-%d')
    edt = datetime.strptime('2014-07-31','%Y-%m-%d')
    print 'days {0}-{1}:{2}'.format(edt,sdt,(edt-sdt+timedelta(days=1)).days)
    print 'days {0}-{1}:{2}'.format(edt,sdt,(edt-sdt+timedelta(days=1)).days*4)

current_test += 1
if dys == measurements:
    print 'Test {0}/{1} passed.'.format(current_test,max_tests)
else: 
    print 'Test {0}/{1} failed.'.format(current_test,max_tests)
if DEBUG:
    print 'count: {0}'.format(count)

#5)	Extract both datasets into csv format for the period March-September 2015
#spatial CIMIS
tablename = scstable
sdate = '2015-03-01'
edate = '2015-09-30'
sql = "SELECT {cols} FROM {tab} WHERE (to_date({datecol},'YYYY-MM-DD')>=to_date('{sdate}','YYYY-MM-DD') and to_date({datecol},'YYYY-MM-DD')<=to_date('{edate}','YYYY-MM-DD')) and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3})".format(cols=scscols,tab=tablename,datecol=datecol,sdate=sdate,edate=edate,tcol=zipcol,z1=zip1,z2=zip2,z3=zip3)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

f = open(creds_scsfile, 'wt')
try:
    writer = csv.writer(f)
    writer.writerow(scscols.split(','))
    for row in cur:
        writer.writerow(row)
except:
    print 'Unable to open and/or write to file {0}'.format(creds_scsfile)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)
finally:
    f.close()
current_test += 1
print 'Test {0}/{1} passed. The station CSV is in {2}'.format(current_test,max_tests,creds_scsfile)

#5)	Extract both datasets into csv format for the period March-September 2015
#WSN
tablename = wsntable
sdate = '2015-03-01'
edate = '2015-09-30'
sql = "SELECT {cols} FROM {tab} WHERE (to_date({datecol},'YYYY-MM-DD')>=to_date('{sdate}','YYYY-MM-DD') and to_date({datecol},'YYYY-MM-DD')<=to_date('{edate}','YYYY-MM-DD')) and ({tcol}={z1} or {tcol}={z2} or {tcol}={z3} or {tcol}={z4})".format(cols=wsncols,tab=tablename,datecol=datecol,sdate=sdate,edate=edate,tcol=stationcol,z1=sta1,z2=sta2,z3=sta3,z4=sta4)
try: 
    retn = cur.execute(sql)
except:
    print 'Error in SQL'
    print sql
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

if cur is None:
    print 'cursor is None: {0} contains no data'.format(tablename)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)

f = open(creds_wsnfile, 'wt')
try:
    writer = csv.writer(f)
    writer.writerow(wsncols.split(','))
    for row in cur:
        writer.writerow(row)
except:
    print 'Unable to open and/or write to file {0}'.format(creds_wsnfile)
    print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
    sys.exit(1)
finally:
    f.close()
current_test += 1
print 'Test {0}/{1} passed. The station CSV is in {2}'.format(current_test,max_tests,creds_wsnfile)
print 'Tests completed and ready for manual steps and comparison against Pow Wow cloud data'
