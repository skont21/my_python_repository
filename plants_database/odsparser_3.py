#!/usr/bin/env python3
import ooolib
import json

class Spreadsheet:

	__VALUE_TYPE_TEXT = 0
	__VALUE_TYPE_NUMBER = 1
	__VALUE_TYPE_SLOT = 2
	__VALUE_TYPE_ID = 3

	def __init__(self, fname):
		self.fname = fname
		self.doc = ooolib.Calc(opendoc = fname)

	def __error_message(self, m = ''):
		if self.__current_h1:
			h1 = '"' + self.__current_h1
			if self.__current_index != None:
				h1 += ' ' + str(self.__current_index)
			h1 += '".'
		else:
			h1 = ''
		m = '"' + self.__current_sheet + '".' + h1 + '"' + \
			self.__current_cap + '": ' + str(m)
		return m

	def __unescape(self, string):
		string = string.replace("&lt;", "<")
		string = string.replace("&gt;", ">")
		string = string.replace("&amp;", "&")
		return string

	def __get_value(self, row, col, value_type = __VALUE_TYPE_TEXT):
		doc = self.doc
		cell_value = doc.get_cell_value(col, row)
		if cell_value == None:
			if value_type == self.__VALUE_TYPE_NUMBER:
				value = 0
			else:
				value = None
		elif cell_value[0] == 'formula':
			raise TypeError('ODS formula')
		else:
			value = cell_value[1]
			if value_type == self.__VALUE_TYPE_NUMBER:
				try:
					value = int(value)
				except ValueError:
					raise ValueError(self.__error_message('Expected' + \
						' integer, got "' + value + '"'))
			elif value_type == self.__VALUE_TYPE_SLOT:
				value = value.split('(')[0].rstrip()
			elif value_type == self.__VALUE_TYPE_ID:
				value = value.split('(')[0].rstrip()
				try:
					value = int(value) - 1
				except ValueError:
					raise ValueError(self.__error_message('Expected' + \
						' \"<ID>\" or \"<ID> (<string>)\", got "' + \
						value + '"'))
		if value_type == self.__VALUE_TYPE_TEXT and value is not None:
			value = self.__unescape(value)
		return value

	def __get_row_values(self, row, ncols, value_type):
		values = []
		for col in range(2, ncols + 2):
			self.__current_index = col - 1
			v = self.__get_value(row, col, value_type)
			values.append(v)
		return values

	def __get_table_values(self, start_row, ncols):
		# Find number of rows
		row = start_row
		while True:
			try:
				value = self.__get_value(row, 1)
				if value == None:
					break
			except:
				pass
			row += 1
		end_row = row
		# Get values
		values = []
		for col in range(2, ncols + 2):
			row_values = []
			for row in range(start_row, end_row):
				v = self.__get_value(row, col)
				row_values.append(v)
			values.append(row_values)
		return values

	def __parse_sheet(self, index):
		doc = self.doc
		doc.set_sheet_index(index)
		sheet_data = {}
		level_data = sheet_data
		level = 0
		col_list = False
		nvalcol = 0
		(cols, rows) = doc.get_sheet_dimensions()
		for row in range(2, rows + 1):
			cell_value = doc.get_cell_value(1, row)
			if cell_value == None:
				# Ignore empty lines
				continue
			cap = cell_value[1]
			if cap == '-':
				# Ignore line connectors
				continue
			if cap[-1] == ':':
				cap = cap.rstrip(':')
				if cap == 'ID':
					# Find number of columns
					col_list = True
					nvalcol = 1
					for col in range(2, cols + 1):
						cell_value = doc.get_cell_value(col, row)
						if cell_value == None:
							break
						else:
							nvalcol = col
					nvalcol -= 1
				else:
					c = cap.split()
					if len(c) > 1 and c[0] == 'Number' and c[1] == 'of':
						value_type = self.__VALUE_TYPE_NUMBER
					elif cap == 'Slot':
						value_type = self.__VALUE_TYPE_SLOT
					else:
						value_type = self.__VALUE_TYPE_TEXT
						c = cap.split('(')
						cap = c[0].rstrip()
						if c[0][-2:] == 'ID' or (len(c) > 1 and c[1][-3:] == 'ID)'):
							value_type = self.__VALUE_TYPE_ID
						if c[0] == 'Communication ID':
							value_type = self.__VALUE_TYPE_TEXT
					# Acquire values
					self.__current_cap = cap
					try:
						if col_list:
							list_data = self.__get_row_values(row, nvalcol, value_type)

							if cap in level_data.keys():
								level_data[cap] += list_data
							else:
								level_data[cap] = list_data
						else:
							self.__current_index = None
							level_data[cap] = self.__get_value(row, 2, value_type)
					except TypeError:
						pass
			else:
				# Parse headers
				if cap == 'Signal connection' or cap == 'Connection':
					h2 = cap

					if h2 in sheet_data.keys():
						level_data = sheet_data[h1][h2]
					else:
						level_data = {}
					sheet_data[h1][h2] = level_data
				elif cap == 'Door ID':
					h2 = cap
					sheet_data[h1][h2] = self.__get_table_values(row + 1, nvalcol)
					break
				else:
					h1 = cap
					self.__current_h1 = h1
					if h1 in sheet_data.keys():
						level_data = sheet_data[h1]

					else:
						level_data = {}
					if cap == 'Router reset contact':
						col_list = True
						nvalcol = 1
					sheet_data[h1] = level_data
					if h1 == 'Settings':
						if nvalcol == 0:
							s1 = doc.get_cell_value(1, row + 1)[1].split('(')[0].rstrip()

							if s1 not in level_data.keys():
								nvalcol = 1
		return sheet_data

	def __parse_spreadsheet(self):
		doc = self.doc
		data = {}
		nsheets = doc.get_sheet_count()
		# Search for sheet lists
		for si in range(0, nsheets):
			doc.set_sheet_index(si)
			sheet_name = doc.get_sheet_name()
			try:
				n = sheet_name.rsplit(None, 1)
				i = int(n[1])
				if i == 1:
					data[n[0]] = [si]
				else:
					data[n[0]].append(si)
			except:
				if sheet_name[0] == '_':
					# Ignore auxiliary sheets
					continue
				data[sheet_name] = si
		# Parse sheets
		for k in data.keys():
			if type(data[k]) == list:
				for i, index in enumerate(data[k]):
					self.__current_sheet = k + ' ' + str(i + 1)
					self.__current_h1 = None
					data[k][i] = self.__parse_sheet(index)
			else:
				self.__current_sheet = k
				self.__current_h1 = None
				data[k] = self.__parse_sheet(data[k])
		return data

	def __fix_dict_lists(self, d):
		for k in d.keys():
			t = type(d[k])
			if t == dict:
				self.__fix_dict_lists(d[k])
			elif t == list:
				d[k] = []

	def __fix_lists(self, data, num, name):
		d = data[name]
		if num == 0:
			t = type(d)
			if t == dict:
				self.__fix_dict_lists(d)
			elif t == list:
				data[name] = []

	def __compat_fix_1(self, data_top, data):
		def get_rd_values(data_top, rdid):
			rd = data_top['Remote-i/o device']['Remote-i/o device']
			cid = None
			sl = None
			sp = None
			ba = None
			if rdid != None:
				rdid = int(rdid)
				try:
					cid = rd['Connection']['Controller ID'][rdid]
					sl = rd['Connection']['Slot'][rdid]
					sp = rd['Connection']['Serial port'][rdid]
					ba = rd['Bus address'][rdid]
				except IndexError:
					pass
			return (cid, sl, sp, ba)
		t = type(data)
		if t == dict:
			for k in data:
				if k == 'Signal type':
					st = data[k]
					sc = data['Signal connection']
					if type(st) == list:
						l = len(st)
						if 'Remote-i/o device ID' in sc.keys():

							if 'Serial Port' not in sc.keys():

								sc['Serial port'] = [None] * l
							if 'Modbus address' not in sc.keys():

								sc['Modbus address'] = [None] * l
						for j in range(l):
							if st[j] == 'Local digital':
								st[j] = 'Digital'
							elif st[j] == 'Remote digital':
								st[j] = 'Modbus digital'
								rdv = get_rd_values(data_top, sc['Remote-i/o device ID'][j])
								if 'Controller ID' in sc.keys():

									sc['Controller ID'][j] = rdv[0]
								sc['Slot'][j] = rdv[1]
								sc['Serial port'][j] = rdv[2]
								sc['Modbus address'][j] = rdv[3]
					else:
						if st == 'Local digital':
							data[k] = 'Digital'
						elif st == 'Remote digital':
							data[k] = 'Modbus digital'
							rdv = get_rd_values(data_top, sc['Remote-i/o device ID'])
							if 'Controller ID' in sc.keys():

								sc['Controller ID'] = rdv[0]
							sc['Slot'] = rdv[1]
							sc['Serial port'] = rdv[2]
							sc['Modbus address'] = rdv[3]
				else:
					self.__compat_fix_1(data_top, data[k])
		elif t == list:
			for i in range(len(data)):
				self.__compat_fix_1(data_top, data[i])
		return

	def __compat_fix_2(self, data):
		try:
			iia = data['PV array']['Inverter']['IP address']
		except KeyError:
			return
		data['PV array']['Inverter']['Signal connection']['IP address'] = iia
		return

	def __compat_fix_3(self, data):
		try:
			mtht = data['PV panel group']['Settings']['Module temperature high threshold']
		except KeyError:
			return
		if type(mtht) != list:
			data['PV panel group']['Settings']['Module temperature high threshold'] = [mtht]
		try:
			mtlt = data['PV panel group']['Settings']['Module temperature low threshold']
		except KeyError:
			return
		if type(mtlt) != list:
			data['PV panel group']['Settings']['Module temperature low threshold'] = [mtlt]
		return

	def __compat_fix_4(self, data):
		for s in ['Wind speed sensor', 'Rain gauge']:
			d = data['Weather station'][s]
			l = len(d['Signal type'])
			sc = d['Signal connection']
			if 'Gain' not in sc.keys():

				sc['Gain'] = [None] * l
			for i in range(l):
				st = d['Signal type'][i]
				if not st:
					continue
				if st == 'Local analog' or st == 'Analog':
					sc['Gain'][i] = sc['PGA gain'][i]
				elif st[-5:] == 'pulse':
					sc['Gain'][i] = sc['pGain'][i]
				elif st == 'Modbus Digital':
					if 'pGain' in sc.keys():

					    sc['Gain'][i] = sc['pGain'][i]

	def get_version(self):
		from zipfile import ZipFile
		zf = ZipFile(self.fname)
		for f in zf.infolist():
			if f.orig_filename == 'meta.xml':
				for t in zf.read(f).decode('utf-8').split('<'):
					if 'meta:user-defined meta:name="Version"' in t:
						v = t.split('>')[1].split('.')
						if len(v) == 1:
							v = (v[0], 0)
						return (int(v[0]), int(v[1]))
		return (0, 0)

	def parse(self):
		data = self.__parse_spreadsheet()
		try:
			n = data['Plant']['Number of transformers']
			self.__fix_lists(data, n, 'TCP')
		except KeyError:
			pass
		try:
			n = data['Plant']['Number of TCPs']
			self.__fix_lists(data, n, 'TCP')
		except KeyError:
			pass
		try:
			n = data['PV panel group']['Number of string monitors']
			self.__fix_lists(data['PV panel group'], n, 'String monitor')
		except KeyError:
			pass
		try:
			n = data['Reference cell']['Number of reference cells']
			self.__fix_lists(data, n, 'Reference cell')
		except KeyError:
			pass
		try:
			n = data['Plant']['Number of weather stations']
			self.__fix_lists(data, n, 'Weather station')
		except KeyError:
			pass
		try:
			n = sum(data['PV array']['PV array']['Number of voltmeters'])
			self.__fix_lists(data['PV array'], n, 'Voltmeter')
			n = sum(data['PV array']['PV array']['Number of ammeters'])
			self.__fix_lists(data['PV array'], n, 'Ammeter')
		except KeyError:
			pass
		try:
			n = data['Electrical panel']['Number of electrical panels']
			self.__fix_lists(data, n, 'Electrical panel')
			n = sum(data['Electrical panel']['Electrical panel']['Number of circuit breaker groups'])
			self.__fix_lists(data['Electrical panel'], n, 'Circuit breaker group')
			n = sum(data['Electrical panel']['Electrical panel']['Number of surge arrester groups'])
			self.__fix_lists(data['Electrical panel'], n, 'Surge arrester group')
			n = sum(data['Electrical panel']['Electrical panel']['Number of fuse groups'])
			self.__fix_lists(data['Electrical panel'], n, 'Fuse group')
			n = sum(data['Electrical panel']['Electrical panel']['Number of switch groups'])
			self.__fix_lists(data['Electrical panel'], n, 'Switch group')
			n = sum(data['Electrical panel']['Electrical panel']['Number of indicator groups'])
			self.__fix_lists(data['Electrical panel'], n, 'Indicator group')
			n = sum(data['Electrical panel']['Electrical panel']['Number of protection devices'])
			self.__fix_lists(data['Electrical panel'], n, 'Protection device')
			n = sum(data['Electrical panel']['Electrical panel']['Number of multimeters'])
			self.__fix_lists(data['Electrical panel'], n, 'Multimeter')
		except KeyError:
			pass
		try:
			n_s = data['Plant']['Number of shelters']
			n = sum(data['Room']['Room']['Number of access-controlled doors'])
			if n_s == 0 or n == 0:
				self.__fix_lists(data, 0, 'Door')
			self.__fix_lists(data, n_s, 'Room')
			self.__fix_lists(data, n_s, 'Shelter')
		except KeyError:
			pass
		try:
			n = data['Plant']['Number of security applications']
			self.__fix_lists(data, n, 'Security app')
			for i in range(n):
				m = data['Security app'][i]['Number of actuator zones']
				self.__fix_lists(data['Security app'][i], m, 'Actuator zone')
				self.__fix_lists(data['Security app'][i], m, 'Actuator')
				m = data['Security app'][i]['Number of alarm zones']
				self.__fix_lists(data['Security app'][i], m, 'Alarm zone')
				self.__fix_lists(data['Security app'][i], m, 'Alarm')
				self.__fix_lists(data['Security app'][i], m, 'Settings')
		except KeyError:
			pass
		try:
			n = data['RFID tag']['Number of RFID tags']
			self.__fix_lists(data, n, 'RFID tag')
		except KeyError:
			pass
		try:
			n = data['Pump station']['Number of pump stations']
			self.__fix_lists(data, n, 'Pump station')
		except KeyError:
			pass

		if 'Remote-io device' in data.keys():
			data['Remote-i/o device'] = data['Remote-io device']
			del(data['Remote-io device'])
			self.__compat_fix_1(data, data)
		self.__compat_fix_2(data)
		self.__compat_fix_3(data)
		self.__compat_fix_4(data)
		return data

