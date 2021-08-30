import xml.etree.ElementTree as ET
from itertools import groupby
from itertools import chain
import transliterate
import datetime
import modules
import xlwt
import re


with open('guides.sql', 'r', encoding='utf-8') as file:
    sql = file.readlines()

insert_list = []

pat = re.compile(r'(INSERT).+')
for x in sql:
    s = pat.search(x)
    if s:
        insert_list.append(s.group())

values_list = []
pat2 = re.compile(r'(?<=\().*?(?=\))')
for x in insert_list:
    res = pat2.findall(x)
    values_list += res

MapPoint_list = []
pat3 = re.compile(r"\d+,'MapPoint'")
for x in values_list:
    s = pat3.search(x)
    if s:
        MapPoint_list.append(x)

pat_pod = re.compile(r'<Type>POD')
pat_pdz = re.compile(r'<Type>PDZ')

POD_PDZ = []
for x in MapPoint_list:
    s1 = pat_pod.search(x)
    s2 = pat_pdz.search(x)
    if s1 or s2:
        POD_PDZ.append(x)

pat_name = re.compile(r'(?<=\<Code>).{5}(?=\<)')
names_five = []
for x in POD_PDZ:
    s = pat_name.search(x)
    if s:
        names_five.append(x)

delete_id = []
pat_id = re.compile(r'\d+')
for x in names_five:
    s = pat_id.findall(x)
    delete_id.append(s[0])



# Opening existing XML file with points
with open('Points.xml', 'r', encoding='utf-8') as file:
    data = file.read()

# Start parsing of XML file
root = ET.fromstring(data)

# Key values in XML file: version, code, codelat, name , namelat, lon, lat, magnetic declination, type
names = []

def try_except(xml, word):
    try:
        parameter = xml.find(word).text
    except:
        parameter = None
    return parameter

def try_false(xml, word):
    try:
        parameter = xml.find(word).text
    except:
        parameter = "false"
    return parameter



for mappoint in root.findall('MapPoint'):
    version = mappoint.get('Version')
    code = mappoint.find('Code').text
    code_lat = try_except(mappoint, 'CodeLat')
    name = try_except(mappoint, 'Name')
    nameLat = try_except(mappoint, 'NameLat')
    magnetic = try_except(mappoint, 'MagneticDeclination')
    type_ = try_except(mappoint, 'Type')
    lat = try_except(mappoint, 'Latitude')
    lon = try_except(mappoint, 'Longitude')
    airport_type = try_except(mappoint, 'AirportType')
    AirportUsageType = try_except(mappoint, 'AirportUsageType')
    AirportOwnerType = try_except(mappoint, 'AirportOwnerType')
    class_ = try_except(mappoint, 'Class')
    CallLetter = try_except(mappoint, 'CallLetter')
    Id = try_except(mappoint, 'Id')
    ObjectId = try_except(mappoint, 'ObjectId')
    IsACP = try_false(mappoint, 'IsACP')
    IsInOut = try_false(mappoint, 'IsInOut')
    IsInOutCIS = try_false(mappoint, 'IsInOutCIS')
    IsGateWay = try_false(mappoint, 'IsGateWay')
    IsTransferPoint = try_false(mappoint, 'IsTransferPoint')
    IsTransferPoint_ACP = try_false(mappoint, 'IsTransferPoint_ACP')
    IsInAirway = try_false(mappoint, 'IsInAirway')
    IsMvl = try_false(mappoint, 'IsMvl')
    LocalChange = try_false(mappoint, 'LocalChange')
    if lat and lon != None:
        lst = [version, code, code_lat, name, nameLat, magnetic, type_, lat, lon, airport_type, AirportUsageType,
           AirportOwnerType, class_, CallLetter, Id, ObjectId, IsACP, IsInOut,
           IsInOutCIS, IsGateWay, IsTransferPoint, IsTransferPoint_ACP, IsInAirway, IsMvl, LocalChange]
        names.append(lst)

# Opening ARINC file
text = open('GKOVD_DV2108Bv15.txt', 'r',
            encoding='utf-8').readlines()

# finding all points
all_points = list(modules.get_points(text))
points = list(modules.get_data(all_points))
points = list(modules.unique(points))

# getting points only inside polygon
inside_points = list(modules.inside(points))

