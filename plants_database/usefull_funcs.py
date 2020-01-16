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

def list_dir(path):
    import os
    print(CRED+CBOLD+"Listing Directories...."+"\n"+CEND)
    directories = list(os.walk(path))[0][1]
    for directory in directories:
        if directory[0]=='.':
            directories.remove(directory)
            continue
    print(CRED+CBOLD+"DONE:"+str(len(directories))+" plants"+CEND+"\n")
    return directories

def parse_ods(plant,path):
    import odsparser_3
    import re
    import os

    print(CRED + plant + CEND + '\n')

    plant_ods = plant+'_InstallationData.ods'
    path = path+'/'+plant+'/'
    files = os.listdir(path)
    # print(path)

    # for f in files:
    #     if re.search(plant_ods,f):
    #         ods = f
            # print("YES")
    try:
        s=odsparser_3.Spreadsheet(path+plant_ods)
    except (UnboundLocalError,IOError,NameError) as e :
        try:
            s=odsparser_3.Spreadsheet(path+'trunk/Provisioning/'+plant_ods)
        except (UnboundLocalError,IOError,NameError) as e :
            print(CRED + CBOLD + "ODS FILE NOT FOUND" + CEND + '\n')
            return(e)

    try:
        data= s._Spreadsheet__parse_spreadsheet()
    except:
        print(CRED + CBOLD + "ODS FILE PARSE ERROR" + CEND + '\n')
        return("Error")
    return(data)

def find_PPC_meter(data):
    meter_selection = data['PPC']['Settings']['Meter selection']
    if meter_selection == 'PCC multimeter' :
        meter_model = data['PCC']['PCC multimeter']['Model']
        meter_man = data['PCC']['PCC multimeter']['Manufacturer']
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT') | (meter_model == 'SUM_OR_METER_GENERIC'):
            meter_model = data['Electrical panel']['Multimeter']['Model'][0]
            meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'Sub-field multimeters':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['Sub-field']['Multimeter']['Model'][ID]
        meter_man = data['Sub-field']['Multimeter']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT') | (meter_model == 'SUM_OR_METER_GENERIC'):
            meter_model = data['Sub-field']['Multimeter']['Model'][0]
            meter_man = data['Sub-field']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'Electrical panel multimeters':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])-1
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['Electrical panel']['Multimeter']['Model'][ID]
        meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT') | (meter_model == 'SUM_OR_METER_GENERIC'):
            try:
                ID_new = int(data['Electrical panel']['Multimeter']["Meter sources"][ID].split(",")[0])-1
                meter_model = data['Electrical panel']['Multimeter']['Model'][ID_new]
                meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][ID_new]
            except:
                meter_model = data['Electrical panel']['Multimeter']['Model'][0]
                meter_man = data['Electrical panel']['Multimeter']['Manufacturer'][0]
    elif meter_selection == 'PCC protection device':
        try:
            ID = int(data['PPC']['Settings']['Meter ID'])-1
        except (KeyError,TypeError) as e:
            ID = 0
        meter_model = data['PCC']['Protection device']['Model'][ID]
        meter_man =  data['PCC']['Protection device']['Manufacturer'][ID]
        if (meter_model == 'PPC_METER_GENERIC') | (meter_model == 'PPC_METER_GENERIC_EXT') | (meter_model == 'SUM_OR_METER_GENERIC'):
            meter_model = data['Protection device']['Multimeter']['Model'][0]
            meter_man = data['Protection device']['Multimeter']['Manufacturer'][0]
    else:
        meter_model = "Check ODS"
        meter_man = "Check ODS"
    return (meter_man,meter_model)

def find_inv(data):
    man = ['None']
    inv = ['None']
    try:
        inv =  list(set(data['PV array']['Inverter']['Model']))
        if not inv:
            inv = ['None']
    except AttributeError:
        inv= ['Undefined']
    except IndexError:
        inv= ['None']
    except KeyError:
        inv= ['None']
    try:
        man = list(set(data['PV array']['Inverter']['Manufacturer']))
        if not man:
            man=['None']
    except AttributeError:
        man= ['Undefined']
    except IndexError:
        man= ['None']
    except KeyError:
        man= ['None']
    return (man,inv)


def find_slave(data):
    slave_man = ['None']
    slave_model = ['None']
    elpanel_dict = data['Electrical panel']
    try:
        slave_man= list(set(elpanel_dict['Slave PPC']['Manufacturer']))
        slave_model =  list(set(elpanel_dict['Slave PPC']['Model']))
        if (slave_man==['INACCESS'])|(slave_man==['inAccess Networks'])|(not slave_man):
            slave_man= ['None']
            slave_model= ['None']
    except IndexError:
        slave_man= ['None']
        slave_model= ['None']
    except KeyError:
        slave_man= ['None']
        slave_model= ['None']
    except AttributeError:
        slave_man= ['Undefined']
        slave_model= ['Undefined']
    return (slave_man,slave_model)

def find_country(data):
    try:
        country = data['Plant']['Country']
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
    except AttributeError:
        country='Undefined'
    except IndexError:
        country='Undefined'
    except KeyError:
        country='Undefined'
    return country


def find_if_ppc(data):
    try:
        PPC_incl = data['PPC']['Power control service']
        if PPC_incl == "Yes":
            return True
        else:
            print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
            return False
    except KeyError:
        print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
        return False

def find_ppc_services(data):
    services=[]
    try:
        PPC_services = data['PPC']['PPC services']
        for k in PPC_services.keys():
            if PPC_services[k]=="Yes":
                services.append(k)
    except KeyError:
        services=['None']
    return services

def find_grid_code(data):
    try:
        gr_code = data['PPC']['Settings']['Grid code']
        if gr_code == 'None':
            gr_code = data['Plant']['Grid code']
            if (gr_code ==' ') | (gr_code == 'No'):
                gr_code = 'None'
    except KeyError:
        gr_code='None'
    return gr_code
