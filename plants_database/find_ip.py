import csv
import os
import re
import sys
from sys import argv
import sqlite3

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

cur.execute('''select * from COUNTRIES''')
countries = cur.fetchall()

cur.execute('''select PLANTS.id, PLANTS.name , IPS.field from PLANTS join IPS on PLANTS.ppc_ip=IPS.id''')
plants = cur.fetchall()

cur.execute('''select id, name, ppc_ip from PLANTS where ppc_ip="-" ''')
plants = plants +cur.fetchall()

while True:
    method = raw_input("Search for a plant (Press ENTER for ALL PLants, c for plants per Country, p for plant per name or q to exit):" )
    if method == "" :
        for plant in plants:
            print (CRED + CBOLD + str(plant[0])+")"+plant[1]+" "*(60-(len(str(plant[0]))+len(plant[1])))+ CGREEN +CBOLD + plant[2] + CEND)
    elif method in ["q","Q"]:
        break
    elif method in ["p","P"]:
        while True:
            nothing=True
            name = raw_input("Enter (part of) name of the plant:")
            for plant in plants:
                if re.search(name,plant[1],re.IGNORECASE):
                    print (CRED + CBOLD + str(plant[0])+")"+plant[1]+" "*(60-(len(str(plant[0]))+len(plant[1])))+ CGREEN +CBOLD + plant[2] + CEND+'\n')
                    print (" "*61+CURL +CBOLD + "REST IPs" + CEND)
                    cur.execute('''select IPS.field from IPS join PLANTS ON IPS.plant_id = PLANTS.id where PLANTS.id='''+str(plant[0]))
                    ips = cur.fetchall()
                    for ip in ips:
                        if ip[0] != plant[2]:
                            print(CBLUE +CBOLD + " "*61+ ip[0] + CEND)
                    print('\n')
                    nothing=False
            if nothing:
                print(CRED +CBOLD + "No plants" +CEND)
                break
            break
    elif method in ["c","C"]:
        indexes = []
        for c in countries:
            indexes.append(str(c[0]))
            print(CBOLD + str(c[0])+ ")" +c[1]+ CEND+'\n')
        while True:
            ind = raw_input("Please choose one of the coutries above:")
            if ind not in indexes:
                continue
            else:
                break


        cur.execute('''select PLANTS.id, PLANTS.name,IPS.field,COUNTRIES.name from PLANTS join COUNTRIES ON PLANTS.country_id =COUNTRIES.id
             join IPS on PLANTS.ppc_ip=IPS.ID where COUNTRIES.id= '''+ind)
        res = cur.fetchall()

        print( CBLUE + CBOLD + "PPC PLANTS FROM " + countries[int(ind)-1][1] +'\n'+CEND)
        for r in res:
            print (CRED + CBOLD + str(r[0])+")"+r[1]+" "*(60-(len(str(r[0]))+len(r[1])))+ CGREEN +CBOLD + r[2] + CEND)
        if not res:
            print(CRED + CBOLD + "NO PPC PLANTS FROM THE SELECTED COUNTRY" + CEND)