# # finding all routes
# routes = list(modules.get_routes(text))
# mvl = list(modules.get_route_info(routes))
# filtred_routes = list(modules.select_routes(mvl, inside_points))
# filtred_routes = list(modules.unique(filtred_routes))
# filtred_routes = sorted(filtred_routes, key=lambda x: x[0])
# filtred_routes = [list(g) for k, g in groupby(filtred_routes, lambda s: s[0])]
#
# # selecting routes with more than 2 points on them
# more2 = list(modules.count_list(filtred_routes))
# more2 = list(chain.from_iterable(more2))
# more2 = list(modules.counter_of_points(more2))
# only_in_trass_points = modules.only_in_trass(more2)
# only_in_trass_points = list(modules.unique(only_in_trass_points))
# names_trass_points = list(modules.names(only_in_trass_points))
#
# # getting points in filtered routes
# filtred_inside_points = [item for item in inside_points if item[0] in names_trass_points]

# transform coordinates from gradus to radians
rad_points = list(modules.radians(inside_points))

# transform coordinates for xls file
# xls_point = list(modules.gradus(filtred_inside_points))

# getting names of mdp_points from XML file
mdp_points = [item[1] for item in names]

# getting names from arinc file and transliterate them into russian
arinc_points = [transliterate.translit(item[0], 'ru') for item in rad_points]

# finding common points in mdp and arinc
common_points = [item for item in arinc_points if item in mdp_points]

# Common points with old parameters from XML file
common_points_params = [item for item in names if item[1] in common_points]

# Common points with old params and new coordinatse from arinc
common_points_arinc = sorted([item for item in rad_points if transliterate.translit(item[0], 'ru') in common_points])

# Replace with new coordinates from arinc
for x in common_points_arinc:
    for y in common_points_params:
        if transliterate.translit(x[0], 'ru') == y[1]:
            y[7] = x[1]
            y[8] = x[2]

common_points_params_sorted = sorted(common_points_params, key=lambda x: transliterate.translit(x[1], 'ru'))

# New points from arinc file included in routes
new_arinc_points = [item for item in rad_points if
                    transliterate.translit(item[0], 'ru') not in common_points and len(item[0]) == 5]

# New points from arinc for XLS file
# xls_new_arinc_points = [item for item in xls_point if
#                    transliterate.translit(item[0], 'ru') not in common_points and len(item[0]) == 5]

# xls_arinc_transformed = [modules.insert_arinc(item) for item in xls_new_arinc_points]

# Airdromes, GeoPoints, Landing and other types we should save
other_points = [item for item in names if item[1] not in common_points and item[6] != "POD"
                and item[6] != "PDZ"]

first = [('Type', 'Code', 'CodeLat', 'Name', 'NameLat', 'Coord', 'MagDecl'
          , 'Elevation', 'H', 'Habs', 'Comment')]

final_old = common_points_params + other_points


# xls_old_transformed = [modules.insert_old(item) for item in final_old]
#
# xls_all = first+ xls_arinc_transformed + xls_old_transformed

# filling excel table
#
# filename = xlwt.Workbook()
# sheet = filename.add_sheet('New_points')
#
# for i, l in enumerate(xls_all):
#     for j, col in enumerate(l):
#         sheet.write(i, j, col)
#
# filename.save('new_points.xls')

