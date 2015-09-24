import psycopg2,sys,json,csv
from datetime import datetime, date, timedelta
'''
Steps for using this test:
1) fill in creds.json with the db name, db username, db user password, IP, and port of the UCSB CEC cloud.  Details on these values can be found here: https://docs.google.com/document/d/1pLy9exK_w0Rf9pWjBi6xIHS8a5IRQhhoGuzbRZU11zM/edit
2) Also in this file (creds.json) modify the values for the table names: tule75, tule76,tule78. Details on these values can be found here: https://docs.google.com/document/d/17r06koVTgnMili2JgptbuHoWTBT9SwBv9LzPh6G68GU/edit#bookmark=id.usyepka709ep
3) Also in this file enter the csv filename to use for the data respectively (defaults are 75.csv, 76.csv, 78.csv).  WARNING, these files will be overwritten!
3) Run via python TULE.py
'''

'''
TEST
1) Extract all Tule data to from GSN for the three  UCDavis Tule sensors (75,75,78) into CSV files for comparison and import by PowWow CEC cloud
- given there are three sensors, we perform two tests each (extraction and csv writing) for a total of 6 tests
'''

DEBUG = False
max_tests = 6 
current_test = 0
#################################################################
''' supporting functions '''

def gen_test(cur,id,tablename,fname):
    '''  
    Read all data from the database for the columns specified 
    and write them to a CSV file for further testing
    '''
    global current_test

    #1) Extract all Tule data to from GSN for the three  UCDavis Tule sensors (75,75,78) into a CSV file
    sql = "SELECT {cols} FROM {tab} ORDER by date".format(cols=cols,tab=tablename)
    try: 
        retn = cur.execute(sql)
    except:
        print 'Error in SQL:'
        print sql
        print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
        sys.exit(1)

    if cur is None:
        print 'cursor is None: {0} contains no data'.format(tablename)
        print 'Test {0}/{1} failed. Not continuing.'.format(current_test,max_tests) 
        sys.exit(1)
    
    current_test += 1
    print 'Test {0}/{1} passed. TULE sensor {2}'.format(current_test,max_tests,id)
    f = open(fname, 'wt')
    try:
        writer = csv.writer(f)
        writer.writerow(cols.split(','))
        for row in cur:
            writer.writerow(row)
    except:
        print 'Unable to open and/or write to file {0}'.format(creds_scsfile)
        print 'Test {0}/{1} failed.'.format(current_test,max_tests) 
        sys.exit(1)
    finally:
        f.close()
    current_test += 1
    print 'Test {0}/{1} passed. TULE sensor {2}'.format(current_test,max_tests,id)

#################################################


#read in the credentials (service and secret) from simple json file
try:
    with open('creds.json') as data_file:
        data = json.load(data_file)
        creds_db = data['db']
        creds_user = data['user']
        creds_pwd = data['password']
        creds_ip = data['IP']
        creds_port = data['port']
        creds_75 = data['tule75_tablename']
        creds_75file = data['tule75_csv_fname']
        creds_76 = data['tule76_tablename']
        creds_76file = data['tule76_csv_fname']
        creds_78 = data['tule78_tablename']
        creds_78file = data['tule78_csv_fname']
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

cols = 'date,eta,eto,eta_eto,fieldstat,irrig_in,irrig_hrs,irrig_rec_in,irrig_rec_hrs,gapped'
gen_test(cur,75,creds_75,creds_75file)
gen_test(cur,76,creds_76,creds_76file)
gen_test(cur,78,creds_78,creds_78file)
