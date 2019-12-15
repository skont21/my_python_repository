import os
import fnmatch
import json
import re
import odsparser
from pyexcel_odsr import get_data
import odsparser
import ooolib

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

    def find_country(data):
        try:
            country = data['Plant']['Country'].encode('utf-8')
        except AttributeError:
            country='Undefined'
        except IndexError:
            country='None'
        except KeyError:
            country='None'
        return country

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
        print(CRED +entry['name'] + CEND + '\n')

        country_ods = entry['name']+'_InstallationData.ods$'
        path = arg1+'/'+entry['name']+'/'
        files = os.listdir(path)

        for f in files:
            if re.search(country_ods,f):
                ods = f
        try:
            s = odsparser.Spreadsheet(path+ods)
        except (UnboundLocalError,IOError) as e :
            continue
        try:
            data = s.parse()
        except:
            continue

        country = find_country(data)

        if country == 'Viet Nam':
            country = 'Vietnam'
        elif country == 'UK':
            country = 'United Kingdom'
        elif country == 'SOUTH AFRICA':
            country = 'South Africa'
        elif country == "Hellas":
            country = "Greece"
        elif country == "GREECE":
            country = "Greece"
        elif country == "United States":
            country = "USA"
        elif country == "KE":
            country = "Kenya"
        elif country == "INDIA":
            country = "India"
        elif country == "NL":
            country = "Netherlands"
        entry['country']=country
        print(entry['country'])

        found = False
        controllers=[]
        # print(found)

        for f in files:
            if re.search(site_it_json,f):
                site = f
                # print(site)

        try:
            with open(path+site) as json_file:
                data=json.load(json_file)
        except IOError:
            # print('Error')
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

        # print(found)
        if not found:
            it=[]
            for f in files:
                if re.search(it_json,f):
                    it.append(f)
            it.sort()
            if it:
                for f in it:
                    error=True
                    with open(path+f) as json_file:
                        #print(CBOLD + path+f +CEND)
                        data=json.load(json_file)
                        for lan in lans:
                            if not error:
                                break
                            else:
                                try:
                                    controllers.append({'address': data['ethernet'][lan]['addresses'][0].split('/')[0]})
                                    # print("FROM CONTROLLER_IT")
                                    error=False
                                    break
                                except (IndexError,KeyError):
                                    pass
            else:
                error=True

            if error:
                print(CBOLD + "No such  key" + CEND + '\n')
                # print('/home/skont/Desktop/Implementation/'+pvplants_dicts[i]['name']+'/trunk/Provisioning/'+f)
                plants_err.append(entry['name'])

        json_files=[]
        for f in files:
            if re.search(controller_json,f):
                    json_files.append(f)
        json_files.sort()
        # print(len(json_files))
        ind=-10
        if json_files:
            for f in json_files:
                # print(f)
                with open(path+f) as json_file:
                    try:
                        data=json.load(json_file)
                    except:
                        ind = 0
                        break
                    try :
                        dump= data['application']['iobs']['ppc:P']
                        if dump:
                            ind = int(f.split('_')[1].split('.')[0])
                    except KeyError:
                        pass
        # print("ind="+str(ind))
        ncontrollers =len(controllers)
        print ncontrollers
        entry['ncontrollers'] = ncontrollers
        l=[]

        for n in range(0,ncontrollers):
            if len(json_files) == 0:
                l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'UNDEFINED'})
                # print("UNDEFINED")
            elif n != ind :
               l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'NO'})
               # print("NO")
            else:
               l.append({'index':n, 'address':controllers[n]['address'],"ppc_ip":'YES'})
               # print("YES")
        entry['controllers']=l
        pvplants_dicts.append(entry)
        i=i+1

    return pvplants_dicts


if __name__=='__main__':
    sys.exit(main())