class FillXML:

    def __init__(self, object_id, id, name, lat, lon):
        self.object_id = object_id
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.data1 = '\t<MapPoint Version="1" IsDeleted="false">\n'
        self.data2 = '\t\t<ObjectId>%s</ObjectId>\n' % self.object_id
        self.data3 = '\t\t<Id>%s</Id>\n' % self.id
        self.data4 = '\t\t<LocalChange>false</LocalChange>\n'
        self.data5 = '\t\t<LastUpdate>%s</LastUpdate>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data6 = '\t\t<Code>%s</Code>\n' % transliterate.translit(self.name, 'ru')
        self.data7 = '\t\t<CodeLat>%s</CodeLat>\n' % self.name
        self.data8 = '\t\t<Name>%s</Name>\n' % transliterate.translit(self.name, 'ru')
        self.data9 = '\t\t<NameLat>%s</NameLat>\n' % self.name
        self.data10 = '\t\t<Names />\n'
        self.data11 = '\t\t<NamesXml />\n'
        self.data12 = '\t\t<Comment />\n'
        self.data13 = '\t\t<BeginDate>0001-01-01T00:00:00Z</BeginDate>\n'
        self.data14 = '\t\t<EndDate>0001-01-01T00:00:00Z</EndDate>\n'
        self.data15 = '\t\t<ShowOnChart>true</ShowOnChart>\n'
        self.data16 = '\t\t<Latitude>%s</Latitude>\n' % self.lat
        self.data17 = '\t\t<Longitude>%s</Longitude>\n' % self.lon
        self.data18 = '\t\t<Elevation>0</Elevation>\n'
        self.data19 = '\t\t<MagneticDeclination>0</MagneticDeclination>\n'
        self.data20 = '\t\t<Frequencies />\n'
        self.data21 = '\t\t<Type>PDZ</Type>\n'
        self.data22 = '\t\t<IsACP>false</IsACP>\n'
        self.data23 = '\t\t<IsInOut>false</IsInOut>\n'
        self.data24 = '\t\t<IsInOutCIS>false</IsInOutCIS>\n'
        self.data25 = '\t\t<IsGateWay>false</IsGateWay>\n'
        self.data26 = '\t\t<IsTransferPoint>false</IsTransferPoint>\n'
        self.data27 = '\t\t<IsTransferPoint_ACP>false</IsTransferPoint_ACP>\n'
        self.data28 = '\t\t<IsInAirway>false</IsInAirway>\n'
        self.data29 = '\t\t<IsMvl>true</IsMvl>\n'
        self.data30 = '\t\t<AirportType>Airport</AirportType>\n'
        self.data31 = '\t\t<AirportUsageType>NotDefined</AirportUsageType>\n'
        self.data32 = '\t\t<AirportOwnerType>NotDefined</AirportOwnerType>\n'
        self.data33 = '\t\t<Class>Unknown</Class>\n'
        self.data34 = '\t\t<AftnAddr />\n'
        self.data35 = '\t\t<CallLetter />\n'
        self.data36 = '\t\t<WorkingTimeRange IsCancelled="false" minlevel="M/M=0/FL=0/FWD" maxlevel="M/M=16100/FL=528/FWD">\n'
        self.data37 = '\t\t\t<ObjectId>0</ObjectId>\n'
        self.data38 = '\t\t\t<Id>0</Id>\n'
        self.data39 = '\t\t\t<IntervalOfClosing>false</IntervalOfClosing>\n'
        self.data40 = '\t\t\t<Reserv>false</Reserv>\n'
        self.data41 = '\t\t\t<Kind>Always</Kind>\n'
        self.data42 = '\t\t\t<Begin>%s</Begin>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data43 = '\t\t\t<End>%s</End>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data44 = '\t\t\t<TimeSpanRanges />\n'
        self.data45 = '\t\t\t<Comment />\n'
        self.data46 = '\t\t\t<Sources />\n'
        self.data47 = '\t\t</WorkingTimeRange>\n'
        self.data48 = '\t\t<Runways />\n'
        self.data49 = '\t</MapPoint>\n'

    def make_list(self):
        self.data_list = [self.data1, self.data2, self.data3, self.data4, self.data5, self.data6, self.data7,
                          self.data8, self.data9, self.data10, self.data11, self.data12, self.data13, self.data14,
                          self.data15, self.data16, self.data17, self.data18, self.data19, self.data20, self.data21,
                          self.data22, self.data23, self.data24, self.data25, self.data26, self.data27, self.data28,
                          self.data29, self.data30, self.data31, self.data32, self.data33, self.data34, self.data35,
                          self.data36, self.data37, self.data38, self.data39, self.data40, self.data41, self.data42,
                          self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49]
        return self.data_list




