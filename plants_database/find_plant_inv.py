import os
import fnmatch
import json
import re
import odsparser_3
# from pyexcel_odsr import get_data
# import ooolib
from usefull_funcs import *

def main(arg1):

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


        data = parse_ods(pvplant,arg1)
        if data =="Error":
            i+=1
            continue

        (inverter_man,inverter_model) = find_inv(data)

        if inverter_model =='None':
            (inverter_man,inverter_model) = find_slave(data)

        entry['inverter_model']=inverter_model
        entry['inverter_man']=inverter_man
        print(entry['inverter_model'])
        print(entry['inverter_man'])

        pvplants_dicts.append(entry)
        i+=1
    return pvplants_dicts

if __name__=='__main__':
    sys.exit(main())
