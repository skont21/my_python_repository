#!/usr/bin/python
#
# Insolar Server Assets
#
# author: kbampion@inaccess.com

import sys
import psycopg2
import csv
import re
import os
import ConfigParser
import shutil
import platform
import random
import json
from optparse import OptionParser

rep_di = {"=DEFAULT:": "0=", "&": ",", "map": "", "=0:": "1=", "=1:": "1=", "=2:": "1=", "=8:": "1="}
rep_ai = {"=DEFAULT:": "0=", "&": ",", "map": "", "=0:": "1=", "=1:": "1=", "=2:": "1=", "=8:": "HIHI=", "=9:": "HIGH=",
		  "=10:": "LOW=", "=11:": "LOLO="}
rep_mi = {"=DEFAULT:": "0=", "&": ",", "map": "", "=0:": "1=", "=1:": "1=", "=2:": "1=", "=10:": "0=", "=11:": "1=",
		  "=12:": "2=", "=13:": "3=", "=14:": "4=", "=15:": "5=", "=16:": "6=", "=17:": "7="}
iectype = {"AI": "M_ME_TF_1|M_ME_NC_1", "DI": "M_SP_TB_1|M_SP_NA_1", "MI": "M_DP_TB_1|M_DP_NA_1",
		   "AO": "C_SE_NC_1|C_SE_NC_1", "DO": "C_SC_NA_1|C_SC_NA_1", "MO": "C_DC_NA_1|C_DC_NA_1"}
EnergyHour = "M_IT_TB_1|M_ME_NC_1"
DEFAULT_IEC_TYPE = "M_ME_TF_1|M_ME_NC_1"

apcode_list = [
	"CumulativeActiveEnergyExportMeasured",
	"CumulativeActiveEnergyImportMeasured",
	"CumulativeReactiveEnergyExportMeasured",
	"CumulativeReactiveEnergyImportMeasured",
	"CumulativeApparentEnergyExportMeasured",
	"CumulativeApparentEnergyImportMeasured",
	"CumulativeArrayOutputEnergyMeasured",
	"TotalHoursOfFeedInOperation",
	"TotalHoursOfOperation",
	"CumulativeApparentEnergyMeasured",
	"CumulativeArrayOutputEnergyMeasuredInv",
	"CumulativeArrayImportEnergyMeasured",
	"CumulativeArrayReactiveEnergyExportMeasured",
	"CumulativeArrayReactiveEnergyImportMeasured",
	"CumulativeMVActiveEnergyExportMeasured",
	"CumulativeMVActiveEnergyImportMeasured",
	"CumulativeMVApparentEnergyMeasured",
	"CumulativeMVReactiveEnergyExportMeasured",
	"CumulativeMVReactiveEnergyImportMeasured"
]


def writefile(protocol, linelist):
	"""
	A function to write files
	:param protocol: Protocol to write
	:param linelist: FIle input
	:return: Status
	"""
	filename = ''
	if protocol == 'iec104':
		filename = 'iec104_assets.csv'
	elif protocol == 'backend':
		filename = 'iec104_backend.csv'
	#elif protocol == 'opcua':
	#	filename = 'opcua_assets.csv'
	#elif protocol == 'opcuajson':
	#	filename = 'opcua_fixed.json'
	else:
		print "You provided an unhandled protocol: %s" % protocol

	try:
		if protocol != 'opcuajson':
			outfile = open(filename, 'w')
			for line in linelist:
				outfile.write(line + '\n')
			outfile.close()
		else:
			with open('opcua_fixed.json', 'w') as fout:
				json.dump(linelist, fout)
	except Exception as ex:
		print "Failed to write file: %s due to %s" %(filename, str(ex))
		return False

	return True