def print_data(data):

	def print_value(n, v):
		if isinstance(v,bytes):
			print(n, '=', v.encode('utf-8'))
		else:
			print(n, '=', v)

	def print_list(data, str = ''):
		if len(data) == 0:
			print("{} = ".format(str))
			# print('[%s = []' % str)
		for i in range(len(data)):
			t = type(data[i])
			s = "{}[{:d}]".format(str,i)
			# s = '%s[%d]' % (str, i)
			if t == list:
				print_list(data[i], s)
			elif t == dict:
				print_dict(data[i], s + '[')
			else:
				print_value("{}[{:d}]".format(str,i),data[i])
				# print_value('[%s[%d]' % (str, i), data[i])

	def print_dict(data, str = ''):
		for k in data.keys():
			t = type(data[k])
			s = "{} {}".format(str,k)
			# s = '%s\'%s\']' % (str, k)
			if t == list:
				print_list(data[k], s)
			elif t == dict:
				print_dict(data[k], s + '[')
			else:
				print_value("{} {}".format(str,k), data[k])
				# print_value('[%s\'%s\']' % (str, k), data[k])

	print_dict(data)


if __name__=='__main__':
	import sys
	argv = sys.argv
	ops = ['-fv', '-p', '-pd', '-pj']
	argv_len = len(argv)
	if argv_len != 3 or argv[1] not in ops:
		print('Usage: odsparser.py { -fv | -p | -pd | -pj } <filename>')
		sys.exit(1)
	try:
		s = Spreadsheet(argv[2])
	except IOError:
		print("Error: Cannot open file {}".format(argv[2]))
		sys.exit(1)
	except:
		print("Error: File '{}' is not valid".format(argv[2]))
		# print('Error: File \'%s\' is not valid' % argv[2])
		sys.exit(1)
	data = s.parse()
	if argv[1] == '-fv':
		fv = s.get_version()
		print(str(fv[0])+"."+str(fv[1]))
		# print('%d.%d' % fv)
	elif argv[1] == '-p':
		print_data(data)
	elif argv[1] == '-pd':
		print(data)
	elif argv[1] == '-pj':
		print(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4).encode('utf-8'))
