import odsparser_3
import ooolib
import json

file = "/media/spiros/my_data/pvplants/VN_Sungrow_Fuji_40MWp_2864/VN_Sungrow_Fuji_40MWp_2864_InstallationData.ods"

s=odsparser.Spreadsheet(file)
data=s.parse()

#print(type(data))

#data=odsparser.print_data(data)
def find_slave(data):
    elpanel_dict = data['Electrical panel']
    if 'Slave PPC' in elpanel_dict.keys():
        slave_man= elpanel_dict['Slave PPC']['Manufacturer'][0].encode('utf-8')
        slave_man_index = list(elpanel_dict.keys()).index('Slave PPC')
        slave_model =  elpanel_dict.values()[slave_man_index-1]['Name'][0].encode('utf-8')
    return slave_man,slave_model

print(find_slave(data))
