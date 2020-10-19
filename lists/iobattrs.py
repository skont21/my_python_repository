#!/usr/bin/python -i
# -*- mode: Python; -*-

import os
import sys
import json
import csv
import optparse


def parse_args():
    usage = "usage: %prog [ options ]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-x", "--extra-iobs",
            dest="extraiobs",
            default=False,
            action="store_true",
            help="create extra IOBs for RT and TR2 measurements")
    (options, args) = parser.parse_args()
    return options



if __name__=='__main__':
    options = parse_args()
    if options.extraiobs:
        print 'INFO: adding extra IOBs (RT and TR2)'
    out_file = 'serverList.csv'
    csv_d = {}
    skipped = {}
    with open(out_file,'r') as f:
        f_csv = csv.reader(f, quoting=csv.QUOTE_NONE)
        for row in f_csv:
            if row[0] == 'IOB Name':
                continue
            if not csv_d.has_key(row[0]):
                csv_d[row[0]] = []
            csv_d[row[0]].append(','.join(row))

    # write output file
    with open('iobattrs.csv','w') as out:
        out.write('IOB NAME,CONTROLLER ID,INSOLAR PATH,TYPE,EUNIT,STATES,MDB,POLLING PERIOD,UUID,IOA,'+ \
            'TABLE,DATA TYPE,REGISTER,DNP3 INDEX,DNP3 CLASS,DNP3 ID'+'\n')

        for iname, iattrs in sorted(csv_d.iteritems()):
            columns = iattrs[0].split(',')
            numcols = len(columns)
            # assume same order with iec104.csv, where k=0 (1st column) is IOB Name (9 columns)
            # 'IOB Name,IOA,IOB type,IOB description,IOB states,' + \
            # 'Asset name,Engineering unit,MDB,Polling period(100msec)'

            # columns existing in iec104.csv
            ioa=''
            cid=''
            itype=''
            desc=''
            state=''
            asset=''
            eunit=''
            mdb=''
            period=''
            # new empty columns
            uuid=''
            insolarpath=''
            # modbussrv columns
            table=''
            dataType=''
            register=''
            # dnp3srv columns
            dnp3index=''
            dnp3class=''
            dnp3id=''

            for k in range(1,numcols):
                if k==1:
                    ioa=columns[k]
                elif k==2:
                    cid=columns[k]
                elif k==3:
                    itype=columns[k]
                elif k==4:
                    desc=columns[k]
                elif k==5:
                    state=columns[k]
                elif k==6:
                    asset=columns[k]
                elif k==7:
                    eunit=columns[k]
                elif k==8:
                    mdb=columns[k]
                elif k==9:
                    period=columns[k]
                elif k==10:
                    table=columns[k]
                elif k==11:
                    dataType=columns[k]
                elif k==12:
                    register=columns[k]
                elif k==13:
                    dnp3index=columns[k]
                elif k==14:
                    dnp3class=columns[k]
                elif k==15:
                    dnp3id=columns[k]

            if ( (not (iname.endswith('MALF') or iname.endswith('_TR2') or \
                     iname.endswith('_RT') or itype in ['SI','SO']) and not options.extraiobs) # ISLCSPR-1182 & 1147
              or (not (iname.endswith('MALF') or itype in ['SI','SO']) and options.extraiobs) ): # ISLCSPR-2423
                out.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' \
                        %(iname,cid,insolarpath,itype,eunit,state,mdb,period,uuid,ioa,table,\
                          dataType,register,dnp3index,dnp3class,dnp3id)+'\n')
                # 'IOB NAME,INSOLAR PATH,TYPE,EUNIT,STATES,MDB,POLLING PERIOD,UUID,IOA,TABLE,DATA TYPE,REGISTER'
            else:
                skipped[iname]="%s,%s,%s" %(iname,cid,itype)

    # write output file for skipped iobs (TR2 , malf, or type SI,SO,MO,DO,AO)
    with open('skipped_iobs2.csv','w') as out:
        out.write('IOB NAME,CONTROLLER ID,TYPE'+'\n')

        for sk in sorted(skipped.iterkeys()):
            out.write(skipped[sk]+'\n')

        print 'Done'
