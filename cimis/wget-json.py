import wget, json, os, sys, datetime

#/home/ec2-user/gsn/data
end=start=datetime.date.today()-datetime.timedelta(days=1)

url = 'http://et.water.ca.gov/api/data?appKey=0e1a4d1a-347c-40af-b811-a14958a8eba8&targets=93230,93274,95616,93460&startDate={0}&endDate={1}'.format(start,end)

'''sierra,nichols,russell-meek,sedgwick'''

'''
targets=93117,94553
{"Data":{"Providers":[{"Name":"cimis","Type":"spatial","Owner":"water.ca.gov","Records":[

{"Date":"2015-07-02","Julian":"183","Standard":"english","ZipCodes":"93117","Scope":"daily","DayAsceEto":{"Value":"0.16","Qc":" ","Unit":"(in)"},"DaySolRadAvg":{"Value":"568","Qc":" ","Unit":"(Ly/day)"},"DayWindSpdAvg":{"Value":"4.1","Qc":" ","Unit":"(MPH)"}},

{"Date":"2015-07-02","Julian":"183","Standard":"english","ZipCodes":"94553","Scope":"daily","DayAsceEto":{"Value":"0.2","Qc":" ","Unit":"(in)"},"DaySolRadAvg":{"Value":"472","Qc":" ","Unit":"(Ly/day)"},"DayWindSpdAvg":{"Value":"6","Qc":" ","Unit":"(MPH)"}}
]
}]}}
'''

outfname = 'data'
try:
    os.remove(outfname)
except OSError:
    pass

csvfname = '/home/ec2-user/gsn/data/cimis.csv'
writeHeader = False
if not os.path.isfile(csvfname):
    writeHeader = True
csvf = open(csvfname,'a')
wget.download(url,out=outfname)
print

f = open(outfname,'r')
header = 'Date, Zip, DayAsceEto, DaySolRadAvg, DayWindSpdAvg\n'
if writeHeader:
   csvf.write(header)
for line in f:
    ent = json.loads(line)
    for ele in ent['Data']['Providers'][0]['Records']:
	output_str = ele['Date']+','
	output_str += ele['ZipCodes']+','
	output_str += ele['DayAsceEto']['Value']+','
	output_str += ele['DaySolRadAvg']['Value']+','
	output_str += ele['DayWindSpdAvg']['Value']+'\n'
        csvf.write(output_str)

csvf.close()