class FamiliarNames:

    def __init__(self, lst, num):
        self.lst = lst
        version = lst[0] if lst[0] is not None else '0'
        code = lst[1]
        code_lat = transliterate.translit(lst[1], 'ru', reversed=True)
        name = lst[1] if lst[3] is None else lst[3]
        name_lat = transliterate.translit(lst[1], 'ru', reversed=True) if lst[4] is None else ""
        magnetic = 0 if lst[5] is None else lst[5]
        type_ = "" if lst[6] is None else lst[6]
        if "ь" in code or "Ь" in code:
            code_lat = ""
            name_lat = ""
        if len(code) == 4 and "Ь" in code:
            code_lat = transliterate.translit(lst[1], 'ru', reversed=True)
            code_lat = code_lat.replace("'", "X")
            name_lat = code_lat
        lat = lst[7]
        lon = lst[8]
        airport_type = "Airport" if lst[9] is None else lst[9]
        AirportUsageType = "NotDefined" if lst[10] is None else lst[10]
        AirportOwnerType = "NotDefined" if lst[11] is None else lst[11]
        class_ = "Unknown" if lst[12] is None else lst[12]
        CallLetter = "" if lst[13] is None else lst[13]
        IsACP = lst[16]
        IsInOut = lst[17]
        IsInOutCIS = lst[18]
        IsGateWay = lst[19]
        IsTransferPoint = lst[20]
        IsTransferPoint_ACP = lst[21]
        IsInAirway = lst[22]
        IsMvl = lst[23]
        LocalChange = lst[24]
        self.data0 = '<?xml version="1.0" encoding="utf-16"?>\n'
        self.data2 = f"""<MapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Version="{version}" IsDeleted="false">\n"""
        self.data3 = f'\t<ObjectId>{num}</ObjectId>\n'
        self.data4 = f'\t<Id>{num}</Id>\n'
        self.data5 = f'\t<LocalChange>{LocalChange}</LocalChange>\n'
        self.data6 = f'\t<LastUpdate>{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}</LastUpdate>\n'
        self.data7 = f'\t<Code>{code}</Code>\n'
        self.data8 = f'\t<CodeLat>{code_lat}</CodeLat>\n' if code_lat != "" else '\t\t<CodeLat> />\n'
        self.data9 = f'\t<Name>{name}</Name>\n'
        self.data10 = f'\t<NameLat>{name_lat}</NameLat>\n' if name_lat != "" else '\t\t<NameLat />\n'
        self.data11 = '\t<Names />\n'
        self.data12 = '\t<NamesXml />\n'
        self.data13 = '\t<Comment />\n'
        self.data14 = '\t<BeginDate>0001-01-01T00:00:00</BeginDate>\n'
        self.data15 = '\t<EndDate>0001-01-01T00:00:00</EndDate>\n'
        self.data16 = '\t<ShowOnChart>true</ShowOnChart>\n'
        self.data17 = f'\t<Latitude>{lat}</Latitude>\n'
        self.data18 = f'\t<Longitude>{lon}</Longitude>\n'
        self.data19 = '\t<Elevation>0</Elevation>\n'
        self.data20 = f'\t<MagneticDeclination>{magnetic}</MagneticDeclination>\n'
        self.data21 = '\t<Frequencies />\n'
        self.data22 = f'\t<Type>{type_}</Type>\n'
        self.data24 = f'\t<IsACP>{IsACP}</IsACP>\n'
        self.data25 = f'\t<IsInOut>{IsInOut}</IsInOut>\n'
        self.data26 = f'\t<IsInOutCIS>{IsInOutCIS}</IsInOutCIS>\n'
        self.data27 = f'\t<IsGateWay>{IsGateWay}</IsGateWay>\n'
        self.data28 = f'\t<IsTransferPoint>{IsTransferPoint}</IsTransferPoint>\n'
        self.data29 = f'\t<IsTransferPoint_ACP>{IsTransferPoint_ACP}</IsTransferPoint_ACP>\n'
        self.data33 = f'\t<IsInAirway>{IsInAirway}</IsInAirway>\n'
        self.data34 = f'\t<IsMvl>{IsMvl}</IsMvl>\n'
        self.data38 = f'\t<AirportType>{airport_type}</AirportType>\n'
        self.data39 = f'\t<AirportUsageType>{AirportUsageType}</AirportUsageType>\n'
        self.data40 = f'\t<AirportOwnerType>{AirportOwnerType}</AirportOwnerType>\n'
        self.data41 = f'\t<Class>{class_}</Class>\n'
        self.data42 = '\t<AftnAddr />\n'
        self.data43 = f'\t<CallLetter>{CallLetter}</CallLetter>\n' if CallLetter != "" else '\t<CallLetter />\n'
        self.data44 = '\t<WorkingTimeRange IsCancelled="false" minlevel="M/M=0/FL=0/FWD" maxlevel="M/M=16100/FL=528/FWD">\n'
        self.data45 = '\t\t<ObjectId>0</ObjectId>\n'
        self.data46 = '\t\t<Id>0</Id>\n'
        self.data47 = '\t\t<IntervalOfClosing>false</IntervalOfClosing>\n'
        self.data48 = '\t\t<Reserv>false</Reserv>\n'
        self.data49 = '\t\t<Kind>Always</Kind>\n'
        self.data50 = '\t\t<Begin>2020-12-03T00:00:00Z</Begin>\n'
        self.data51 = '\t\t<End>2021-01-03T00:00:00Z</End>\n'
        self.data52 = '\t\t<TimeSpanRanges />\n'
        self.data53 = '\t\t<Comment />\n'
        self.data54 = '\t\t<Sources />\n'
        self.data55 = '\t</WorkingTimeRange>\n'
        self.data56 = '\t<Runways />\n'
        self.data57 = '</MapPoint>'

    def change_ID(self):
        self.id = self.lst[14]
        self.ObjectId = self.lst[15]
        self.data3 = f'\t<ObjectId>{self.ObjectId}</ObjectId>\n'
        self.data4 = f'\t<Id>{self.id}</Id>\n'
        self.data_list = [self.data0, self.data2, self.data3, self.data4, self.data5, self.data6,
                          self.data7, self.data8, self.data9, self.data10, self.data11, self.data12,
                          self.data13,self.data14, self.data15, self.data16, self.data17, self.data18,
                          self.data19, self.data20, self.data21, self.data22, self.data24, self.data25,
                          self.data26, self.data27, self.data28, self.data29, self.data33, self.data34,
                          self.data38, self.data39, self.data40, self.data41, self.data42, self.data43,
                          self.data44, self.data45, self.data46, self.data47, self.data48, self.data49,
                          self.data50, self.data51, self.data52, self.data53, self.data54, self.data55,
                          self.data56, self.data57]
        return self.data_list

    def simple_list(self):
        self.data_list = [self.data0, self.data2, self.data3, self.data4, self.data5, self.data6, self.data7,
                          self.data8, self.data9, self.data10, self.data11, self.data12, self.data13, self.data14,
                          self.data15, self.data16, self.data17, self.data18, self.data19, self.data20, self.data21,
                          self.data22, self.data24, self.data25, self.data26, self.data27, self.data28, self.data29,
                          self.data33, self.data34, self.data38, self.data39, self.data40, self.data41, self.data42,
                          self.data43, self.data44, self.data45, self.data46, self.data47, self.data48, self.data49,
                          self.data50, self.data51, self.data52, self.data53, self.data54, self.data55, self.data56,
                          self.data57]
        return self.data_list