def loadandcompareiec(lines, apcode_list, iec104assets):
	"""
	Load the existing iec104_assets.csv file if exists and create the final oupt
	:param lines: The input lines of the previous process
	:param apcode_list: The list with the apcodes to handle
	:param iec104assets: A switch to decide if the iec104_assets.csv exists or not
	:return:
	"""
	iecassetoutput = []  # iec104_assets.csv output list
	iecbackendoutput = []  # iec104_backend.csv output list

	liecdf = {}  # Load iec104_assets to check the previous input
	if iec104assets == '1':
		liecf = open('iec104_assets.csv', 'r')
		liecl = csv.reader(liecf, delimiter=',')
		headers_temp = liecl.next()
		# IOB NAME, CONTROLLER ID, INSOLAR PATH, TYPE, EUNIT, STATES, MDB, POLLING PERIOD, UUID, IOA, IEC TYPE, TAG
		for row in liecl:
			for h in headers_temp:
				if row[0] in liecdf:
					liecdf[row[0]].update({h: row[headers_temp.index(h)]})
				else:
					liecdf[row[0]] = {h: row[headers_temp.index(h)]}
		liecf.close()
	else:
		headers_temp = ['IOB NAME', 'CONTROLLER ID', 'INSOLAR PATH', 'TYPE', 'EUNIT', 'STATES', 'MDB', 'POLLING PERIOD',
				   'UUID', 'IOA', 'IEC TYPE', 'TAG']
	headers = list(headers_temp)
	headers.extend(h for h in lines[0] if h not in headers)
	lindex = 0
	inlines = []
	head = []
	# Generated list:
	# IOB NAME, CONTROLLER ID, INSOLAR PATH, TYPE, EUNIT, STATES, MDB, POLLING PERIOD, UUID, IOA, BACKEND TYPE, APCODE
	for line in lines:
		if lindex == 0:
			head = line
			lindex += 1
			continue
		inline = {}
		for x in range(len(line)):
			inline[head[x]] = line[x]
		inlines.append(inline)
	sortlines = sorted(inlines, key=lambda k: k['IOB NAME'])

	for sl in sortlines:
		fo = []  # iec104_assets.csv line
		bo = []  # iec104_backend.csv line
		iob = sl['IOB NAME']
		states = sl['STATES']
		ioa = sl['IOA'] + "|" + sl['IOA']
		if sl['IOA'] is not None and sl['IOA'] != '':
			ioa2 = sl['IOA'] + "|" + sl['IOA']
		else:
			ioa2 = 'SKIP'
		apcode = sl['APCODE']
		if apcode in apcode_list and sl['TYPE'] == 'AI':
			iec_type = EnergyHour
		else:
			iec_type = iectype.get(sl['TYPE'], DEFAULT_IEC_TYPE)
		tag = sl['UUID']
		if iob in liecdf:
			fline = liecdf.get(iob)
			if 'STATES' in fline:
				states = fline['STATES']
			if 'IOA' in fline:
				ioa = fline['IOA']
				if fline['IOA'] is not None and fline['IOA'] != '':
					ioa2 = fline['IOA']
				else:
					ioa2 = 'SKIP'
			if 'IEC TYPE' in fline:
				iec_type = fline['IEC TYPE']
			if 'TAG' in fline:
				tag = fline['TAG']
		states_length = len(states.split("|"))
		if states_length > 4 and (sl['TYPE'] == 'MI' or sl['TYPE'] == 'MO'):
			continue
		fo.append(iob)
		fo.append(sl['CONTROLLER ID'])
		fo.append(sl['INSOLAR PATH'])
		fo.append(sl['TYPE'])
		fo.append(sl['EUNIT'])
		fo.append(states)
		fo.append(sl['MDB'])
		fo.append(sl['POLLING PERIOD'])
		fo.append(sl['UUID'])
		if len(ioa.split("|")) < 3:
			fo.append(ioa.split("|")[0])
		else:
			fo.append(ioa)
		fo.append(iec_type)
		fo.append(tag)
		for xx in range(12, len(headers)):
			fo.append(sl[headers[xx]])
		foline = ','.join(fo)
		iecassetoutput.append(foline)

		bo.append(sl['BACKEND TYPE'])
		bo.append(sl['UUID'])
		bo.append(tag)
		if len(ioa2.split("|")) == 1 and len(iec_type.split("|")) > 1:
			bo.append(ioa2 + "|" + ioa2)
		else:
			bo.append(ioa)
		bo.append(iec_type)
		bo.append(states)
		boline = ';'.join(bo)
		if ioa2 == 'SKIP':  # Skip this line in case of empty IOA
			continue
		iecbackendoutput.append(boline)

	iecassetoutput.sort()
	headline = ','.join(headers)
	if 'TAG' not in headers:
		headline += ',TAG'
	iecassetoutput.insert(0, headline)
	iecbackendoutput.sort()

	return iecassetoutput, iecbackendoutput


