import sqlite3
import pickle
from usefull_funcs import *
import tkinter as tk
from tkinter import filedialog,messagebox
import sys

answer=None

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


root = tk.Tk()
root.withdraw()

path_to_files = filedialog.askdirectory(parent=root)

if not path_to_files:
    sys.exit()

choise = tk.Toplevel(root)
choise.title("Select Action")
choise.resizable(width=False, height=False)
choise.withdraw()
choise.protocol("WM_DELETE_WINDOW")

tk.Label(choise,text="Insert data from file?").grid(row=0,column=0,columnspan=2)

def get_answer(button):
    global answer
    button_text=button.cget("text")
    if button_text == "Yes":
        answer = "yes"
        choise.destroy()
    else:
        answer = "no"
        choise.destroy()

data_bt = tk.Button(choise,text="Yes")
data_bt.config(command= lambda btn=data_bt:get_answer(btn))
data_bt.grid(row=1,column=0)

all_bt = tk.Button(choise,text="No",command=get_answer)
all_bt.config(command= lambda btn=all_bt:get_answer(btn))
all_bt.grid(row=1,column=1)

choise.deiconify()
choise.grab_set()
choise.wait_window(choise)

if answer=="yes":

    file = filedialog.askopenfilename(initialdir = ".",title="Select pickle file",
                                filetypes = (("pickle files","*.pickle"),),parent=root)

    root.destroy()
    print(CRED+CBOLD+"Loading Data :"+CEND+"\n")

    with open ('all_data.pickle','rb') as file:
        all_data = pickle.load(file)

elif answer=="no":
    root.destroy()

    plants=list_dir(path_to_files)

    print(CBOLD + "Beginning Parsing Procedure (This may take a while)" + CEND + "\n")
    all_data=[]
    for plant in plants:
        data = parse_ods(plant,path_to_files)
        all_data.append({plant:data})

    print(CBOLD + "Parsing completed succesfullt" + CEND + "\n")


    print(CBOLD + "Saving data to all_data.pickle for later use...." + CEND)
    with open("all_data.pickle",'wb') as f:
        pickle.dump(all_data,f)

    print(CBOLD + "DONE" + CEND)

else:
    sys.exit()

ppc_plants_data = []
plants_data = []

for plant in all_data:
    pl = list(plant.keys())[0]
    ppc = find_if_ppc(plant[pl])
    inv = find_inv(plant[pl])
    country = find_country(plant[pl])
    grid = find_grid_code(plant[pl]) or 'None'
    ips = find_plant_ips(path_to_files,plant[pl],pl)
    try:
        ppc_c = 'c_'+str(int(find_ppc_controller(plant[pl]))-1)
    except:
        ppc_c = '-'
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
        try:
            ppc_nom_power=float(ppc_nom_power)
        except:
            ppc_nom_power=float(ppc_nom_power.replace(",","."))
        ppc_nom_power = '{:.2f}'.format(ppc_nom_power)

    else:
        ppc_meter = ['None','None']
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

    print(CBOLD+pl+CEND+"\n")


print(CRED+CBOLD+"Proccessing DataBase :"+CEND+"\n")

conn = sqlite3.connect('all_plants.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS PLANTS (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    plant TEXT UNIQUE,
    portal_name TEXT,
    country_id INTEGER,
    ppc_meter_id INTEGER,
    inverter_id INTEGER,
    grid_code_id INTEGER,
    ppc_ip_id INTEGER,
    n_controllers INTEGER,
    ppc_nominal_power INTEGER,
    ppc_controller TEXT
);
CREATE TABLE IF NOT EXISTS COUNTRIES (
    id INTEGER NOT NULL PRIMARY KEY  UNIQUE,
    country TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS IPS (
    id INTEGER NOT NULL PRIMARY KEY   UNIQUE,
    ip TEXT UNIQUE,
    plant_id INTEGER
);
CREATE TABLE IF NOT EXISTS METER_MODELS(
    id INTEGER NOT NULL PRIMARY KEY   UNIQUE,
    model TEXT UNIQUE,
    man_id INTEGER
);
CREATE TABLE IF NOT EXISTS METER_MANUFACTURERS(
    id INTEGER NOT NULL PRIMARY KEY   UNIQUE,
    manufacturer TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS INVERTER_MODELS(
    id INTEGER NOT NULL PRIMARY KEY  UNIQUE,
    model TEXT UNIQUE,
    man_id INTEGER
);
CREATE TABLE IF NOT EXISTS INVERTER_MANUFACTURERS(
    id INTEGER NOT NULL PRIMARY KEY  UNIQUE,
    manufacturer TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS GRID_CODES(
    id INTEGER NOT NULL PRIMARY KEY  UNIQUE,
    grid_code TEXT UNIQUE
)

''')

for entry in plants_data:

    cur.execute('''INSERT OR IGNORE INTO PLANTS(plant)
    VALUES (?)''',(entry['Name'],))
    cur.execute('''SELECT id FROM PLANTS where plant = ?''',(entry['Name'],))
    plant_id = cur.fetchone()[0]


    cur.execute('''INSERT OR IGNORE INTO COUNTRIES(country)
    VALUES (?)''',(entry['Country'],))
    cur.execute('''SELECT id FROM COUNTRIES where country = ?''',(entry['Country'],))
    country_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO METER_MANUFACTURERS(manufacturer)
    VALUES (?)''',(entry['PPC Meter'][0],))
    cur.execute('''SELECT id FROM METER_MANUFACTURERS where manufacturer = ?''',(entry['PPC Meter'][0],))
    meter_man_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO METER_MODELS(model,man_id)
    VALUES (?,?)''',(entry['PPC Meter'][1],meter_man_id,))
    cur.execute('''SELECT id FROM METER_MODELS where model = ?''',(entry['PPC Meter'][1],))
    meter_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO INVERTER_MANUFACTURERS(manufacturer)
    VALUES (?)''',(entry['Inverter'][0][0],))
    cur.execute('''SELECT id FROM INVERTER_MANUFACTURERS where manufacturer = ?''',(entry['Inverter'][0][0],))
    inv_man_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO INVERTER_MODELS(model,man_id)
    VALUES (?,?)''',(entry['Inverter'][1][0],inv_man_id))
    cur.execute('''SELECT id FROM INVERTER_MODELS where model = ?''',(entry['Inverter'][1][0],))
    inv_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO GRID_CODES(grid_code)
    VALUES (?)''',(entry['Grid_Code'],))
    cur.execute('''SELECT id FROM GRID_CODES where grid_code = ?''',(entry['Grid_Code'],))
    grid_id = cur.fetchone()[0]

    for ip in entry['PPC ip'] + entry['Rest ips']:
        cur.execute('''INSERT OR IGNORE INTO IPS(ip,plant_id) VALUES (?,?)''',(ip,plant_id,))
    cur.execute('''SELECT id FROM IPS where ip = ?''',(entry['PPC ip'][0],))
    ppc_ip_id = cur.fetchone()[0]

    cur.execute('''UPDATE PLANTS SET  portal_name = ?, country_id = ?, ppc_meter_id = ?,
    inverter_id = ?, grid_code_id = ?, ppc_ip_id = ?, n_controllers = ?,
    ppc_nominal_power = ?, ppc_controller = ? where id = ?''',
               (entry['Portal Name'],country_id,meter_id,inv_id,grid_id,
               ppc_ip_id,entry['#_Controllers'],entry['PPC Nominal Power'],entry['PPC Controller'],plant_id,))
conn.commit()

# print(CRED+CBOLD+"ALL DONE"+CEND)
