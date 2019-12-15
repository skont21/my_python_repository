import csv
import os
import re
import sys
from sys import argv

CRED = '\33[91m'
CUNDERL = '\33[4m'
CGREEN = '\33[92m'
CBOLD = '\33[1m'
CEND = '\33[0m'
CGREENBG  = '\33[42m'
CREDBG    = '\33[41m'

name = raw_input("Search for a plant:" )

plants = []
ips=[]

try:
    csv_file = open('ppc_ips.csv','rt')
except:
    print(CRED + CBOLD + "No file with PPC IPs. Exiting..." + CEND)
    sys.exit()

data = csv.reader(csv_file, delimiter=',')

i=0
for row in data:
    if i==0:
        i=i+1
        continue
    else:
        plants.append(dict(index=row[0],country=row[1],name=row[2],ip=row[3]))

results = []
for plant in plants:
    if re.search(name,plant["name"],re.IGNORECASE):
        results.append(plant)

if not results :
    print(CRED + CBOLD +"No plants" + CEND)
elif len(results)==1:
    print(CRED + CBOLD +"Connecting to:"  + CEND + CGREEN + CUNDERL + CBOLD +results[0]["name"] +"  "+"("+results[0]["ip"]+")" "..." + CEND)
    cmd = "ssh root@"+results[0]["ip"]
    os.system(cmd)
else :
    print(CRED + CBOLD + "Multiple plants found:" + CEND +"\n")
    for plant in results:
        print (CRED + CBOLD + plant["name"] +CEND +" "*(60-len(plant["name"]))+ CGREEN +CBOLD + plant["ip"] + CEND)
