import urlparse,sys,requests,argparse,sys,csv
from datetime import datetime, timedelta

DEBUG = False
def main():
    '''
    Acquire data from two specific sensors in a SensMit Mesh.
    EX: python reqtest2.py -s '2015-01-01 13:00:00' -e '2015-09-27 12:58:10' APIKEY
    EX: python reqtest2.py --printonly -s '2015-08-02 13:00:00' -e '2015-09-27 12:58:10' APIKEY
    EX: python reqtest2.py --printonly APIKEY
    	* without --single_req, we zero out the hour of -s param and get data in 
    	24 hour request chunks.  If -e param is less than 24 hours of -s param,
    	no data will be found ...
        * be careful with --single_req as too large of a date range will place
        a heavy load on the server and take significant time to return...
    EX: python reqtest2.py --single_req --printonly -s '2015-09-26 13:00:00' -e '2015-09-27 12:58:10' APIKEY
    '''
    parser = argparse.ArgumentParser(description='Testfarm SensMit/Irrometer Access')
    #required argument
    parser.add_argument('api_key',action='store',help='API KEY')
    #optional arguments
    parser.add_argument('--stime','-s',action='store',help='start time in YYYY-mm-dd HH:MM:SS in quotes, disregarded if etime is not also set or stime >= etime. If disregared, stime becomes two hours earlier than etime.  We round any stime given back to the earlier hour.')
    parser.add_argument('--etime','-e',action='store',help='end time in YYYY-mm-dd HH:MM:SS in quotes. We round any etime given back to the earlier hour. The default is now.')
    parser.add_argument('--printonly','-p',action='store_true',help='Use to avoid writing to csv file and instead printing to console (only first file)')
    parser.add_argument('--single_request','-r',action='store_true',help='Get data in a single request vs in 24 hour blocks.')
    args = parser.parse_args()
    
    header = {'Authorization':'ApiKey {0}'.format(args.api_key)}

    #access the meshes, for each pull out the sensors and their data
    #http://www.sensmitweb.com/api/documentation
    meshes = 'http://www.sensmitweb.com/api/v1/meshes'
    if DEBUG:
        r = requests.get(meshes, headers=header)
        print r.json()

    #first date with data in the test system: 2014-08-01, MO1 and MO2 for 681 and 682 starts 8/8/14
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
        #backup four hours, call this script every hour (takes irrometer over an hour to get data to API some times)
        stime = etime - timedelta(hours=4)
    if DEBUG:
        print 'start time: {0}, end time: {1}'.format(stime,etime)
        print 'printing to console (only first dataset)? {0}'.format(args.printonly)
        print 'getting data in a single request? {0}'.format(args.single_request)
        
    mesh_db_id = 97
    sens1_id = 681
    sens2_id = 682
    fname = '{0}test.csv'.format(sens1_id)
    f = open(fname,'wt')
    csv1 = csv.writer(f)
    fname = '{0}test.csv'.format(sens2_id)
    if args.printonly:
        print 'ts, MO1, MO2, MO3, INT, EXT, POW, CAP, TIP, IRR'
    else:
        csv1.writerow(['ts','MO1','MO2','MO3','INT','EXT','POW','CAP','TIP','IRR'])
    f2 = open(fname,'wt')
    csv2 = csv.writer(f2)
    if not args.printonly:
        csv2.writerow(['ts','MO1','MO2','MO3','INT','EXT','POW','CAP','TIP','IRR'])
    url = '{0}/{1}/data'.format(meshes,mesh_db_id)
    dts = stime
    if args.single_request:
        dte = etime
    else:
        #restart stime to midnight of stime date
        stime = stime.replace(hour=0,second=0,microsecond=0)
        dte = stime + timedelta(hours=24)
    objs = None
    
    while dte <= etime:
        payload = {
            'start_time':dts.strftime('%s'),
            'end_time':dte.strftime('%s'),
            'utc_offset':480
        }
        print payload
        this_dts = dts
        this_dte = dte
        dts = dte
        dte += timedelta(hours=24)
        r = requests.get(url, headers=header, params=payload)
        objs = r.json()["objects"]
        if len(objs) == 0: #no data in this timespan
            print 'no data {0} {1}'.format(this_dts,this_dte)
            continue
        for sensor in objs:
            if 'seconds' not in sensor or 'id' not in sensor:
                #something is very wrong, skip this sensor entry
                continue
            if sensor['id'] == sens1_id or sensor['id'] == sens2_id:
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
	        ts = datetime.fromtimestamp(sensor["seconds"]).strftime('%Y-%m-%d %H:%M:%S')
                if args.printonly:
                    print '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(
                        ts,mo1,mo2,mo3,intt,ext,poww,cap,tip,irr)
                else:
                    if sensor['id'] == sens1_id:
		        csvwriter = csv1
                    else:
		        csvwriter = csv2
    
                    #write out the data
	            csvwriter.writerow([ts,mo1,mo2,mo3,intt,ext,poww,cap,tip,irr])
    f.close()
    f2.close()
		
######################################
if __name__ == "__main__":
    main()
######################################