result_new = []
for num, item in enumerate(new_arinc_points):
    real_num = num + 1
    point = FillXML(real_num, real_num, item[0], item[1], item[2])
    point_xml = point.make_list()
    result_new.append(point_xml)

length = len(result_new)

result_old = {}
count = length
for num, item in enumerate(final_old):
    real_num = num + length
    if item[14] in delete_id:
        point = FamiliarNames(item, real_num)
        point_xml = point.change_ID()
        new_value = {point.id: [point_xml, 1 if item[0] is None else int(item[0]) + 1]}
        result_old.update(new_value)
    # else:
    #     point = FamiliarNames(item, real_num)
    #     point_xml = point.simple_list()
    #     new_value = {real_num: [point_xml, 1 if item[0] is None else int(item[0]) + 1]}
    #     result_old.update(new_value)

result = result_new

with open('result.xml', 'w', encoding='utf-8') as output:
    output.write('\ufeff<?xml version="1.0" encoding="utf-16"?>\n')
    output.write(
        '<ArrayOfMapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n')
    for point in result:
        for item in point:
            output.write(item)
    output.write('</ArrayOfMapPoint>')

begin_query = "INSERT INTO `tbl_guides` (`guides_id`, `code`, `is_backup`, `user`, `xml_value`, `isdeleted`, `version`, `arm_name`) VALUES "
lst_values = []

for key, value in result_old.items():
    with open('draft.xml', 'w', encoding='utf-8') as draft:
        for item in result_old[key][0]:
            for param in item:
                draft.write(param)
    with open('draft.xml', 'r', encoding='utf-8') as draft_read:
        xml = draft_read.read()
        new_value = """(%s, 'MapPoint', '0', 'admin', '%s', '0', '%s', 'second') """ % (key, xml, result_old[key][1])
        lst_values.append(new_value)

body_query = ',\n'.join(lst_values)
full_query = begin_query + body_query + ';'

with open('query_old.sql', 'w', encoding='cp1251') as sql:
    sql.write(full_query)


res = ',\n'.join(delete_id)
del_query = f"DELETE FROM tbl_guides WHERE guides_id IN ({res});"
with open('delete_query.sql', 'w', encoding='cp1251') as sql:
    sql.write(del_query)