def generatefirstinput(mlocs, svars, sets, msonly):
	"""
	A function to read iobattrs.csv file and generate the first input
	:param mlocs: Measurement locations data
	:param svars: State variables data
	:param sets: Settings data
	:param msonly: A switch if we want to process only measurement locations
	:return: A list with the output lines for the file
	"""
	mdf = open('iobattrs.csv', 'r')
	lmdf = csv.reader(mdf, delimiter=',')
	headers = lmdf.next()
	dmdf = {}
	for row in lmdf:
		for h in headers:
			if row[0] in dmdf:
				dmdf[row[0]].update({h: row[headers.index(h)]})
			else:
				dmdf[row[0]] = {h: row[headers.index(h)]}

	mdf.close()
	ms = dict()
	for ml in mlocs:
		ms[ml[0].replace("\"", "")] = ml
	sv = dict()
	for svar in svars:
		sv[svar[0].replace("\"", "")] = svar
	st = dict()
	for se in sets:
		st[se[0].replace("\"", "")] = se

	lines = []
	for name, asset in dmdf.iteritems():
		line = []
		if name.split('-')[0] in ms.keys():
			tms = ms[name.split('-')[0]]
			for header in headers:
				if header == 'INSOLAR PATH':
					line.append(tms[1].replace("\"", ""))
				elif header == 'EUNIT':
					line.append(tms[2].replace("\"", ""))
				elif header == 'UUID':
					line.append(tms[4].replace("\"", ""))
				elif header == 'TAG':
					line.append(tms[5].replace("\"", ""))
				else:
					line.append(asset[header])
			if 'UUID' not in headers:
				line.append(tms[4].replace("\"", ""))
			if 'TAG' not in headers:
				line.append(tms[5].replace("\"", ""))
			if 'APCODE' not in headers:
				line.append(tms[6].replace("\"", ""))
			if 'OPCUA_TAG' not in headers:
				line.append(tms[1].replace("\"", "").replace(" ", "")
							.replace("|", ".").replace("\\", "").replace("_", "").replace("-", "").replace("(", "")
							.replace(")", "").replace("%", ""))
		elif name.split('-')[0] in sv.keys() and msonly == 0:
			tms = sv[name.split('-')[0]]
			for header in headers:
				if header == 'INSOLAR PATH':
					line.append(tms[1].replace("\"", ""))
				elif header == 'EUNIT':
					line.append(tms[2].replace("\"", ""))
				elif header == 'STATES':
					line.append(tms[3].replace("\"", ""))
				elif header == 'UUID':
					line.append(tms[4].replace("\"", ""))
				elif header == 'TAG':
					line.append(tms[5].replace("\"", ""))
				else:
					line.append(asset[header])
			if 'UUID' not in headers:
				line.append(tms[4].replace("\"", ""))
			if 'TAG' not in headers:
				line.append(tms[5].replace("\"", ""))
			if 'APCODE' not in headers:
				line.append(tms[6].replace("\"", ""))
			if 'OPCUA_TAG' not in headers:
				line.append(tms[1].replace("\"", "").replace(" ", "")
							.replace("|", ".").replace("\\", "").replace("_", "").replace("-", "").replace("(", "")
							.replace(")", "").replace("%", ""))
		elif name.split('-')[0] in st.keys() and msonly == 0:
			tms = st[name.split('-')[0]]

			for header in headers:
				if header == 'INSOLAR PATH':
					line.append(tms[1].replace("\"", ""))
				elif header == 'EUNIT':
					line.append(tms[2].replace("\"", ""))
				elif header == 'UUID':
					line.append(tms[4].replace("\"", ""))
				elif header == 'TAG':
					line.append(tms[5].replace("\"", ""))
				else:
					line.append(asset[header])
			if 'UUID' not in headers:
				line.append(tms[4].replace("\"", ""))
			if 'TAG' not in headers:
				line.append(tms[5].replace("\"", ""))
			if 'APCODE' not in headers:
				line.append(tms[6].replace("\"", ""))
			if 'OPCUA_TAG' not in headers:
				line.append(tms[1].replace("\"", "").replace(" ", "")
							.replace("|", ".").replace("\\", "").replace("_", "").replace("-", "").replace("(", "")
							.replace(")", "").replace("%", ""))
		else:
			continue
		lines.append(line)
	lines.sort()
	headers.append('BACKEND TYPE')
	headers.append('APCODE')
	headers.append('OPCUA_TAG')
	lines.insert(0, headers)
	return lines


