import sqlite3
import find_plant_inv

conn = sqlite3.connect('plants.sqlite')
cur = conn.cursor()

conn1 = sqlite3.connect('inverters.sqlite')
cur1 = conn1.cursor()



cur1.executescript('''
CREATE TABLE IF NOT EXISTS PLANTS(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE,
    inv_model_id INTEGER
);
CREATE TABLE IF NOT EXISTS INVERTER_MODEL(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE,
    man_id INTEGER
);
CREATE TABLE IF NOT EXISTS MANUFACTURERS(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
)
''')

cur.execute('''SELECT name from PLANTS''')
pl=cur.fetchall()

cur1.execute('''SELECT INVERTER_MODEL.name FROM PLANTS JOIN INVERTER_MODEL ON PLANTS.inv_model_id = INVERTER_MODEL.id''')
mod = cur1.fetchall()

plants=[]
for p in pl:
    # print(p)
    plants.append(p[0])

models =[]
for m in mod:
    # print(m)
    models.append(m[0].encode('utf-8'))

path_to_files = raw_input('Please insert the path to the pvplants folders:')
plant_inv = find_plant_inv.main(path_to_files,plants)

for entry in plant_inv:

    cur1.execute('''INSERT OR IGNORE INTO MANUFACTURERS (name)
               VALUES (?)''', (entry['inverter_man'],))

    cur1.execute('''SELECT id FROM MANUFACTURERS WHERE name = ?''',(entry['inverter_man'],))
    man_id = cur1.fetchone()[0]

    cur1.execute('''INSERT OR IGNORE INTO INVERTER_MODEL (name)
               VALUES (?)''', (entry['inverter_model'],))

    cur1.execute('''UPDATE INVERTER_MODEL set man_id = ? where name = ?''',(man_id,entry['inverter_model'],))

    cur1.execute('''SELECT id FROM INVERTER_MODEL WHERE name = ?''',(entry['inverter_model'],))
    inv_id = cur1.fetchone()[0]

    cur1.execute('''INSERT OR IGNORE INTO PLANTS (name)
               VALUES (?)''',(entry['name'],))

    cur1.execute('''UPDATE PLANTS set inv_model_id = ? where name = ?''',(inv_id,entry['name'],))
conn1.commit()
