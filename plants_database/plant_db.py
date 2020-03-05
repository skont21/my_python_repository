import sqlite3
import csv
import sys
import json
import find_controller_ips


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

Controls=['P Control','P-Rate Control','P(f) Control','Q Control','Q(V) Control','Q-Rate Control','PF Control','AVR Control']

conn = sqlite3.connect('plants.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS PLANTS (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE,
    ppc_ip INTEGER,
    n_controllers INTEGER,
    ppc_c TEXT,
    country_id INTEGER
);
CREATE TABLE IF NOT EXISTS CONTROLS (
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    control TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS COUNTRIES (
    id INTEGER NOT NULL PRIMARY KEY  UNIQUE,
    name TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS IPS (
    id INTEGER NOT NULL PRIMARY KEY UNIQUE,
    field TEXT UNIQUE,
    plant_id INTEGER
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

path_to_files = input('Please insert the path to the pvplants folders:')
controller_ips = find_controller_ips.main(path_to_files,plants,ppc_ips)

for entry in controller_ips:

    ip_id="-"
    ppc_c = "-"

    cur.execute('''INSERT OR IGNORE INTO COUNTRIES (name)
               VALUES (?)''', (entry['country'],))

    cur.execute('''SELECT id FROM COUNTRIES WHERE name = ?''',(entry['country'],))
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
