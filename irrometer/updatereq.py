import urlparse,sys,requests,argparse,sys,csv,os,unicodedata
from datetime import datetime, timedelta
#process_files requires os commands: diff, awk, mv, rm, cat

DEBUG = False

######################################
def process_files(fname,fnamenew,fnameout,dont_append=False):
    #Step 2) append diff fnamenew and/to sensor1/2_fname
    #use double curly braces to insert a curly brace in a string processed by format
    #we overwrite fnameout here if any
    os.system("diff {0} {1}| grep '^>'|awk -F'> ' '{{print $2}}' > {2}".format(fname,fnamenew,fnameout))
    if DEBUG:
        res = os.popen("cat {0}".format(fnameout)).read()
        print 'DEBUG: adding diffs: '
        print res

    #append fnameout to fname
    if dont_append:
        print 'testing: not appending to file {0}'.format(fname)
    else:
        os.system("cat {0} >> {1}".format(fnameout,fname))
        #sanity check - there should be nothing in fnameout file
        os.system("diff {0} {1} |grep '^>'|awk -F'> ' '{{print $2}}' > {2}".format(fname,fnamenew,fnameout))
        if os.path.getsize("{0}".format(fnameout)) != 0:
            print 'ERROR: difference between {0} and {1} should be 0, it is {2}'.format(fname,fnamenew, os.path.getsize("{0}".format(fnameout)))
            res = os.system("cat {0}".format(fnameout))
            print res
        elif DEBUG:
            print 'Sanity check passed. Cleaning up...'
    #cleanup
    #leave fnameout for sanity check
    #os.remove("{0}".format(fnameout))
    os.remove("{0}".format(fnamenew))

######################################
def main():
    '''
    Acquire data from the sensors in a SensMit Mesh.
    '''

    parser = argparse.ArgumentParser(description='Testfarm SensMit/Irrometer Access')
    #required argument
    parser.add_argument('api_key',action='store',help='API KEY')
    #optional arguments
    parser.add_argument('--stime','-s',action='store',help='start time in YYYY-mm-dd HH:MM:SS in quotes, disregarded if etime is not also set or stime >= etime. If disregared, stime becomes two hours earlier than etime.  We round any stime given back to the earlier hour.')
    parser.add_argument('--etime','-e',action='store',help='end time in YYYY-mm-dd HH:MM:SS in quotes. We round any etime given back to the earlier hour. The default is now.')
    parser.add_argument('--sensor1_csv',action='store',help='Name of output file if any (681.csv is default',default='681.csv')
    parser.add_argument('--sensor2_csv',action='store',help='Name of output file if any (682.csv is default',default='682.csv')
    parser.add_argument('--tmpout_fname1',action='store',help='Name of output file if any (tmp.out is default',default='tmp.out')
    parser.add_argument('--tmpout_fname2',action='store',help='Name of output file if any (tmp2.out is default',default='tmp2.out')
    parser.add_argument('--dont_append',action='store_true',help='Do not override original file (used for testing only)')
    args = parser.parse_args()
    
    header = {'Authorization':'ApiKey {0}'.format(args.api_key)}
    #extract the datetime from the args if any, zeroing out the seconds
    if args.etime is not None:
        etime = datetime.strptime(args.etime, '%Y-%m-%d %H:%M:%S')
        etime = etime.replace(second=0,microsecond=0)
        if args.stime is not None:
            stime = datetime.strptime(args.stime, '%Y-%m-%d %H:%M:%S')
            stime = stime.replace(second=0,microsecond=0)

        #if stime is None or invalid, set it to four hours earlier than etime
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
        print 'temporary output file names: {0} {1}'.format(args.tmpout_fname1,args.tmpout_fname2)
        print 'output csv file names: {0} {1}'.format(args.sensor1_csv,args.sensor2_csv)

    #access the meshes, for each pull out two sensors and their data
    #http://www.sensmitweb.com/api/documentation
    meshes = 'http://www.sensmitweb.com/api/v1/meshes'
    mesh_db_id = 97
    sens1_id = 681 #must match fname1.csv
    sens2_id = 682 #must match fname2.csv
    #we expect files 681.csv and 682.csv with a header to be in the cwd (we append here)

    url = '{0}/{1}/data'.format(meshes,mesh_db_id)
    payload = {
        'start_time':stime.strftime('%s'),
        'end_time':etime.strftime('%s'),
        'utc_offset':480
    }
    r = requests.get(url, headers=header, params=payload)
    objects = r.json()["objects"]
    if len(objects) == 0: #no data in this timespan
        print 'no data between {0} {1}'.format(stime,etime)
        sys.exit(0)

    '''Steps:
    1) get the data and put it in file fnamenew
    2) diff fnamenew and sensor1/2_fname (681/682.csv) and append the difference 
    to sensor1/2_fname
    '''
    #sensor 1 csvwriter
    fnamenew = '{0}tmp.csv'.format(sens1_id)
    f = open(fnamenew,'wt') #destroy it if it exists
    csv1 = csv.writer(f)
    #sensor 2 csvwriter
    fnamenew2 = '{0}tmp.csv'.format(sens2_id)
    f2 = open(fnamenew2,'wt') #destroy it if it exists
    csv2 = csv.writer(f2)

    #Step 1) get the data and put it in file fnamenew
    for sensor in objects:
        if 'seconds' not in sensor or 'id' not in sensor:
            #something is very wrong, skip this sensor entry
            continue
        #store -1 in an entry if there is no key for the measurement in the data
        if sensor["id"] == sens1_id or sensor["id"] == sens2_id:
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
            if sensor["id"] == sens1_id:
		csvwriter = csv1
            else:
		csvwriter = csv2
            #write out the data
	    csvwriter.writerow([ts,mo1,mo2,mo3,intt,ext,poww,cap,tip,irr])

    #close to force flush
    f.close()
    f2.close()

    #Step 2) append diff fnamenew and/to sensor1/2_fname
    process_files(args.sensor1_csv,fnamenew,args.tmpout_fname1,args.dont_append)
    process_files(args.sensor2_csv,fnamenew2,args.tmpout_fname2,args.dont_append)
    
######################################
if __name__ == "__main__":
    main()
######################################
