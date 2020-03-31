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
    import subprocess

    print(CRED + CBOLD + "Listing directories" + CEND+"\n")
    current_path = os.getcwd()
    os.chdir(path)
    cmd=subprocess.Popen('ls',stdout=subprocess.PIPE)
    directories, cmd_err = cmd.communicate()
    directories = directories.split(b"\n")
    directories = [el.decode('utf-8') for el in directories]
    print(CRED+CBOLD+"DONE:"+str(len(directories))+" plants"+CEND+"\n")
    os.chdir(current_path)
    return directories

def parse_ods(plant,path):
    import odsparser_3
    import re
    import os

    print(CRED + plant + CEND + '\n')

    plant_ods = plant+'_InstallationData.ods'
    path = path+'/'+plant+'/'

    try:
        files = os.listdir(path)
    except FileNotFoundError:
        return("Error")

    try:
        s=odsparser_3.Spreadsheet(path+plant_ods)
    except (UnboundLocalError,IOError,NameError) as e :
        # print(CRED + CBOLD + "ODS FILE NOT FOUND" + CEND + '\n')
        return("Error")

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
        for ind,el in enumerate(inv):
            if not el:
                inv[ind]='None'
        if not inv :
            inv = ['None']

    except (IndexError,KeyError,TypeError,AttributeError):
        inv= ['None']
    try:
        man = list(set(data['PV array']['Inverter']['Manufacturer']))
        for ind,el in enumerate(man):
            if not el:
                man[ind]='None'
        if not man:
            man = ['None']

    except (IndexError,KeyError,TypeError,AttributeError):
        man= ['None']
    return(man,inv)

def find_slave(data):
    slave_man = ['None']
    slave_model = ['None']
    elpanel_dict = data['Electrical panel']
    try:
        slave_man= list(set(elpanel_dict['Slave PPC']['Manufacturer']))
        slave_model =  list(set(elpanel_dict['Slave PPC']['Model']))
        # if (slave_man==['INACCESS'])|(slave_man==['inAccess Networks'])|(not slave_man):
        #     slave_man= ['None']
        #     slave_model= ['None']
    except (IndexError,KeyError,TypeError,AttributeError):
        slave_man= ['None']
        slave_model= ['None']
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
        elif not country:
            country='Undefined'
    except (AttributeError,IndexError,KeyError,TypeError):
        country='Undefined'
    return country


def find_if_ppc(data):
    try:
        PPC_incl = data['PPC']['Power control service']
        if PPC_incl == "Yes":
            return True
        else:
            # print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
            return False
    except (TypeError,KeyError):
        # print(CRED + CBOLD + "NO PPC IN THIS PLANT" + CEND + '\n')
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
    except (KeyError,TypeError):
        gr_code='None'
    return gr_code

def find_portal_name(data):
    try:
        portal_name = data['Plant']['Name']
    except (KeyError,TypeError):
        portal_name = 'None'
    return portal_name

def find_ppc_controller(data):
    try:
        ppc_c = data['PPC']['Settings']['PPC controller']
    except(KeyError,TypeError):
        ppc_c = 'None'
    return ppc_c

def find_ppc_nom_power(data):
    try:
        nom = data['PPC']['Settings']['Nominal power']
    except (KeyError,TypeError):
        nom = 'Undefined'
    return nom

def find_plant_ips(path,data,plant):

    # import find_ppc_controller
    # import find_if_ppc
    import os
    import re
    import json

    plants_err=[]
    services=['insolar-2','insolar-octopus','insolar-sc','management','insolar']
    it_json = 'controller_[0-9]*_it.json$'
    lans = ['enp1s0','enp3s0','lan','eth0']
    controller_json = 'controller_[0-9]*\.json$'
    site_it_json = 'site_it.json$'

    found = False
    controllers = []

    entry= {'name':'','ncontrollers':'','controllers':''}
    entry['name']= plant

    files = os.listdir(path+'/'+plant+'/')
    for f in files:
        if re.search(site_it_json,f):
            site = f
    try:
        with open(path+'/'+plant+'/'+site) as json_file:
            dat=json.load(json_file)
    except (IOError,UnboundLocalError):
        return {'name':plant,'ncontrollers':'-','controllers':'-'}

    for service in services:
        if found:
            break
        else:
            try:
                controllers = dat['services'][service]['controllers']
                found=True
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
                with open(path+'/'+plant+'/'+f) as json_file:
                    dat=json.load(json_file)
                    for lan in lans:
                        if not error:
                            break
                        else:
                            try:
                                controllers.append({'address':dat['ethernet'][lan]['addresses'][0].split('/')[0]})
                                error =False
                                break
                            except (IndexError,KeyError):
                                pass
    else:
            error=True
            plants_err.append(entry['name'])

    ncontrollers = len(controllers)
    entry['ncontrollers'] = ncontrollers

    # print(plant)

    l=[]
    if find_if_ppc(data):
        ind = int(find_ppc_controller(data))-1
    else:
        ind = -10

    for n in range(0,ncontrollers):
        if n == ind :
            l.append({'index':n,'address':controllers[n]['address'],"ppc_ip":"YES"})
        else:
            l.append({'index':n,'address':controllers[n]['address'],"ppc_ip":"NO"})

    entry['controllers']=l

    return entry
