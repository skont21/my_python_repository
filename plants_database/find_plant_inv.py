import os
import fnmatch
import json
import re
import odsparser_3
from pyexcel_odsr import get_data
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

def main(arg1,arg2):


    def find_inv(data):
        try:
            inv = data['PV array']['Inverter']['Model'][0].encode('utf-8')
        except AttributeError:
            inv='Undefined'
        except IndexError:
            inv='None'
        except KeyError:
            inv='None'
        return inv

    def find_man(data):
        try:
            man = data['PV array']['Inverter']['Manufacturer'][0].encode('utf-8')
        except AttributeError:
            man='Undefined'
        except IndexError:
            man='None'
        except KeyError:
            man='None'
        return man

    def find_slave(data):
        elpanel_dict = data['Electrical panel']
        try:
            slave_man= elpanel_dict['Slave PPC']['Manufacturer'][0].encode('utf-8')
            slave_model =  elpanel_dict['Slave PPC']['Model'][0].encode('utf-8')
            if (slave_man=='INACCESS')|(slave_man=='inAccess Networks'):
                slave_man='None'
                slave_model='None'
        except IndexError:
            slave_man='None'
            slave_model='None'
        except KeyError:
            slave_man='None'
            slave_model='None'
        except AttributeError:
            slave_man='Undefined'
            slave_model='Undefined'
        return slave_man,slave_model

    directories = list(os.walk(arg1))[0][1]
    for directory in directories:
        if directory[0]=='.':
            directories.remove(directory)
            continue

    pvplants_dicts=[]
    i=0
    for pvplant in directories:

        entry = {'name':'','inverter_model':'','inverter_man':''}
        entry['name']=pvplant
        print(CRED +entry['name'] + CEND + '\n')

        plant_ods = entry['name']+'_InstallationData.ods$'
        path = arg1+'/'+entry['name']+'/'
        files = os.listdir(path)

        for f in files:
            if re.search(plant_ods,f):
                ods = f
        try:
            s = odsparser.Spreadsheet(path+ods)
        except (UnboundLocalError,IOError) as e :
            continue

        try:
            data = s.parse()
        except:
            continue

        inverter_model = find_inv(data)
        inverter_man = find_man(data)

        if inverter_model =='None':
            (inverter_man,inverter_model) = find_slave(data)

        entry['inverter_model']=inverter_model
        entry['inverter_man']=inverter_man
        print(entry['inverter_model'])
        print(entry['inverter_man']+'\n')

        pvplants_dicts.append(entry)
        i+=1
    return pvplants_dicts

if __name__=='__main__':
    sys.exit(main())
