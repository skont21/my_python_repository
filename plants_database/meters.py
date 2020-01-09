import odsparser_3
import os
import re

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

def find_PPC_meter(data):
    meter_selection = data['PPC']['Settings']['Meter selection']
    if meter_selection == 'PCC multimeter' :
        meter_model = data['PCC']['PCC multimeter']['Model']
        meter_man = data['PCC']['PCC multimeter']['Manufacturer']
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT'):
            meter_model = data['Electrical panel']['Multimeter']['Model'][0]
            meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'Sub-field multimeters':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['Sub-field']['Multimeter']['Model'][ID]
        meter_man = data['Sub-field']['Multimeter']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT'):
            meter_model = data['Sub-field']['Multimeter']['Model'][0]
            meter_man = data['Sub-field']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'Electrical panel multimeters':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['Electrical panel']['Multimeter']['Model'][ID]
        meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT'):
            meter_model = data['Electrical panel']['Multimeter']['Model'][0]
            meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'PCC protection device':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['PCC']['Protection device']['Model'][ID]
        meter_man =  data['PCC']['Protection device']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT'):
            meter_model = data['Protection device']['Multimeter']['Model'][0]
            meter_man = data['Protection device']['Multimeter']['Manufacturer'][0]
    else:
        meter_model = "Check ODS"
        meter_man = "Check ODS"
    return (meter_man,meter_model)

path_to_files = input('Please insert the path to the pvplants folders:')

print(CRED+CBOLD+"Listing Directories...."+"\n"+CEND)
directories = list(os.walk(path_to_files))[0][1]
for directory in directories:
    if directory[0]=='.':
        directories.remove(directory)
        continue
print(CRED+CBOLD+"DONE"+CEND)

PPC_meters=[]
for pvplant in directories:

    entry = {'name':'','meter_man':[],'meter_model':[]}

    print(CRED + pvplant + CEND + '\n')

    plant_ods = pvplant+'_InstallationData.ods$'
    path = path_to_files+'/'+pvplant+'/'
    files = os.listdir(path)
    # print(path)

    for f in files:
        if re.search(plant_ods,f):
            ods = f
            # print("YES")
    try:
        s=odsparser_3.Spreadsheet(path+ods)
    except (UnboundLocalError,IOError,NameError) as e :
        print(CRED + CBOLD + "ODS FILE NOT FOUND" + CEND + '\n')
        continue
    try:
        data= s._Spreadsheet__parse_spreadsheet()
    except:
        print(CRED + CBOLD + "ODS FILE PARSE ERROR" + CEND + '\n')
        continue

    try:
        PPC_incl = data['PPC']['Power control service']
    except KeyError:
        print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
        continue

    if PPC_incl == "Yes":
        entry['name'] = pvplant
        man,mod = find_PPC_meter(data)
        entry['meter_man'] = man
        entry['meter_model'] = mod
        PPC_meters.append(entry)
        print(str(entry['meter_man']))
        print(str(entry['meter_model'])+'\n')
    else:
        print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
        continue
