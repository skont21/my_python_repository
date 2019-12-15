import requests
from bs4 import BeautifulSoup
import os
import subprocess
from getpass import getpass

path=os.getcwd()

# print("Current Path:",path)
username= input("Username:")
password=getpass("Password:")

url = "https://svn.inaccess.com/implementation/"
data = requests.get(url,auth=(username,password)).content.decode('utf-8')

soup = BeautifulSoup(data,"html.parser")
tags = soup('a')

pvplants_urls=[]
pvplants=[]
for tag in tags:
    # Look at the parts of a tag
    plant = tag.get('href', None).split('/')[0]
    pvplants.append(plant)
    pvplants_urls.append(url+plant+'/trunk/Provisioning/')

directories = list(os.walk('.'))[0][1]
for plant in pvplants:
    if plant in directories:
        continue
    else:
        print("Making Directory:",plant)
        mkdir = "mkdir " + plant
        _=subprocess.Popen(mkdir.split(),stdout=subprocess.PIPE).communicate()

i=0
for pvplants_url in pvplants_urls:
    ci = "svn co "+"--username "+username+" --password "+password+" "+pvplants_url+" ."
    up = "svn up"
    os.chdir(pvplants[i]+"/")

    files = list(os.walk('.'))[0][2]
    if not files:
        print("Checkout:",pvplants[i])
        _=subprocess.Popen(ci.split(),stdout=subprocess.PIPE).communicate()
    else:
        print("Updating:",pvplants[i])
        _=subprocess.Popen(up.split(),stdout=subprocess.PIPE).communicate()
    i+=1
    os.chdir("..")
