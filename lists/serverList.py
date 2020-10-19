
import os
import sys
import json
import csv
import optparse
import re
from shutil import copyfile
reload(sys).setdefaultencoding('utf-8')

def parse_args():
    usage = "usage: %prog [ options ]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-q", "--quiet",
            dest="quiet",
            default=False,
            action="store_true",
            help="hide skipped signals")
    parser.add_option("-n", "--no-adress",
            dest="noaddress",
            default=False,
            action="store_true",
            help="do not calculate Addresses. Used for initializing serverList.csv with None values.")
    parser.add_option("-s", "--server_name",
            dest="server_name",
            default="",
            help="Server name (IEC104, MODBUSSRV, DNP3SRV)")
    parser.add_option("-u", "--update",
            dest="update",
            action= "store_true",
            default=False,
            help="update IOBs (with non-None info) for a specified server type (see -s) from serverList.csv")
    parser.add_option("-x", "--exclude",
            dest="exclude",
            action= "store_true",
            default=False,
            help="exclude certain IOBs (pvpgroup/smu string-related) from IOA ID calculation")

    (options, args) = parser.parse_args()
    return options

def get_asset_type(appname):
    asset_type=''
    apps_dict = {
        'pvarray'   : 'Inverter',
        'invm'      : 'Inverter module',
        'pvpgroup'  : 'PV panel',
        'smu'       : 'String Monitor',
        'weather'   : 'Weather station',
        'ppc'       : 'Power Plant Controller',
        'sbfs'      : 'Subfield Protection Device',
        'lcps'      : 'LCP Protection Device',
        'eps'       : 'Electrical Panel Protection Device',
        'pccs'      : 'PCC Protection Device',
        'transfs'   : 'T/F Protection Device',
        'transf'    : 'T/F Protection Device',
        'sbfm'      : 'Subfield Multimeter',
        'lcpm'      : 'LCP Multimeter',
        'epm'       : 'Electrical Panel Multimeter',
        'pccm'      : 'PCC Multimeter',
        'transflvm' : 'T/F Multimeter',
        'transfhvm' : 'T/F Multimeter',
        'pvarrayac' : 'Inverter Multimeter',
        'ups'       : 'Uninterruptible Power Supply',
        'epups'     : 'Electrical Panel Uninterruptible Power Supply',
        'pvtran'    : 'Tracker Anemometer',
        'pvtrgw'    : 'Tracker Gateway',
        'pvtrack'   : 'Tracker',
        'pvtrin'    : 'Tracker Installation',
        'sec'       : 'Security',
        'switches'  : 'Switch',

    }

    for app in apps_dict:
        exp = r"%s\d+$" %app
        exp2 = r"%s$" %app
        a=re.match(exp, appname) is not None #match followed by number eg in pvarray001
        b=re.match(exp2, appname) is not None #exact match eg ppc
        if a or b:
            asset_type = apps_dict[app]
            break

    return asset_type

def calc_state(iname,iattrs):
    state=''
    if iattrs['type'] in ['MO','MI']:
        if iattrs.has_key('name_z'):
            state += 'Z(8)=%s|' %(iattrs['name_z'])
        for k in range(8):
            if iattrs.has_key('name_s%d' %k):
                state += '%d=%s|' %(k, iattrs['name_s%d' %k])
    elif iattrs['type'] in ['DO','DI']:
        for key in ['z_nm','o_nm']:
            foundState=False
            if iattrs.has_key(key):
                foundState=True
                if key == 'z_nm':
                    state += '0=%s|' %(iattrs[key])
                else:
                    state += '1=%s|' %(iattrs[key])

        # check event_wrd low byte for VABN and ctl_wrd low byte for flag NORO
        if not foundState:
            vabn = False
            noro = False
            if iattrs.has_key('event_wrd') and len(iattrs['event_wrd'])==2:
                event_low_byte = iattrs['event_wrd'][1]
                vabn = ( ( event_low_byte & 256) == 256)

            if iattrs.has_key('ctl_wrd') and len(iattrs['ctl_wrd'])==2:
                ctl_low_byte = iattrs['ctl_wrd'][1]
                noro = ( ( ctl_low_byte & 2048) == 2048)
            # if vabn event flag is 1 (set) enables check for abnormal value
            if vabn:
                #noro true means vabn = zero val
                if noro:
                    state += '0=ALARM|1=NORMAL|'
                else:
                    state += '0=NORMAL|1=ALARM|'

    if state.endswith('|'):
        state = state.rstrip('|')
    #if any state name contains commas, replace them with whitespace (' ')
    #in order not to spoil the columns structure in csv file
    state.replace(',' , ' ')

    return state