def fixsvars(mls, lsv):
	"""
	A function to convert the state variable data to a humanly readable form
	:param mls: Measurement location info
	:param lsv: State variable info
	:return: List with the state variable data
	"""
	nlsv =[]
	for tsv in lsv:
		m = 0
		ntsv = []
		ntsv.append(tsv[0])
		ntsv.append(tsv[1])
		ntsv.append(tsv[2])
		if tsv[6] == 'A':
			rep = reduce(lambda a, kv: a.replace(*kv), rep_ai.iteritems(), tsv[3])
			t_rep = rep.split(',')
			for i in t_rep:
				if i.find('DEFAULT') != -1 or i.find('0:') != -1:
					m = t_rep.index(i)
			t_rep.insert(0, t_rep.pop(m))
			f_rep = '|'.join(t_rep)
			ntsv.append(f_rep.lstrip())  # STATE MAP
		elif tsv[6] == 'D':
			rep = reduce(lambda a, kv: a.replace(*kv), rep_di.iteritems(), tsv[3])
			t_rep = rep.split(',')
			for i in t_rep:
				if i.find('DEFAULT') != -1 or i.find('0:') != -1:
					m = t_rep.index(i)
			t_rep.insert(0, t_rep.pop(m))
			f_rep = '|'.join(t_rep)
			ntsv.append(f_rep.lstrip())  # STATE MAP
		elif tsv[6] == 'S' or tsv[6] == 'M':
			rep = reduce(lambda a, kv: a.replace(*kv), rep_mi.iteritems(), tsv[3])
			t_rep = rep.split(',')
			for i in t_rep:
				if i.find('DEFAULT') != -1 or i.find('0:') != -1:
					m = t_rep.index(i)
			t_rep.insert(0, t_rep.pop(m))
			f_rep = '|'.join(t_rep)
			ntsv.append(f_rep.lstrip())  # STATE MAP
		else:
			ntsv.append(tsv[3])
		ntsv.append(tsv[4])
		ntsv.append(tsv[5])
		ntsv.append(tsv[7])
		nlsv.append(ntsv)
	return nlsv


def generatelists(mlocs, svars, sets):
	"""
	A function to generate the file input lists
	:param mlocs: Measurement locations data
	:param svars: State variables data
	:param sets: Settings data
	:return: Three lists for the respective data type
	"""
	db = []
	dbsv = []
	dbsets = []
	for mloc in mlocs:
		mloc_out = []
		m1 = ''  # IOB NAME
		if mloc[0]:
			m1 = '\"' + re.sub(r".*sid=(.*)%3A(.*)", "\\1:\\2", mloc[0]) + '\"'
		else:
			m1 = "\"\""
		mloc_out.append(m1)
		m2 = ''  # PATH
		if mloc[1]:
			m2 = '\"' + mloc[1] + '\"'
		else:
			m2 = "\"\""
		mloc_out.append(m2)
		m3 = ''  # EU
		if mloc[2]:
			m3 = '\"' + mloc[2] + '\"'
		else:
			m3 = "\"\""
		mloc_out.append(m3)
		m4 = ''  # SHARED ASI
		if mloc[3]:
			m4 = '\"' + mloc[3] + '\"'
		else:
			m4 = "\"\""
		mloc_out.append(m4)
		m5 = ''  # UUID
		if mloc[4]:
			m5 = '\"' + mloc[4] + '\"'
		else:
			m5 = "\"\""
		mloc_out.append(m5)
		m6 = ''  # TAG
		if mloc[5]:
			m6 = '\"' + mloc[5] + '\"'
		else:
			m6 = "\"\""
		mloc_out.append(m6)
		if mloc[6]:
			m7 = '\"' + mloc[6] + '\"'
		else:
			m7 = "\"\""
		mloc_out.append(m7)
		db.append(mloc_out)
	for svar in svars:
		svar_out = []
		s1 = ''  # IOB NAME
		if svar[0]:
			s1 = '\"' + re.sub(r".*sid=(.*)%3A(.*)", "\\1:\\2", svar[0]).split('iobname=')[1] + '\"'
		else:
			s1 = "\"\""
		svar_out.append(s1)
		s2 = ''  # PATH
		if svar[1]:
			s2 = '\"' + svar[1] + '\"'
		else:
			s2 = "\"\""
		svar_out.append(s2)
		s3 = ''  # EU
		if svar[2]:
			s3 = '\"' + svar[2] + '\"'
		else:
			s3 = "\"\""
		svar_out.append(s3)
		s4 = ''  # SHARED ASI
		if svar[3]:
			s4 = '\"' + svar[3] + '\"'
		else:
			s4 = "\"\""
		svar_out.append(s4)
		s5 = ''  # UUID
		if svar[4]:
			s5 = '\"' + svar[4] + '\"'
		else:
			s5 = "\"\""
		svar_out.append(s5)
		s6 = ''  # TAG
		if svar[5]:
			s6 = '\"' + svar[5] + '\"'
		else:
			s6 = "\"\""
		svar_out.append(s6)
		s7= ''  # TYPE
		if svar[0]:
			s7 = svar[0].split("sid=")[1].split("&")[0].split("_")[1][0]
		else:
			s7 = "\"\""
		# Keeping only Indicator status for switchesXXX:INDICXX
		if ('switches' in s1) and ('INDIC' in s1) and ('Indicator status' not in s2):
			continue
		# Keeping only Alarm status for secXXX:Z1_DETXX
		if ('sec' in s1) and ('_DET' in s1) and ('Alarm status' not in s2):
			continue
		# Keeping only Circuit breaker status for switchesXXX:CIRCBRXX
		if ('switches' in s1) and ('CIRCBR' in s1) and ('Circuit breaker status' not in s2):
			continue
		# Keeping only Switch status for switchesXXX:SWITCHXX
		if ('switches' in s1) and ('SWITCH' in s1) and ('Switch status' not in s2):
			continue
		# Keep only Communication status for XXXXXX:MALF
		if ('MALF' in s1) and ('Communication status' not in s2):
			continue
		svar_out.append(s7)
		s8 = ''  # APCODE
		if svar[6]:
			s8 = '\"' + svar[6] + '\"'
		else:
			s8 = "\"\""
		svar_out.append(s8)
		dbsv.append(svar_out)
	for seti in sets:
		sets_out = []
		t1 = ''  # IOB NAME
		if svar[0]:
			t1 = '\"' + re.sub(r".*sid=(.*)%3A(.*)", "\\1:\\2", seti[0]) + '\"'
		else:
			t1 = "\"\""
		sets_out.append(t1)
		t2 = ''  # PATH
		if seti[1]:
			t2 = '\"' + seti[1] + '\"'
		else:
			t2 = "\"\""
		sets_out.append(t2)
		t3 = ''  # EU
		if seti[2]:
			t3 = '\"' + seti[2] + '\"'
		else:
			t3 = "\"\""
		sets_out.append(t3)
		t4 = ''  # SHARED ASI
		if seti[3]:
			t4 = '\"' + seti[3] + '\"'
		else:
			t4 = "\"\""
		sets_out.append(t4)
		t5 = ''  # UUID
		if seti[4]:
			t5 = '\"' + seti[4] + '\"'
		else:
			t5 = "\"\""
		sets_out.append(t5)
		t6 = ''  # TAG
		if seti[5]:
			t6 = '\"' + seti[5] + '\"'
		else:
			t6 = "\"\""
		sets_out.append(t6)
		t7 = ''  # APCODE
		if seti[6]:
			t7 = '\"' + seti[6] + '\"'
		else:
			t7 = "\"\""
		sets_out.append(t7)
		dbsets.append(sets_out)

	return db, dbsv, dbsets


