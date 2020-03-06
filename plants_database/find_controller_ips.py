import os
import fnmatch
import json
import re
import odsparser_3
import ooolib
from usefull_funcs import *

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CBOLD = '\33[1m'
CURL = '\33[4m'
CEND = '\33[0m'



def main(arg1,arg2,arg3):

    directories = list(os.walk(arg1))[0][1]
    for directory in directories:
        if directory[0]=='.':
            directories.remove(directory)
            continue

    plants_err=[]
    services=['insolar-2','insolar-octopus','insolar-sc','management','insolar']
    it_json = 'controller_[0-9]*_it.json$'
    lans = ['enp1s0','enp3s0','lan','eth0']
    controller_json = 'controller_[0-9]*\.json$'
    site_it_json = 'site_it.json$'


    i=0
    pvplants_dicts=[]
    for pvplant in directories:

        entry= {'name':'','ncontrollers':'','controllers':'','country':''}
        entry['name']=pvplant

        path = arg1

        data = parse_ods(pvplant,path)
        if data =="Error":
            i+=1
            continue

        country = find_country(data)


        entry['country']=country
        print(entry['country'])

        found = False
        controllers=[]

        files = os.listdir(path+'/'+pvplant+'/')
        for f in files:
            if re.search(site_it_json,f):
                site = f
        try:
            with open(path+'/'+pvplant+'/'+site) as json_file:
                data=json.load(json_file)
        except IOError:
            continue

        for service in services:
            if found:
                break
            else:
                try:
                    controllers = data['services'][service]['controllers']
                    found = True
                except KeyError:
                    pass

        if not found:
            it=[]
            for f in files:
                if re.search(it_json,f):
                    it.append(f)
            it.sort()
            if it:
                for f in it:
                    error=True
                    with open(path+'/'+pvplant+'/'+f) as json_file:
                        data=json.load(json_file)
                        for lan in lans:
                            if not error:
                                break
                            else:
                                try:
                                    controllers.append({'address': data['ethernet'][lan]['addresses'][0].split('/')[0]})
                                    error=False
                                    break
                                except (IndexError,KeyError):
                                    pass
            else:
                error=True

            if error:
                plants_err.append(entry['name'])

        json_files=[]
        for f in files:
            if re.search(controller_json,f):
                    json_files.append(f)
        json_files.sort()
        ind=-10
        if json_files:
            for f in json_files:
                with open(path+'/'+pvplant+'/'+f) as json_file:
                    try:
                        data=json.load(json_file)
                    except:
                        ind = -10
                        break
                    try :
                        dump= data['application']['iobs']['ppc:P']
                        if dump:
                            ind = int(f.split('_')[1].split('.')[0])
                    except KeyError:
                        pass
        ncontrollers =len(controllers)
        entry['ncontrollers'] = ncontrollers
        l=[]

        for n in range(0,ncontrollers):
            if len(json_files) == 0:
                l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'UNDEFINED'})
            elif n != ind :
               l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'NO'})
            else:
               l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'YES'})
        entry['controllers']=l
        pvplants_dicts.append(entry)
        i=i+1

    return pvplants_dicts


if __name__=='__main__':
    sys.exit(main())
