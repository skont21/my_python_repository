path_to_files = input('Please insert the path to the pvplants folders:')
from usefull_funcs import *
import pickle
with open ('all_data.pickle','rb') as file:
    all_data = pickle.load(file)

# plants=list_dir(path_to_files)
# all_data=[]
# for plant in plants:
#     data = parse_ods(plant,path_to_files)
#     all_data.append({plant:data})

ppc_plants_data = []
plants_data = []
for plant in all_data:
    pl = list(plant.keys())[0]
    ppc = find_if_ppc(plant[pl])
    inv = find_inv(plant[pl])
    country = find_country(plant[pl])
    grid = find_grid_code(plant[pl])
    ips = find_plant_ips(path_to_files,plant[pl],pl)
    try:
        ppc_c = 'c_'+str(int(find_ppc_controller(plant[pl]))-1)
    except:
        ppc_c = ['-']
    try:
        ppc_ip = [ el['address'] for el in ips['controllers'] if el['ppc_ip']=="YES"] or ['-']
    except:
        ppc_ip = ['-']
    try:
        rest_ips = [ el['address'] for el in ips['controllers'] if el['ppc_ip']=="NO"]
    except:
        rest_ips = []
    if ppc:
        ppc_meter = find_PPC_meter(plant[pl])
        ppc_nom_power = find_ppc_nom_power(plant[pl])
    else:
        ppc_meter = '-'
        ppc_nom_power = '-'
    if ppc:
        ppc_plants_data.append({'Name':pl,
                               'PPC Meter':ppc_meter,
                               'Inverter':inv,
                               'Country':country,
                               'Grid_Code':grid,
                               'PPC Controller':ppc_c,
                               'Portal Name':find_portal_name(plant[pl]),
                               'PPC Nominal Power': ppc_nom_power,
                               '#_Controllers': ips['ncontrollers'],
                               'PPC ip': ppc_ip,
                               'Rest ips':rest_ips})
    plants_data.append({'Name':pl,
                       'Inverter':inv,
                       'PPC Meter':ppc_meter,
                       'Country':country,
                       'Grid_Code':grid,
                       'PPC Controller':ppc_c,
                       'Portal Name':find_portal_name(plant[pl]),
                       'PPC Nominal Power': ppc_nom_power,
                       '#_Controllers': ips['ncontrollers'],
                       'PPC ip': ppc_ip,
                       'Rest ips':rest_ips})