def getdata(cstring, sname):
	"""
	Function to retrieve data from the database
	:param cstring: Connection string
	:param sname: Site name
	:return: Set of data
	"""
	tempmlocs = ()
	tempsvars = ()
	tempsets = ()
	conn = None
	retrievestatus = True
	try:
		conn = psycopg2.connect(cstring)
		cur = conn.cursor()
		sname = (sname.strip(),)
		q_sites = "SELECT site_id, name from sites where name ~ %s"
		cur.execute(q_sites, sname)
		sites = cur.fetchall()
		siteid = ''

		if len(sites) == 0:
			print "No sites found!"
			retrievestatus = False
			return retrievestatus, tempmlocs, tempsvars, tempsets
		elif len(sites) > 1:
			for site in sites:
				print "Site: %-50s\tSite_id: %s" % (site[1], site[0])
			sid = raw_input("Select one site id: ")
			s_id = sid.strip()
		else:
			s_id = sites[0][0]

		siteid = (s_id,)

		q_mlocs = """
			        SELECT ms.asi AS asi,
			               (SELECT array_to_string(array_agg(nq.segname), '|')
			                  FROM (SELECT seg2.name AS segname
			                          FROM segments AS seg2,
			                               network_segments AS ns2
			                         WHERE ns2.network_id = ns.network_id
			                           AND ns2.lft <= ns.lft
			                           AND ns2.rgt >= ns.rgt
			                           AND seg2.segment_id = ns2.segment_id
			                      ORDER BY ns2.lft asc) AS nq) || '|' || ml.name AS path,
			               eu.name AS eu,
			               '' AS sharedAsi,
			               ml.measurement_location_id AS uid,
			               'mloc' AS tag,
			               ml.apcode AS apcode
			          FROM sites AS s,
			               networks AS n,
			               network_segments AS ns,
			               segments AS seg,
			               measurement_locations AS ml,
			               measurement_sources AS ms,
			               calculation_periods AS cp,
			               engineering_units AS eu,
			               agents AS ag
			         WHERE s.site_id = %s
			           AND s.site_id = n.associated_entity_id
			           AND n.network_id = ns.network_id
			           AND seg.segment_id = ns.segment_id
			           AND ml.segment_id = seg.segment_id
			           AND ms.measurement_location_id=ml.measurement_location_id
			           AND ms.calculation_period_id=cp.calculation_period_id
			           AND (cp.is_tr=true OR cp.name = 'Variant')
			           AND ms.engineering_unit_id = eu.engineering_unit_id
			           AND ms.handling_agent_id = ag.agent_id
			           AND (ag.name ~ 'TEL' OR ag.name ~'-c')
			           AND ag.agent_type_id = '12a666c2-8af9-11de-ad55-0090f586a869'
			      ORDER BY 1
			     """
		cur.execute(q_mlocs, siteid)
		tempmlocs = cur.fetchall()

		if len(tempmlocs) == 0:
			print "No parameters found!"
			return False, tempmlocs, tempsvars, tempsets

		q_svars = """
			        SELECT sv.asi AS asi,
			               (SELECT array_to_string(array_agg(nq.segname), '|')
			                  FROM (SELECT seg2.name AS segname
			                          FROM segments AS seg2,
			                               network_segments AS ns2
			                         WHERE ns2.network_id = ns.network_id
			                           AND ns2.lft <= ns.lft
			                           AND ns2.rgt >= ns.rgt
			                           AND seg2.segment_id = ns2.segment_id
			                      ORDER BY ns2.lft ASC) AS nq) || '|'|| sv.name AS path,
			               '' AS eu,
			                sa.asi AS sharedAsi,
			                sv.state_variable_id AS uid,
			                'svar' AS tag,
			                sv.apcode AS apcode
			            FROM sites AS s,
			                 networks AS n,
			                 network_segments AS ns,
			                 segments AS seg,
			                 state_variables AS sv,
			                 shared_asis AS sa,
			                 state_variable_types AS st,
			                 agents AS ag
			           WHERE s.site_id = %s
			             AND s.site_id=n.associated_entity_id
			             AND n.network_id=ns.network_id
			             AND seg.segment_id=ns.segment_id
			             AND sv.segment_id=ns.segment_id
			             AND sv.agent_id = ag.agent_id 
			             AND (ag.name ~ 'TEL' OR ag.name ~ '-c')
			             AND ag.agent_type_id = '12a666c2-8af9-11de-ad55-0090f586a869'
			             AND sv.asi ~ 'iobname'
			             AND sv.shared_asi_id = sa.shared_asi_id
			             AND st.state_variable_type_id = sv.state_variable_type_id
			        ORDER BY 1
			      """

		cur.execute(q_svars, siteid)
		tempsvars = cur.fetchall()

		if len(tempsvars) == 0:
			print "No state variables found!"
			return False, tempmlocs, tempsvars, tempsets

		q_sets = """
				   SELECT sets.asi AS asi,
		            	  (SELECT array_to_string(array_agg(nq.segname), '|')
		               	     FROM (SELECT seg2.name AS segname
		                        	 FROM segments AS seg2,
		                                  network_segments AS ns2
		                      	   	WHERE ns2.network_id = ns.network_id
		                        	  AND ns2.lft <= ns.lft
		                        	  AND ns2.rgt >= ns.rgt
		                        	  AND seg2.segment_id = ns2.segment_id
		                   		 ORDER BY ns2.lft ASC) AS nq) || '|'|| sets.name AS path,
		           		   eu.name AS eu,
		           		   '' AS sharedAsi,
		           		    sets.setting_id AS uid,
		           			'set' AS tag,
		           			sets.apcode AS apcode
		   			      FROM sites AS s,
		            		   networks AS n,
		            		   network_segments AS ns,
		            		   segments AS seg,
		            		   settings AS sets,
		            		   engineering_units AS eu,
		            		   agents AS ag
		  				 WHERE s.site_id = %s
		    			   AND s.site_id=n.associated_entity_id
		    			   AND n.network_id=ns.network_id
		    			   AND seg.segment_id=ns.segment_id
		    			   AND sets.segment_id=ns.segment_id
		    			   AND sets.agent_id = ag.agent_id 
		    			   AND (ag.name ~ 'TEL'OR ag.name ~ '-c') 
		    			   AND ag.agent_type_id = '12a666c2-8af9-11de-ad55-0090f586a869'
		    			   AND sets.asi ~ 'type=IOB'
		    			   AND sets.engineering_unit_id = eu.engineering_unit_id
		 			  ORDER BY 1
				"""

		cur.execute(q_sets, siteid)
		tempsets = cur.fetchall()

		if len(tempsets) == 0:
			print "No sets found!"

	except psycopg2.DatabaseError, e:
		print "I am unable to connect to the database: %s" % e
		retrievestatus = False

	finally:
		if conn:
			conn.close()

	return retrievestatus, tempmlocs, tempsvars, tempsets