def calc_row(iname,iattrs,cid,ioa=None,table=None,dataType=None,register=None,DNP3index=None,DNP3class=None,DNP3ID=None):
    # IOB name,
    # IOA,
    # IOB type,
    # IOB description,
    # IOB states,
    # Asset name,
    # Engineering unit,
    # MDB,
    # Period
    if not iattrs.has_key("desc"):
        iattrs['desc'] = ""
    desc=iattrs['desc'].replace(',' , ' ')
    state=calc_state(iname,iattrs)

    egu=''
    mdb=''
    if iattrs['type'] in ['AO','AI']:
        egu='-'
        mdb='5'
        if iattrs.has_key('egu'):
            egu = iattrs['egu']
            egu.replace(',' , ' ')
        if iattrs.has_key('mdb'):
            mdb=iattrs['mdb']

    period='10'
    if iattrs.has_key('period'):
        period = iattrs['period']

    asset_type=''
    if len(iname.split(':',1))>1:
        appname = iname.split(':',1)[0]
        asset_type = get_asset_type(appname)

    row = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" \
    %(iname, ioa, cid, iattrs['type'], desc, state, asset_type, egu, mdb, period, table, dataType, register, DNP3index,DNP3class,DNP3ID)

    return row

###########################################
####              IEC 104              ####
###########################################

