import urlparse,sys,requests,argparse,sys
from datetime import datetime, timedelta

DEBUG=False
def main():
    '''
    Acquire data from the sensors in a SensMit Mesh: sample queries
    EX: python reqtest.py APIKEY  
	-- past 4 hours (from now) of data
    EX: python reqtest.py --stime "2015-09-20 00:00:00" --etime "2015-09-21 00:00:00" APIKEY  
	-- date range of data
    EX: python reqtest.py --stime "2015-01-25 00:00:00" APIKEY  
	-- all data since start time until now
    Note that a large number of dates will take a long time to return and may 
    take out the server.  Recommendation: no more than 15 days (30secs).
    '''

    parser = argparse.ArgumentParser(description='SensMit/Irrometer Access')
    #required argument
    parser.add_argument('api_key',action='store',help='API KEY')
    parser.add_argument('--stime','-s',action='store',help='start time in YYYY-mm-dd HH:MM:SS in quotes, disregarded if etime is not also set or stime >= etime. If disregared, stime becomes four hours earlier than etime.  We round any stime given back to the earlier hour.')
    parser.add_argument('--etime','-e',action='store',help='end time in YYYY-mm-dd HH:MM:SS in quotes. We round any etime given back to the earlier hour. The default is now. Limit date range to 15 days if possible (will take ~30secs; 30 days = 1min)')
    args = parser.parse_args()

    #extract the datetime from the args if any, zeroing out the seconds
    if args.etime is not None:
        etime = datetime.strptime(args.etime, '%Y-%m-%d %H:%M:%S')
        etime = etime.replace(second=0,microsecond=0)
        if args.stime is not None:
            stime = datetime.strptime(args.stime, '%Y-%m-%d %H:%M:%S')
            stime = stime.replace(second=0,microsecond=0)

        #if stime is None or invalid, set it to 4 hours earlier than etime
        if args.stime is None or etime <= stime:
            stime = etime - timedelta(hours=4)
    else: 
        #if etime is not set in the args, then set it to now (and set stime 2 hours earlier)
        etime = datetime.now()
        etime = etime.replace(second=0,microsecond=0)

        if args.stime is not None:
            stime = datetime.strptime(args.stime, '%Y-%m-%d %H:%M:%S')
            stime = stime.replace(second=0,microsecond=0)

        if args.stime is None or etime <= stime:
            #backup four hours, call this script every hour (takes irrometer over an hour to get data to API some times)
            stime = etime - timedelta(hours=4)
        else:
            stime = datetime.strptime(args.stime, '%Y-%m-%d %H:%M:%S')
            stime = stime.replace(second=0,microsecond=0)
    
    if DEBUG:
        print 'stime: {0}, etime: {1}'.format(stime,etime)
    header = {'Authorization':'ApiKey {0}'.format(args.api_key)}

    #access the meshes, for each pull out the sensors and their data
    #http://www.sensmitweb.com/api/documentation
    meshes = 'http://www.sensmitweb.com/api/v1/meshes'
    r = None
    try:
        r = requests.get(meshes, headers=header)
    except Exception as e:
        print "Error: unable to contact sensmit!"
        sys.exit(1)
    
    if DEBUG:
        print 'Accessing API: {0}'.format(r.url)
        print 'result: {0}\n'.format(r.text)
    res = r.json()
    for obj in res["objects"]:
        mesh_db_id = obj["id"]
        mesh_id = obj["mesh_id"]

        #other API accesses from http://www.sensmitweb.com/api/documentation
        #this accesses the sensmits which has only latest data (not used here)
        #this also has status
        url = 'http://www.sensmitweb.com/api/v1/sensmits'
        payload = {'mesh_id': mesh_db_id}
        r = requests.get(url, headers=header, params=payload)
        if DEBUG:  #this is a big dump
            print 'Accessing API: {0}'.format(r.url)
            print 'result1: {0}\n'.format(r.text)
        jobj = r.json()
        for sensr in jobj["objects"]:
            sensmit_id = sensr["sensmit_id"]
            sensmit_alias = sensr["alias"]
            if sensmit_alias == "":
                sensmit_alias = "None"
            sensmit_status = sensr["status_code"]
            if DEBUG:
                print 'SensorID: {0}; alias: {1}; status: {2}'.format(sensmit_id,sensmit_alias,sensmit_status)

        #access the data elements (sensor data)
        url = '{0}/{1}/data'.format(meshes,mesh_db_id)
        payload = {
            'start_time':stime.strftime('%s'),
            'end_time':etime.strftime('%s'),
            'utc_offset':480
        }
        r = requests.get(url, headers=header, params=payload)
        jobj = r.json()
        if "error" in jobj: 
            print 'Terminating... Error in API query: {0}'.format(r.text)
            sys.exit(1)
        if DEBUG:  #this is a big dump
            print 'Accessing API: {0}'.format(r.url)
            print 'result2: {0}\n'.format(r.text)
    
        #loop through the available sensors (by sensmit_id)
        for sensor in jobj["objects"]:
            if 'sensmit_id' not in sensor:
                print 'Terminating... Error in API query -- sensmit_id key not found: {0}'.format(r.text)
                sys.exit(1)

            sensmit_id = sensor["sensmit_id"]
            if 'seconds' not in sensor:
	        ts = None
            else:
	        ts = datetime.fromtimestamp(sensor["seconds"]).strftime('%Y-%m-%d %H:%M:%S')
            if 'EXT' not in sensor:
                ext = -1 
            else: 
                ext = sensor["EXT"] 
            if 'MO1' not in sensor:
                mo1 = -1 
            else: 
                mo1 = sensor["MO1"] 
            if 'MO2' not in sensor:
                mo2 = -1 
            else: 
                mo2 = sensor["MO2"] 
            if 'MO3' not in sensor:
                mo3 = -1 
            else: 
                mo3 = sensor["MO3"] 
            if 'INT' not in sensor:
                intt = -1 
            else: 
                intt = sensor["INT"] 
            if 'TIP' not in sensor:
                tip = -1 
            else: 
                tip = sensor["TIP"] 
            if 'IRR' not in sensor:
                irr = -1 
            else: 
                irr = sensor["IRR"] 
            if 'CAP' not in sensor:
                cap = -1 
            else: 
                cap = sensor["CAP"] 
            if 'POW' not in sensor:
                poww = -1 
            else: 
                poww = sensor["POW"] 
            print '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}'.format(
                ts,sensmit_id,mo1,mo2,mo3,intt,ext,poww,cap,tip,irr)

######################################
if __name__ == "__main__":
    main()
######################################
