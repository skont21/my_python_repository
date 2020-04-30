import requests
from bs4 import BeautifulSoup
import os
import subprocess
from getpass import getpass
from usefull_funcs import *

path=input("Enter the pvplants path: ")

# print("Current Path:",path)
username= input("Username:")
password=getpass("Password:")

url = "https://svn.inaccess.com/implementation/"

print("Connecting to SVN\n")
data = requests.get(url,auth=(username,password)).content.decode('utf-8')
print("Done\n")

soup = BeautifulSoup(data,"html.parser")
tags = soup('a')

pvplants_urls=[]
pvplants=[]
for tag in tags:
    # Look at the parts of a tag
    plant = tag.get('href', None).split('/')[0]
    pvplants.append(plant)
    pvplants_urls.append(url+plant+'/trunk/Provisioning/')

print("Checking for new directories"+"\n")
# directories = list(os.walk(path))[0][1]
directories = list_dir(path)
for plant in pvplants:
    if plant in directories:
        continue
    else:
        print("Making Directory:",plant)
        mkdir = "mkdir " + path + "/" +plant
        _=subprocess.Popen(mkdir.split(),stdout=subprocess.PIPE).communicate()
print("Done\n")

i=0

for pvplants_url in pvplants_urls:
    ci = "svn co "+"--username "+username+" --password "+password+" "+pvplants_url+" ."
    up = "svn up --accept tf"
    os.chdir(path+"/"+pvplants[i]+"/")

    files = list(os.walk('.'))[0][2]
    if not files:
        print("Checkout:",pvplants[i])
        _=subprocess.Popen(ci.split(),stdout=subprocess.PIPE).communicate()
    else:
        print("Already Existing:",pvplants[i])
        # _=subprocess.Popen(up.split(),stdout=subprocess.PIPE).communicate()
    i+=1
    os.chdir(path)