def json2csvIEC104(json_data, iobs, out_file, iob_controller):

    # initially read the current csv file
    # and extract the existing IOBs which will be skipped
    with open(out_file,'r') as f:
        f_csv = csv.reader(f, quoting=csv.QUOTE_NONE)
        ioa_l=[0]
        ioa_d = {}
        csv_d = {}
        for row in f_csv:
            if row[0] == 'IOB Name':
                continue
            if not csv_d.has_key(row[0]):
                csv_d[row[0]] = []
            try:
                ioa_l.append(int(row[1]))
            except:
                pass
            csv_d[row[0]].append(','.join(row))

    # exit if duplicate IOAs are found in the csv
    if not options.noaddress and len(set([ioa for ioa in ioa_l if ioa_l.count(ioa) > 1])) > 0:
        print("ERROR: Duplicate IOAs found:")
        for ioa in set([ioa for ioa in ioa_l if ioa_l.count(ioa) > 1]):
            print(ioa
        exit()

    skipped={}

    if len(iobs) > 10000:
        cnt_log = True
        cnt = 0  # start counter
        print("%d IOBs will now be processed to add them in the CSV" %len(iobs))
    else:
        cnt_log = False

    for iname, iattrs in sorted(iobs.iteritems()):

        if cnt_log:
            cnt += 1
            if cnt % 1000 == 0:
                print("         %d out of %d IOBs done" %(cnt, len(iobs))


        # ignore t3sys IOBs
        if iname.startswith('t3sys'):
            continue

        # keep the old file settings for IOBs already present if their type is the same
        if iname in csv_d.keys():
            if options.quiet:
                continue
            else:
                print("         Skipped existing IOB %s" %iname
            skipped[iname] = "%s,%s,%s" %(iname,'existing',iattrs['type'])

        # in iec104.csv, add all SI IOBs
        elif iattrs['type'] == 'SI' and iname[0] != '_' and \
             (True if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]!='_')  ) :
                 if not options.noaddress and (iname.split(':',1)[0][:-3]+':'+iname.split(':',1)[1] not in exclude_iobs):
                     ioa = next(i for i in range(max(ioa_l)+2) if i not in ioa_l)
                     ioa_l.append(ioa)
                 else:
                     ioa = None
                 csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],ioa)

        # in iec104.csv, add all xI IOBs that have logging or some events enabled
        elif (iattrs['type'][1] == 'I' and iname[0] != '_' and \
             (True if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]!='_')  ) and \
             ((iattrs.has_key('event_wrd') and iattrs['event_wrd'] != []) or \
              (iattrs.has_key('ctl_wrd') and iattrs['ctl_wrd'][0] & 7168 != 0))):
                 if not options.noaddress and (iname.split(':',1)[0][:-3]+':'+iname.split(':',1)[1] not in exclude_iobs):
                    ioa = next(i for i in range(max(ioa_l)+2) if i not in ioa_l)
                    ioa_l.append(ioa)
                 else:
                     ioa = None
                 csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],ioa)

        # in iec104.csv, add all DO, SO, MO, AO IOBs not starting with '_'
        elif iattrs['type'] in ['DO','SO','MO','AO'] and iname[0] != '_' and \
             (True if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]!='_')  ) :
                 if not options.noaddress and (iname.split(':',1)[0][:-3]+':'+iname.split(':',1)[1] not in exclude_iobs):
                    ioa = next(i for i in range(max(ioa_l)+2) if i not in ioa_l)
                    ioa_l.append(ioa)
                 else:
                     ioa = None
                 csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],ioa)


        # in iec104.csv, add all xO IOBs without preceding underscore in their name
        # which are not connected to LOB outputs, except for FSM LOBs
        elif (iattrs['type'][1] == 'O' and iname[0] != '_' and \
             (True if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]!='_')  ) and \
             iname not in lob_terms):
                 if not options.noaddress and (iname.split(':',1)[0][:-3]+':'+iname.split(':',1)[1] not in exclude_iobs):
                    ioa = next(i for i in range(max(ioa_l)+2) if i not in ioa_l)
                    ioa_l.append(ioa)
                 else:
                     ioa = None
                 csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],ioa)

        # ignore all other signals
        else:
            if options.quiet:
                continue
            else:
                print("         Skipped internal %s IOB %s" %(iattrs['type'], iname))
        skipped[iname] = "%s,%s,%s" %(iname,'new',iattrs['type'])

    checkIOBs(cnt_log, iobs, csv_d)
    writeToFiles(cnt_log, csv_d, skipped, out_file)


#################################################
####              Modbus Server              ####
#################################################

def getCurrentCsv(out_file):
    with open(out_file,'r') as f:
        f_csv = csv.reader(f, quoting=csv.QUOTE_NONE)
        hr_l=[]
        di_l=[]
        cl_l=[]
        ioa_d = {}
        csv_d = {}
        for row in f_csv:
            if row[0] == 'IOB Name':
                continue
            if not csv_d.has_key(row[0]):
                csv_d[row[0]] = []
            table = row[10]
            data_type = row[11]
            register = row[12]
            try:
                if table == "HR":
                    hr_l.append(int(register))
                    # reserve another register
                    if data_type in ['float2','unsigned2']:
                        hr_l.append(int(register)+1)
                elif table == "DI":
                    di_l.append(int(register))
                elif table == "CL":
                    cl_l.append(int(register))
            except:
                pass
            csv_d[row[0]].append(','.join(row))

    return (csv_d, hr_l, di_l, cl_l)