def delfolder(tmploc, prevloc):
	"""
	A function to delete the input folder
	:param tmploc: Folder to delete
	:param prevloc: Prvious location
	:return:
	"""
	os.chdir(prevloc)

	shutil.rmtree(tmploc)
	print "Deleted temporary directory: %s" % tmploc


def svnfolder(sn):
	"""
	Function to create the svn folder and retrieve the data
	:param sn: The svn folder name
	:return: Status, the temporary folder path, the plant svn name, the external path
	"""
	tmpdir = ""
	status = True
	# Check for exact match
	svnls = "svn ls https://svn.inaccess.com/implementation | grep %s | sed -e 's/\///g' | grep -x %s" % (sn, sn)
	pname = os.popen(svnls).read().rstrip('\n')
	svnlsnum = "echo  %s | wc -w" % pname
	pnum = os.popen(svnlsnum).read().rstrip('\n')

	# Check for partial matches
	if int(pnum) != 1:
		svnls = "svn ls https://svn.inaccess.com/implementation | grep %s | sed -e 's/\///g'" % sn
		pname = os.popen(svnls).read().rstrip('\n')
		svnlsnum = "echo  %s | wc -w" % pname
		pnum = os.popen(svnlsnum).read().rstrip('\n')

	extp = ""
	if int(pnum) == 0:
		extp = "syglisis"
		svnls = "svn ls https://svn.inaccess.com/implementation/%s | grep %s | sed -e 's/\///g'" % (extp, sn)
		pname = os.popen(svnls).read().rstrip('\n')
		svnlsnum = "echo  %s | wc -w" % pname
		pnum = os.popen(svnlsnum).read().rstrip('\n')

	if int(pnum) == 0:
		print "No plants found with this name: %s" % sn
		status = False
	elif int(pnum) > 1:
		print "Multiple plants found \n Please retry using full name if possible."
		status = False

	if status:
		print "Plant SVN name is %s" % pname
		osname = platform.system()
		if osname.lower() == "linux":
			tdir = "/bin/mktemp -d -q /tmp/iec104.XXXXXXXX"
			tmpdir = os.popen(tdir).read().rstrip('\n')
		elif osname.lower() == "darwin":
			tdirstring = "/tmp/iec104."
			rlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
			for i in range(9):
				tdirstring = tdirstring + str(rlist[random.randint(0, 9)])
			tdir = "/bin/mkdir -p " + tdirstring
			tmpdir = os.popen(tdir).read().rstrip('\n')
			tmpdir = tdirstring

		# CHECK IF tmpdir was created
		if not os.path.exists(tmpdir):
			print "Could not create the temporary folder!"
			status = False

	return status, tmpdir, pname, extp


