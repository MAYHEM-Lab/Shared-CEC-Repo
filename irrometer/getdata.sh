#! /bin/bash

#update this value with your api key
APIKEY="XXX"

#fix all paths below as appropriate

#the following grabs the data from the past 4 hours (from now)
#call this from a cron job or periodic task within 4 hours of 
#uploading the base dataset to gsn
#Suggested frequency = 1hr mins -- irrometer doesn't store more frequently than this -- I've seen 75 min delays

#cmd="/usr/bin/python /Users/ckrintz/RESEARCH/data/CEC/irrometer/updatereq.py --sensor1_csv /home/ec2-user/gsn/data/681.csv --sensor2_csv /home/ec2-user/gsn/data/682.csv --tmpout_fname1 /tmp/tmp1.out --tmpout_fname2 /tmp/tmp2.out ${APIKEY}"
#eval $cmd

####################################################
#for testing purposes
DATE=`date +%Y-%m-%d\ %H:%M:%S`
SDATE="2015-09-27 11:38:00"
EDATE="2015-09-27 13:38:00"

#fill in csvs up to now (default etime) 
SDATE="2015-09-26 00:00:00"
#touch 681.csv 682.csv, don't append, just keep the tmp files with the data
#cmd="python updatereq.py --dont_append -e '${DATE}' -s '${SDATE}' user_1406829249625.294:34d839b8e438ad1db614dbf9c5d1577cc9110094"
#eval $cmd

#name your own csv files, these will be appended to and must exist
#cmd="python updatereq.py --sensor1_csv '681.csv' --sensor2_csv '682.csv' -e '${DATE}' -s '${SDATE}' ${APIKEY}"
#eval $cmd

#no csv -- just get some data between two dates for sensors 681 and 682
#python reqtest2.py --single_req --printonly -s '2015-09-27 12:00:00' -e '2015-09-27 16:00:00' PUT_APIKEY_HERE
