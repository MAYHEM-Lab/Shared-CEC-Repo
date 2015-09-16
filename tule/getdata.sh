#! /bin/bash
#perform the signin first and save the cookie (replace LOGIN,PWD below)
curl -d "utf8=%26#x2713;&authenticity_token=xYM/hCdhdw+KU0qqYX1BdxckiyOSIUosQT/C96Qbrak=&user[email]=LOGIN&user[password]=PWD" --cookie-jar ./cookie https://www.tuletechnologies.com/users/sign_in

#Then for each sensor: XXX, YYY, ZZZ do this
/usr/bin/curl --cookie ./cookie https://www.tuletechnologies.com/towers/XXX.csv?year=2015 > XXX.csv
/usr/bin/curl --cookie ./cookie https://www.tuletechnologies.com/towers/YYY.csv?year=2015 > YYY.csv
/usr/bin/curl --cookie ./cookie https://www.tuletechnologies.com/towers/ZZZ.csv?year=2015 > ZZZ.csv
