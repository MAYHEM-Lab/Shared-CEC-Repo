import urlparse,sys,requests,argparse,sys
from datetime import datetime, timedelta


def main():
    '''
    Acquire data from the sensors in a SensMit Mesh: sample queries
    EX: python reqtest.py APIKEY
    '''

    parser = argparse.ArgumentParser(description='Testfarm SensMit/Irrometer Access')
    #required argument
    parser.add_argument('api_key',action='store',help='API KEY')
    args = parser.parse_args()
    
    header = {'Authorization':'ApiKey {0}'.format(args.api_key)}

    #access the meshes, for each pull out the sensors and their data
    #http://www.sensmitweb.com/api/documentation
    meshes = 'http://www.sensmitweb.com/api/v1/meshes'
    r = requests.get(meshes, headers=header)
    print 'Accessing API: {0}'.format(r.url)
    print 'result: {0}\n'.format(r.text)
    res = r.json()
    stime = datetime.strptime('2015-09-20 00:00:00', '%Y-%m-%d %H:%M:%S')
    etime = datetime.strptime('2015-09-21 00:00:00', '%Y-%m-%d %H:%M:%S')
    payload = {
        'start_time':stime.strftime('%s'),
        'end_time':etime.strftime('%s'),
        'utc_offset':480
        }
    for obj in res["objects"]:
        mesh_db_id = obj["id"]
        mesh_id = obj["mesh_id"]
        url = '{0}/{1}/data'.format(meshes,mesh_db_id)
        r = requests.get(url, headers=header, params=payload)
        print 'Accessing API: {0}'.format(r.url)
        print 'result: {0}\n'.format(r.text)
    
        #other API accesses from http://www.sensmitweb.com/api/documentation
        url = 'http://www.sensmitweb.com/api/v1/sensmits'
        payload = {'mesh_id': mesh_db_id}
        r = requests.get(url, headers=header, params=payload)
        print 'Accessing API: {0}'.format(r.url)
        print 'result: {0}\n'.format(r.text)

        #update sesmit_id with a valid ID (681 will work for demo account)
        sesmit_id = 681
        url = 'http://www.sensmitweb.com/api/v1/sensmits/{0}'.format(sesmit_id)
        payload = {}
        r = requests.get(url, headers=header, params=payload)
        print 'Accessing API: {0}'.format(r.url)
        print 'result: {0}\n'.format(r.text)

        #update sesmit_id with a valid ID (682 will work for demo account)
        sesmit_id = 682
        url = 'http://www.sensmitweb.com/api/v1/sensmits/{0}'.format(sesmit_id)
        payload = {}
        r = requests.get(url, headers=header, params=payload)
        print 'Accessing API: {0}'.format(r.url)
        print 'result: {0}\n'.format(r.text)
######################################
if __name__ == "__main__":
    main()
######################################