def checkForDuplicates(hr_l, di_l, cl_l):
    if not options.noaddress and len(set([reg for reg in hr_l if hr_l.count(reg) > 1])) > 0:
        print("ERROR: Duplicate registers found:")
        for reg in set([reg for reg in hr_l if hr_l.count(reg) > 1]):
            print("HR:%d " %reg,
        exit()

    if not options.noaddress and len(set([reg for reg in di_l if di_l.count(reg) > 1])) > 0:
        print("ERROR: Duplicate registers found:")
        for reg in set([reg for reg in di_l if di_l.count(reg) > 1]):
            print("HR:%d " %reg,
        exit()

    if not options.noaddress and len(set([reg for reg in cl_l if cl_l.count(reg) > 1])) > 0:
        print("ERROR: Duplicate registers found:")
        for reg in set([reg for reg in cl_l if cl_l.count(reg) > 1]):
            print("HR:%d " %reg,
        exit()

def findFreeRegs(hr_l, di_l, cl_l):
    hr_l.sort()
    di_l.sort()
    cl_l.sort()

    tl = [i for i in range(0, 65535*2)]
    free_hr = list(set(tl)-set(hr_l))

    tll = [i for i in range(0, 65535*2)]
    free_di = list(set(tll)-set(di_l))

    tlll = [i for i in range(0, 65535*2)]
    free_cl = list(set(tlll)-set(cl_l))

    return (free_hr, free_di, free_cl)

def checkIOBs(cnt_log, iobs, csv_d):
    cnt = 0  # start counter

    if cnt_log:
        print("All %d IOBs have been processed" %len(iobs))
        print("%d IOBs will now be checked if they are no longer in the t3apps" %len(csv_d))

    # remove all CSV signals that are not present in the JSON files
    for iname in sorted(csv_d.iterkeys()):
        if iname not in iobs.keys():
            del csv_d[iname]
            if not options.quiet:
                print("-        Removed non-existent IOB %s" %iname)
        if cnt_log:
            cnt += 1
            if cnt % 1000 == 0:
                print("         %d out of %d IOBs done" %(cnt, len(csv_d)))

    if cnt_log:
        print("IOB process complete")

def writeToFiles(cnt_log, csv_d, skipped, out_file):
    print("%d rows will now be added to csv file" %len(csv_d)
    cnt = 0  # start counter

    # write output file
    with open(out_file,'w') as f:
        f.write('IOB Name,IOA,Controller ID,IOB type,IOB description,IOB states,' + \
        'Asset name,Engineering unit,MDB,Polling period(100msec),Table,Data type,Register,' + \
        'DNP3 index,DNP3 class,DNP3 ID' + '\n')
        for iob_v in sorted(csv_d.iterkeys()):
            if type(csv_d[iob_v]) == list:
                for iob_vl in csv_d[iob_v]:
                    f.write(iob_vl+'\n')
            else:
                f.write(csv_d[iob_v]+'\n')
            if cnt_log:
                cnt += 1
                if cnt % 1000 == 0:
                    print("         %d out of %d IOBs done" %(cnt, len(csv_d))

    # write output file skipped iobs
    if not options.quiet:
        with open('skipped_iobs.csv','w') as f:
            f.write('IOB Name,Existing/new,Type'+'\n')
            for sk in sorted(skipped.iterkeys()):
                f.write(skipped[sk]+'\n')

def get_one_reg(attrs, free_l):
    idx = 0
    while True:
        #One for value - One for status
        if free_l[idx + 1] == free_l[idx] + 1:
            reg = free_l[idx]
            attrs.append(reg)
            #attrs.append(reg + 1) # status
            free_l.remove(reg)
            #free_l.remove(reg+1) # status
            return reg
        idx += 1

def get_two_regs(attrs, free_l):
    idx = 0
    while True:
        #Two for value - One for status
        if free_l[idx + 2] == free_l[idx + 1] + 1 == free_l[idx] + 2:
            reg = free_l[idx]
            attrs.append(reg)
            attrs.append(reg + 1)
            #attrs.append(reg + 2) # status
            free_l.remove(reg)
            free_l.remove(reg+1)
            #free_l.remove(reg+2) # status
            return reg
        idx += 1

def getIobFromJson(csv_d, skipped, iname, iattrs, registers):
    # ignore t3sys IOBs and internal
    if iname.startswith('t3sys') or iname[0] == '_' or \
         (False if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]=='_')  ):
        return
    elif iname in csv_d.keys():
        if not options.quiet:
            print("         Skipped existing IOB %s" %iname
        skipped[iname] = "%s,%s,%s" %(iname,'existing',iattrs['type'])
    elif iattrs['type'] in ['AI', 'AO']:
        table = 'HR'
        d_type = 'float2'
        if not options.noaddress:
            reg = get_two_regs(registers.hr, registers.free_hr)
        else:
             reg = None
        csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,table,d_type,reg)
    elif iattrs['type'] == 'PC':
        table = 'HR'
        d_type = 'unsigned2'
        if not options.noaddress:
            reg = get_two_regs(registers.hr, registers.free_hr)
        else:
             reg = None
        csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,table,d_type,reg)
    elif iattrs['type'] in ['MI', 'MO']:
        table = 'HR'
        d_type = 'unsigned1'
        if not options.noaddress:
            reg = get_one_reg(registers.hr, registers.free_hr)
        else:
             reg = None
        csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,table,d_type,reg)
    elif iattrs['type'] == 'DI':
        table = 'DI'
        d_type = 'bit'
        if not options.noaddress:
            reg = get_one_reg(registers.di, registers.free_di)
        else:
             reg = None
        csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,table,d_type,reg)
    elif iattrs['type'] == 'DO':
        table = 'CL'
        d_type = 'bit'
        if not options.noaddress:
            reg = get_one_reg(registers.cl, registers.free_cl)
        else:
             reg = None
        csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,table,d_type,reg)
    # ignore all other signals
    else:
        if not options.quiet:
            print("         Skipped %s IOB %s" \
                  %(iattrs['type'], iname)
        skipped[iname] = "%s,%s,%s" %(iname,'new',iattrs['type'])


def json2csvDNP3SRV(json_data, iobs, out_file, iob_controller):
    skipped={}
    csv_d = {}
    dnp3id_l=[0]
    # initially read the current csv file
    # and extract the existing IOBs which will be skipped
    with open(out_file,'r') as f:
        f_csv = csv.reader(f, quoting=csv.QUOTE_NONE)
        for row in f_csv:
            if row[0] == 'IOB Name':
                continue
            if not csv_d.has_key(row[0]):
                csv_d[row[0]] = []
            try:
                dnp3id_l.append(int(row[15]))
            except:
                pass
            csv_d[row[0]].append(','.join(row))

    # exit if duplicate DNP3 IDs are found in the csv
    if not options.noaddress and len(set([dnp3id for dnp3id in dnp3id_l if dnp3id_l.count(dnp3id) > 1])) > 0:
        print("ERROR: Duplicate DNP3 IDs found:",
        for dnp3id in set([dnp3id for dnp3id in dnp3id_l if dnp3id_l.count(dnp3id) > 1]):
            print(dnp3id,
        exit()

    if len(iobs) > 10000:
        cnt_log = True
        cnt = 0  # start counter
        print("%d IOBs will now be processed to add them in the CSV" %len(iobs)
    else:
        cnt_log = False

    for iname, iattrs in sorted(iobs.iteritems()):

        if cnt_log:
            cnt += 1
            if cnt % 1000 == 0:
                print("         %d out of %d IOBs done" %(cnt, len(iobs))

    	# ignore t3sys IOBs and internal
    	if iname.startswith('t3sys') or iname[0] == '_' or \
    	     (False if (len(iname.split(':',1))==1 ) else (iname.split(':',1)[1][0]=='_')  ):
    	    continue
    	elif iname in csv_d.keys():
    	    if not options.quiet:
    	        print("         Skipped existing IOB %s" %iname
    	    skipped[iname] = "%s,%s,%s" %(iname,'existing',iattrs['type'])
	else:

            if not options.noaddress:
                dnp3id = next(i for i in range(max(dnp3id_l)+2) if i not in dnp3id_l)
                dnp3id_l.append(dnp3id)
            else:
                dnp3id = None

            csv_d[iname] = calc_row(iname,iattrs,iob_controller[iname],None,None,None,None,None,None,dnp3id)

    checkIOBs(cnt_log, iobs, csv_d)
    writeToFiles(cnt_log, csv_d, skipped, out_file)


def json2csvModbusSRV(json_data, iobs, out_file, iob_controller):

    csv_d = {}
    skipped={}
    registers = Registers()
    registers.hr = []
    registers.di = []
    registers.cl = []

    # initially read the current csv file
    # and extract the existing IOBs which will be skipped
    csv_d, hr_l, di_l, cl_l = getCurrentCsv(out_file)

    # exit if duplicate registers are found in the csv
    checkForDuplicates(hr_l, di_l, cl_l)

    # find free registers
    registers.free_hr, registers.free_di, registers.free_cl = findFreeRegs(hr_l, di_l, cl_l)

    if len(iobs) > 10000:
        cnt_log = True
        cnt = 0  # start counter
        print("%d IOBs will now be processed to add them in the CSV" %len(iobs)
    else:
        cnt_log = False

    for iname, iattrs in sorted(iobs.iteritems()):

        if cnt_log:
            cnt += 1
            if cnt % 1000 == 0:
                print("         %d out of %d IOBs done" %(cnt, len(iobs))

        # keep the old file settings for IOBs already present if their type is the same
        getIobFromJson(csv_d, skipped, iname, iattrs, registers)

    checkIOBs(cnt_log, iobs, csv_d)
    writeToFiles(cnt_log, csv_d, skipped, out_file)

def csv2jsonModbusSRV(csv_source,modbus_json):

    # load serverList
    with open(modbus_json) as json_file:
        json_data = json_file.read()
        try:
            data = json.loads(json_data)
        except Exception as e:
            raise
    with open(csv_source) as csv_file:
        try:
            reader = csv.reader(csv_file)
        except Exception as e:
            raise
        lines =  [l for l in reader]
        for n in range(len(lines)):
            if lines[n][12] != 'None':
                for k in data.keys():
                    # update keys in json
                    key = k
                    if lines[n][0] == key.replace('-value',''):
                        if data[k][0] != lines[n][10]:
                            #Table
                            data[k][0] = lines[n][10]
                            print(("Updating %s IOB's table value..."%(lines[n][0]))
                        if data[k][1] != lines[n][11]:
                            #Data tpye
                            data[k][1] = lines[n][11]
                            print(("Updating %s IOB's data type..."%(lines[n][0]))
                        if data[k][1] != lines[n][12]:
                            #Register
                            data[k][2] = lines[n][12]
                            print(("Updating %s IOB's register..."%(lines[n][0]))
        #finished close files and copy
        try:
            csv_file.close()
            jsonfile = open(modbus_json,'w+')
            jsonfile.write(json.dumps(data, sort_keys=True, indent=4))
            jsonfile.close()
        except Exception as e:
            raise e

def csv2csvIECSRV(csv_source,csv_output):
    r = csv.reader(open(csv_source))
    lines_in = list(r)

    r = csv.reader(open(csv_output))
    lines_out = list(r)
    for li in range(1,len(lines_in)):
        if lines_in[li][1] != 'None': #IOA value is changed
            for lo in range(1,len(lines_out)):
                if lines_in[li][0] == lines_out[lo][1]: #keys IOBname match
                    print('Updating IOB %s IOA value'%(lines_out[lo][1])
                    lines_out[lo][2] = lines_in[li][1] #update value

   #write file and close
    with open(csv_output, 'wb') as csv_file:
        try:
            writer = csv.writer(csv_file)
            writer.writerows(lines_out)
            csv_file.close()
        except Exception as e:
            raise e

class Registers:
  hr = None
  free_hr = None
  di = None
  free_di = None
  cl = None
  free_cl = None

if __name__=='__main__':

    options = parse_args()

    cid = 0
    for f in os.listdir("."):
        if (f.startswith('controller') and f.endswith('_it.json') and '_node_' not in f) or \
                (f.startswith('controller') and f.endswith('node_0_it.json')):
            cid = cid + 1

    iobs = {}
    lob_terms = []
    iob_controller = {}

    if options.exclude:
        exclude_iobs = ['pvpgroup:STRINGST','pvpgroup:STRINGABN','pvpgroup:STRLOW_TH',\
                        'smu:STRDEV_TH','smu:STRLOW_TH','smu:STRINGST_SUM']
    else:
        exclude_iobs = []

    if options.update and options.server_name=="MODBUSSRV":
        print('Updating Modbus server files for controllers...'
        if 'serverList.csv' not in os.listdir("."):
            print('ERROR: Failed to load serverList.csv file.'
            exit()
        else:
            # for all controller_jsons
            for i in range(cid): #existing fixed file
                print('Checking controller %d...'%i
                if 'controller_%d_modbussrv_fixed.json'%i in os.listdir("."):
                    csv2jsonModbusSRV('serverList.csv','controller_%d_modbussrv_fixed.json'%i)
                else: #make it
                    if 'controller_%d_modbussrv.json'%i in os.listdir("."):
                        print('controller_%d_modbussrv.json created...'%i
                        copyfile('controller_%d_modbussrv.json'%i,'controller_%d_modbussrv_fixed.json'%i)
                        csv2jsonModbusSRV('serverList.csv','controller_%d_modbussrv_fixed.json'%i)
            print('Updates completed successfully!'

    elif options.update and options.server_name=="IEC104":
        print('Updating IEC server files for controllers...'
        if 'serverList.csv' not in os.listdir("."):
            print('ERROR: Failed to load serverList.csv file.'
            exit()
        if 'control.csv' not in os.listdir("."):
            print('ERROR: Failed to load control.csv file.'
            exit()
        if 'monitor.csv' not in os.listdir("."):
            print('ERROR: Failed to load monitor.csv file.'
            exit()
        csv2csvIECSRV('serverList.csv','control.csv')
        print('Updates for IEC control IOBs completed!'
        csv2csvIECSRV('serverList.csv','monitor.csv')
        print('Updates for IEC monitor IOBs completed!'


    # parse controller JSON files
    for i in range(cid):

        try:
            f = open('controller_%d.json' %i,'r')
        except:
            print("ERROR: Failed to open controller_%d.json file." %i
            exit()
        try:
            json_data = json.load(f, encoding='latin-1')
        except:
            print("ERROR: Failed to load data from controller_%d.json file." %i
            exit()

        # generate IOBs structure
        if not json_data.has_key('application') or \
           not json_data['application'].has_key('iobs'):
               print("ERROR: No IOB information in controller_%d.json file." %i
               exit()
        iobs.update(json_data['application']['iobs'])

        # generate xO IOBs connected to LOB outputs, except for FSM LOBs
        if json_data['application'].has_key('lobs'):
            for lattrs in json_data['application']['lobs'].itervalues():
                if lattrs.has_key('B'):
                    for term in lattrs['B'].keys():
                        if term.startswith('Q') and not lattrs['type'].endswith('fsm') and \
                           iobs[lattrs['B'][term]]['type'][1] == 'O':
                               lob_terms.append(lattrs['B'][term])

        # generate IOB to controller mapping
        for iname in json_data['application']['iobs'].iterkeys():
            iob_controller[iname] = i

    if not options.update:
        if options.server_name == "IEC104":
            # generate serverList.csv
            if 'serverList.csv' in os.listdir("."):
                pass
            else:
                print('Creating new serverList.csv file'
                open('serverList.csv','w').close()

            json2csvIEC104(json_data, iobs, 'serverList.csv', iob_controller)
        elif options.server_name == "MODBUSSRV":
            # generate serverList.csv
            if 'serverList.csv' in os.listdir("."):
                pass
            else:
                print('Creating new serverList.csv file'
                open('serverList.csv','w').close()
            json2csvModbusSRV(json_data, iobs, 'serverList.csv', iob_controller)
        elif options.server_name == "DNP3SRV":
            # generate serverList.csv
            if 'serverList.csv' in os.listdir("."):
                pass
            else:
                print('Creating new serverList.csv file'
                open('serverList.csv','w').close()

            json2csvDNP3SRV(json_data, iobs, 'serverList.csv', iob_controller)
        else:
            print("ERROR: Servers supported (IEC104, MODBUSSRV, DNP3SRV)"

        print('Done.'