def getconnectionstring(configfile):
	"""
	Function to create the connection string
	:param configfile: Configuration file
	:return: The connection string
	"""
	connection_string = ""
	cp = ConfigParser.ConfigParser()
	with open(configfile, 'r') as config:
		cp.readfp(config)

	dbuser = cp.get("db", "user")
	dbname = cp.get("db", "database")
	dbhost = cp.get("db", "host")
	dbpasswd = cp.get("db", "password")

	connection_string = "dbname=%s user=%s host=%s password=%s" % (dbname, dbuser, dbhost, dbpasswd)
	return connection_string


def parseoptions():
	"""
	Function to parse options
	:return:
	"""
	connstring = ""
	plant = ""
	svnf = ""
	extp = ""
	state = True
	sitename = ""
	protocol = ""
	localdir = ""
	uselocal = False
	usage = "usage: %prog [options]"
	parser = OptionParser(usage)
	parser.add_option("-c", dest="config_file", help="Configuration File(Full path)", metavar="FILE")
	parser.add_option("-s", dest="site_name", help="Site name")
	parser.add_option("-v", dest="svn_name", help="Site svn folder name")
	parser.add_option("-p", dest="protocol", help="Server protocol")
	#parser.add_option("-a", dest="iec104_apcode", help="IEC104 apcode list")
	parser.add_option("-l", dest="localdir", help="Use local directory")
	(options, args) = parser.parse_args()

	if options.localdir:
		localdir = options.localdir
		uselocal = True

	if not options.config_file:
		print "ERROR: Provisioning configuration file not found"
		print "See help (run with -h)."
		state = False
	else:
		connstring = getconnectionstring(options.config_file)

	if not options.site_name:
		print "ERROR: You need to provide a site name"
		print "See help (run with -h)"
		state = False
	else:
		sitename = options.site_name

	if not options.svn_name and not uselocal:
		print "ERROR: You need to provide a svn folder name"
		print "See help (run with -h)"
		state = False

	if not options.protocol:
		print "ERROR: You need to provide a protocol"
		print "See help (run with -h)"
		state = False

	if not uselocal:
		svn = options.svn_name
		print "svn: %s" % svn
		(status, svnf, plant, extp) = svnfolder(svn)
		if not status:
			state = False

	protocol = options.protocol.lower()

	#apcode_list = []
	#if protocol == 'iec104':
	#	if not options.iec104_apcode:
	#		print "Error: You need to provide an IEC 104 apcode list for IEC 104 Type"
	#		print "See help (run with -h)"
	#		state = False
	#	else:
	#		try:
	#			apcode_list=[line.rstrip('\n') for line in open(options.iec104_apcode)]
	#		except Exception as ex:
	#			print "Error: Failed to open file: %s \n" % options.iec104_apcode
	#			print str(ex)
	#			state = False

	return state, connstring, svnf, plant, sitename, extp, protocol, uselocal, localdir #, apcode_list


