import sqlite3
import csv
import sys
import json
import find_controller_ips
import pickle


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


conn = sqlite3.connect('plants.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS PLANTS (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    plant TEXT UNIQUE,
    portal_name TEXT UNIQUE,
    country_id INTEGER
    meter_id INTEGER,
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
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    ip TEXT UNIQUE,
    plant_id INTEGER
);
CREATE TABLE IF NOT EXISTS METER_MODELS(
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    model TEXT UNIQUE,
    man_id INTEGER
);
CREATE TABLE IF NOT EXISTS METER_MANUFACTURERS(
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    manufacturer TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS INVERTER_MODELS(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    models TEXT UNIQUE,
    man_id INTEGER
);
CREATE TABLE IF NOT EXISTS MANUFACTURERS(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    manufacturer TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS GRID_CODES(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    grid_code TEXT UNIQUE
)

''')

cur.execute('''SELECT name from PLANTS''')
pl=cur.fetchall()

cur.execute('''SELECT Countries.name from COUNTRIES JOIN PLANTS ON PLANTS.country_id = COUNTRIES.id''')
count=cur.fetchall()

cur.execute('''SELECT ppc_ip  from PLANTS''')
ppc_ip=cur.fetchall()

for control in Controls:
    cur.execute('''INSERT OR IGNORE INTO CONTROLS (control)
           VALUES (?)''', (control,))

plants=[]
for p in pl:
    plants.append(p[0])

ppc_ips=[]
for ip in ppc_ip:
    ppc_ips.append(ip[0])

for entry in controller_ips:

    ip_id="-"
    ppc_c = "-"

    cur.execute('''INSERT OR IGNORE INTO COUNTRIES (name)
               VALUES (?)''', (entry['country'],))

    if entry['country']:
        cur.execute('''SELECT id FROM COUNTRIES WHERE name = ?''',(entry['country'],))
    else:
        cur.execute('''SELECT id FROM COUNTRIES WHERE name = ?''',('Undefined',))
    country_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO PLANTS (name,country_id)
               VALUES (?,?)''',(entry['name'],country_id,))

    cur.execute('''SELECT id FROM PLANTS WHERE name = ?''',(entry['name'],))
    plant_id = cur.fetchone()[0]

    for i in range(0,len(entry['controllers'])):

        field = entry['controllers'][i]['address']
        cur.execute('''INSERT OR IGNORE INTO IPS (field,plant_id)
            VALUES (?,?)''', (field,plant_id,))

        if entry['controllers'][i]['ppc_ip']=='YES':
            cur.execute('''SELECT id FROM IPS WHERE field = ?''',(field,))
            ip_id = cur.fetchone()[0]
            # ip = entry['controllers'][i]['address']
            ppc_c = "c"+ str(entry['controllers'][i]['index'])

    cur.execute('''UPDATE PLANTS SET ppc_ip = ?, n_controllers = ?, ppc_c = ? where NAME = ?''',(ip_id,entry['ncontrollers'],ppc_c,entry['name'],))

conn.commit()
