import requests, json, os, sys, argparse
from datetime import datetime, date, timedelta

#http://www.python-requests.org/en/latest/
#r = requests.get('https://api.github.com/user', auth=('user', 'pass'))

###########################
def main():
    #summarize all cols in all tables in a db:
    parser = argparse.ArgumentParser(description='Make/process Cimis API calls')
    parser.add_argument('start',action='store',help='start date YYYY-MM-DD')
    parser.add_argument('end',action='store',help='end date YYYY-MM-DD')
    #parser.add_argument('dbname',action='store',help='SQLite3 database name')
    parser.add_argument('--daily_wsn',action='store', default=None,
        help='Output daily WSN: Give filename if True, else omit arg')
    parser.add_argument('--daily_scs',action='store',default=None,
        help='Output daily SCS: Give filename if True, else omit arg')
    parser.add_argument('--hourly_wsn',action='store',default=None,
        help='Output hourly WSN: Give filename if True, else omit arg')
    args = parser.parse_args()

    startday = args.start
    endday = args.end

    #cimis targets can be zips or stations, not both
    #cimis by zip, can ambiguously return different station data/values
    #cimis by zip is required for spatial/interpolated (ASCE Eto and Solar Radiation) values
    #1) run by station, request all but spatial data
    #2) run by zip request spatial data
    url='http://et.water.ca.gov/api/data'
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'

    #loop through and do this daily as CIMIS server cannot handle more
    dtstart = datetime.strptime(startday, '%Y-%m-%d')
    dtend = datetime.strptime(endday, '%Y-%m-%d')
    if dtstart.date() >= date.today() or dtend.date() >= date.today():
        parser.error('\nstart and end dates must both be less than todays date')
        sys.exit(-1)
    if dtstart.date() > dtend.date():
        parser.error('\nend date must be after or equal to start date')
        sys.exit(-1)
    dt = dtstart
    while dt <= dtend:
        #take it one day at a time, convert to strings
        startd = datetime.strftime(dt,'%Y-%m-%d')
        endd = datetime.strftime(dt,'%Y-%m-%d')
        dt = dt + timedelta(days=1)
    
        if args.daily_wsn is not None:
            #1) by day run by station, request all but spatial data
            header = 'day-asce-eto,day-asce-etr,day-precip,day-sol-rad-avg,day-vap-pres-avg,day-air-tmp-max,day-air-tmp-min,day-air-tmp-avg,day-rel-hum-max,day-rel-hum-min,day-rel-hum-avg,day-dew-pnt,day-wind-spd-avg,day-wind-run,day-soil-tmp-avg,day-soil-tmp-min,day-soil-tmp-max,day-eto'
            #1 and 33 show inactive here but Stan requested: http://www.cimis.water.ca.gov/Stations.aspx
            #replacing 1 with 80, 33 with 86,169
            stations = '6,39,64,80,86,88,94,107,121,139,165,169,230'
            payload = {'appKey': '0e1a4d1a-347c-40af-b811-a14958a8eba8', \
                'targets': stations, 'dataItems':header, 'startDate':startd, \
                'endDate':endd \
                }
            req = None
            try:
                req = s.get(url,params=payload)
            except requests.exceptions.RequestException as e:   
                print e
                sys.exit(1)
            entWSN = req.json()
    
            ent = entWSN
            csvfname = args.daily_wsn
            #write the header only if we are creating the file (vs appending)
            writeHeader = False
            if not os.path.isfile(csvfname):
                writeHeader = True
            csvf = open(csvfname,'a')
            header = 'Date,Station,'+header
            output_str = ''
            if writeHeader:
               output_str += header + '\n'

            if req.status_code != requests.codes.ok:
               #18 + 1(station) -1's here to indicate error for all stations on this date
               output_str += startd+',-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1\n'
            else:
                for ele in ent['Data']['Providers'][0]['Records']:
                   if 'Date' not in ele or 'Station' not in ele:
                       continue
                   output_str += ele['Date']+','
                   output_str += ele['Station']+','
                   if ele['DayEto']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayEto']['Value']+','
                   if ele['DayAsceEto']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayAsceEto']['Value']+','
                   if 'DayAsceEtr' not in ele or ele['DayAsceEtr']['Value'] is None:
                       output_str += '-1,'  #always produces a None value
                   else:
                       output_str += ele['DayAsceEtr']['Value']+','
                   if ele['DayPrecip']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayPrecip']['Value']+','
                   if ele['DaySolRadAvg']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DaySolRadAvg']['Value']+','
                   if ele['DayVapPresAvg']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayVapPresAvg']['Value']+','
                   if ele['DayAirTmpMin']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayAirTmpMin']['Value']+','
                   if ele['DayAirTmpMax']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayAirTmpMax']['Value']+','
                   if ele['DayAirTmpAvg']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayAirTmpAvg']['Value']+','
                   if ele['DayRelHumMin']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayRelHumMin']['Value']+','
                   if ele['DayRelHumMax']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayRelHumMax']['Value']+','
                   if ele['DayRelHumAvg']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayRelHumAvg']['Value']+','
                   if ele['DayDewPnt']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayDewPnt']['Value']+','
                   if ele['DayWindSpdAvg']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayWindSpdAvg']['Value']+','
                   if ele['DayWindRun']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DayWindRun']['Value']+','
                   if ele['DaySoilTmpMin']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['DaySoilTmpMin']['Value']+','
                   if ele['DaySoilTmpMax']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['DaySoilTmpMax']['Value']+','
                   if ele['DaySoilTmpAvg']['Value'] is None:
                       output_str += '-1\n' #last in csv line, omitting comma
                   else:
                       output_str += ele['DaySoilTmpAvg']['Value']+'\n' #last in csv line, omitting comma
            csvf.write(output_str)
            csvf.close()
        
        if args.daily_scs is not None:
            #2) run by zip request spatial data
            header = 'day-asce-eto,day-asce-etr,day-sol-rad-avg'
            zips_some_covered_by_same_stations = '93109,93199,93117,93254,93460,93458,95618,95694,95620,93766,93662'
            zips = '93109,93254,93270,93286,93460,93458,95618,95694,95620,93728,93662,93274,93230,95616,93710'
            #tests:
            #zips = '93710,93726,93612,93703,93702,93727,93291,93277,93292,93274,95616,95694,95695,95620'
            #zips = '93274,93230,95616,95694,93460,93710'
            payload = {'appKey': '0e1a4d1a-347c-40af-b811-a14958a8eba8', \
                'targets': zips, 'dataItems':header, 'startDate':startd, \
                'endDate':endd, 'prioritizeSCS':'Y' \
                }
            req = None
            try:
                req = s.get(url,params=payload)
            except requests.exceptions.RequestException as e:   
                print e
                sys.exit(1)
            entSCS = req.json()

            ent = entSCS
            csvfname = args.daily_scs
            #write the header only if we are creating the file (vs appending)
            writeHeader = False
            if not os.path.isfile(csvfname):
                writeHeader = True
            csvf = open(csvfname,'a')
            header = 'Date,Zips,'+header
            output_str = ''
            if writeHeader:
               output_str += header + '\n'

            if req.status_code != requests.codes.ok:
               #3 + 1(zips) -1's here to indicate error for all stations on this date
               output_str += startd+',-1,-1,-1,-1\n'
            else:
                for ele in ent['Data']['Providers'][0]['Records']:
                   if 'Date' not in ele or 'ZipCodes' not in ele:
                       continue
                   #Bug in CIMIS API call for spatial for zip 93766 returns today's date as well
                   if ele['Date'] == str(date.today()):
                       #print 'CIMIS Bug for at least these zips: 93766 93662'
                       continue
        
                   output_str += ele['Date']+','
                   output_str += ele['ZipCodes']+','
                   if ele['DayAsceEto']['Value'] is None:
                       output_str += '-1,'  
                   else:
                       output_str += ele['DayAsceEto']['Value']+','
                   if 'DayAsceEtr' not in ele or ele['DayAsceEtr']['Value'] is None:
                       output_str += '-1,'  #always produces a None value
                   else:
                       output_str += ele['DayAsceEtr']['Value']+','
                   if ele['DaySolRadAvg']['Value'] is None:
                       output_str += '-1\n'  #last in csv line, omitting comma
                   else:
                       output_str += ele['DaySolRadAvg']['Value']+'\n' #last in csv line, omitting comma
            csvf.write(output_str)
            csvf.close()
        
        if args.hourly_wsn is not None:
            #3) by hour run by station, request all but spatial data
            header = 'hly-air-tmp,hly-dew-pnt,hly-eto,hly-net-rad,hly-asce-eto,hly-asce-etr,hly-precip,hly-rel-hum,hly-res-wind,hly-soil-tmp,hly-sol-rad,hly-vap-pres,hly-wind-dir,hly-wind-spd'
            #1 and 33 show inactive here but Stan requested: http://www.cimis.water.ca.gov/Stations.aspx
            #replacing 1 with 80, 33 with 86,169
            stations = '6,39,64,80,86,88,94,107,121,139,165,169,230'
            payload = {'appKey': '0e1a4d1a-347c-40af-b811-a14958a8eba8', \
                'targets': stations, 'dataItems':header, 'startDate':startd, \
                'endDate':endd \
                }
            req = None
            try:
                req = s.get(url,params=payload)
            except requests.exceptions.RequestException as e:   
                print e
                sys.exit(1)
            entWSN = req.json()

            ent = entWSN
            csvfname = args.hourly_wsn
            #write the header only if we are creating the file (vs appending)
            writeHeader = False
            if not os.path.isfile(csvfname):
                writeHeader = True
            csvf = open(csvfname,'a')
            header = 'Date,Station,Hour,'+header
            output_str = ''
            if writeHeader:
               output_str += header + '\n'

            if req.status_code != requests.codes.ok:
               #14 + 2(station,hour) -1's here to indicate error for all stations on this date
               output_str += startd+',-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1\n'
            else:
                for ele in ent['Data']['Providers'][0]['Records']:
                   if 'Date' not in ele or 'Station' not in ele or 'Hour' not in ele :
                       continue
                   output_str += ele['Date']+','
                   output_str += ele['Station']+','
                   output_str += ele['Hour']+','
                   if ele['HlyAirTmp']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyAirTmp']['Value']+','
                   if ele['HlyDewPnt']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyDewPnt']['Value']+','
                   if ele['HlyEto']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyEto']['Value']+','
                   if ele['HlyNetRad']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyNetRad']['Value']+','
                   if ele['HlyAsceEto']['Value'] is None:
                       output_str += '-1,'
                   else:
                       output_str += ele['HlyAsceEto']['Value']+','
                   if 'HlyAsceEtr' not in ele or ele['HlyAsceEtr']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyAsceEtr']['Value']+','
                   if ele['HlyPrecip']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyPrecip']['Value']+','
                   if ele['HlyRelHum']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyRelHum']['Value']+','
                   if ele['HlyResWind']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyResWind']['Value']+','
                   if ele['HlySoilTmp']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlySoilTmp']['Value']+','
                   if ele['HlySolRad']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlySolRad']['Value']+','
                   if ele['HlyVapPres']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyVapPres']['Value']+','
                   if ele['HlyWindDir']['Value'] is None:
                       output_str += '-1,' 
                   else:
                       output_str += ele['HlyWindDir']['Value']+','
                   if ele['HlyWindSpd']['Value'] is None:
                       output_str += '-1\n'  #last in csv line, omitting comma
                   else:
                       output_str += ele['HlyWindSpd']['Value']+'\n' #last in csv line, omitting comma
            csvf.write(output_str)
            csvf.close()
    #end of day loop
        
######################################
if __name__ == "__main__":
    main()