if __name__=="__main__":
	(ostate, cs, sv, pln, sname, extp, protocol, uselocal, localdir) = parseoptions()
	if not ostate:
		sys.exit(1)

	loc = os.popen("pwd").read().rstrip('\n')
	if not uselocal:
		# Check out svn folder and use the temp directory
		print "Using temp directory %s" % sv
		svnco = "svn co https://svn.inaccess.com/implementation/%s/%s/trunk/Provisioning %s > /dev/null" % \
				(extp, pln, sv)
		os.system(svnco)
		os.chdir(sv)
	else:
		print "Using directory: %s" % localdir
		os.chdir(localdir)

	iobattrs = os.popen("ls | grep iobattrs.csv |  wc -l").read().rstrip('\n')

	if int(iobattrs) == 0:
		print "Exiting, missing iobattrs.csv file"
		delfolder(sv, loc)
		sys.exit(1)

	iec104assets = '0'
	iec104backend = '0'
	if protocol == "iec104":
		iec104assets = os.popen("ls | grep iec104_assets.csv |  wc -l").read().rstrip('\n').strip(' ')
		iec104backend = os.popen("ls | grep iec104_backend.csv |  wc -l").read().rstrip('\n').strip(' ')
	else:
		print "Exiting, Unhandled protocol"
		delfolder(sv, loc)
		sys.exit(1)

	print "Retrieving data for site: %s" % sname
	(rdstate, tmlocs, tsvars, tsets) = getdata(cs, sname)

	if not rdstate:
		print "Exiting, missing data!"
		delfolder(sv, loc)
		sys.exit(0)

	print "Merging data"
	(tmls, tsvs, tsts) = generatelists(tmlocs, tsvars, tsets)

	if len(tmls) == 0 and len(tsvs) == 0:
		print "Exiting, missing data matching!"
		delfolder(sv, loc)
		sys.exit(0)

	print "Fixing stat variables"
	ntsvs = fixsvars(tmls, tsvs)

	print "Generate files input"
	firstinput = []
	if protocol == "iec104":
		firstinput = generatefirstinput(tmls, ntsvs, tsts, 0)
	else:
		print "Exiting, Unhandled protocol: %s" % protocol
		delfolder(sv, loc)
		sys.exit(0)
	if len(firstinput) == 0:
		print "Exiting, no first input was generated!"
		delfolder(sv, loc)
		sys.exit(0)

	print "Generating files"
	if protocol == "iec104":
		iecassetoutput, iecbackendoutput = loadandcompareiec(firstinput, apcode_list, iec104assets)

		if len(iecassetoutput) == 0 and len(iecbackendoutput) == 0:
			print "There is an issue with the iec output for the final files generation!"
			delfolder(sv, loc)
			sys.exit(0)
		# Write file/s
		writeassets = writefile(protocol, iecassetoutput)
		writebackend = writefile('backend', iecbackendoutput)

		if not writeassets or not writebackend:
			print "There was an issue with writing the required files!"
			delfolder(sv, loc)
			sys.exit(1)

	if not uselocal:
		if protocol == "iec104":
			if iec104assets == '0':
				print "Adding iec104_assets.csv to svn"
				addassets = "svn add iec104_assets.csv"
				os.popen(addassets)
			if iec104backend == '0':
				print "Adding iec104_backend.csv to svn"
				addassets = "svn add iec104_backend.csv"
				os.popen(addassets)
			commit_string = "svn commit iec104_assets.csv -m \"IEC104 assets file: Committed iec104 asset csv file\""
			commit = os.popen(commit_string).read().rstrip('\n')
			print commit
			commit_string = "svn commit iec104_backend.csv -m \"IEC104 backend file: Committed iec104 backend csv file\""
			commit = os.popen(commit_string).read().rstrip('\n')
			print commit
		else:
			print "You provided an unhandled protocol: %s" % protocol
			delfolder(sv, loc)
			sys.exit(1)

		delfolder(sv, loc)
	else:
		os.chdir(loc)

	print "Finished!"
