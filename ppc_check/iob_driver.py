import os
import re
import sys

drivers = ["NULL","CONST","SOFT","SOFTRAW","NETLINK","POPBUS","LON","EIB","BACNET","MODBUS2","XDRV","IEC60870"]
drivers_id =["0x00","0x01","SOFT","0x03","0x10","0x40","0x60","0x70","0x80","0xb0","0xf0","0x84"]

def get_iob_driver(iobName):
    cmd = "iobaccess read " + iobName + " drv_id | awk '{print $3}'"
    x = os.popen(cmd).read().strip()
    if not x :
	drv = "This IOB does not exist"
    else :
   	 try:
         	index = drivers_id.index(x)
         	drv = drivers[index]
    	 except:
        	drv = "UNDEFINED"
    return drv


iob = sys.argv[1]
driver = get_iob_driver(iob)
print "The driver of {" + iob + "} is "  + driver
