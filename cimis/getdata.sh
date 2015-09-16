#! /bin/bash

DATE=`date +%Y-%m-%d -d "1 day ago"`
#echo $DATE

/usr/bin/python /root/src/CEC/cimis/cimis.py ${DATE} ${DATE} --daily_wsn /home/ec2-user/gsn/data/wsn3.csv --daily_scs /home/ec2-user/gsn/data/scs3.csv --hourly_wsn /home/ec2-user/gsn/data/wsnHr3.csv

############## for testing only #############
#copy in wsn2.csv to grotwsn, scs.csv to grot, and wsnHourly to grothourly
#python cimis.py ${DATE} ${DATE} --daily_wsn grotwsn --daily_scs grot --hourly_wsn grothourly
