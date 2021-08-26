import xml.etree.ElementTree as ET
from itertools import groupby
from itertools import chain
import transliterate
import datetime
import modules
import xlwt

# Opening existing XML file with points
with open('Points.xml', 'r', encoding='utf-8') as file:
    data = file.read()

# Start parsing of XML file
root = ET.fromstring(data)

# Key values in XML file: version, code, codelat, name , namelat, lon, lat, magnetic declination, type
names = []

for mappoint in root.findall('MapPoint'):
    version = mappoint.get('Version')
    code = mappoint.find('Code').text
    try:
        code_lat = mappoint.find('CodeLat').text
    except:
        code_lat = None
    try:
        name = mappoint.find('Name').text
    except:
        name = None
    try:
        nameLat = mappoint.find('NameLat').text
    except:
        nameLat = None
    try:
        magnetic = mappoint.find('MagneticDeclination').text
    except:
        magnetic = None
    type = mappoint.find('Type').text
    lat = mappoint.find('Latitude').text
    lon = mappoint.find('Longitude').text
    try:
        airport_type = mappoint.find('AirportType').text
    except:
        airport_type = None
    try:
        AirportUsageType = mappoint.find('AirportUsageType').text
    except:
        AirportUsageType = None
    try:
        AirportOwnerType = mappoint.find('AirportOwnerType').text
    except:
        AirportOwnerType = None
    try:
        class_ = mappoint.find('Class').text
    except:
        class_ = None
    try:
        CallLetter = mappoint.find("CallLetter").text
    except:
        CallLetter = None
    try:
        Id = mappoint.find("Id").text
    except:
        Id = None
    ObjectId = mappoint.find("ObjectId").text
    try:
        IsInAirway = mappoint.find("IsInAirway").text
    except:
        IsInAirway = None
    lst = [version, code, code_lat, name, nameLat, magnetic, type, lat, lon, airport_type, AirportUsageType,
           AirportOwnerType, class_, CallLetter, Id, ObjectId, IsInAirway]
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
        # self.data0 = '\ufeff<?xml version="1.0" encoding="utf-16"?>\n'
        # self.data1 = '<ArrayOfMapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
        self.data2 = '\t<MapPoint Version="3" IsDeleted="false">\n'
        self.data3 = '\t\t<ObjectId>%s</ObjectId>\n' % self.object_id
        self.data4 = '\t\t<Id>%s</Id>\n' % self.id
        self.data5 = '\t\t<LocalChange>false</LocalChange>\n'
        self.data6 = '\t\t<LastUpdate>%s</LastUpdate>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data7 = '\t\t<Code>%s</Code>\n' % transliterate.translit(self.name, 'ru')
        self.data8 = '\t\t<CodeLat>%s</CodeLat>\n' % self.name
        self.data9 = '\t\t<Name>%s</Name>\n' % transliterate.translit(self.name, 'ru')
        self.data10 = '\t\t<NameLat>%s</NameLat>\n' % self.name
        self.data11 = '\t\t<Names />\n'
        self.data12 = '\t\t<NamesXml />\n'
        self.data13 = '\t\t<Comment />\n'
        self.data14 = '\t\t<BeginDate>0001-01-01T00:00:00Z</BeginDate>\n'
        self.data15 = '\t\t<EndDate>0001-01-01T00:00:00Z</EndDate>\n'
        self.data16 = '\t\t<ShowOnChart>true</ShowOnChart>\n'
        self.data17 = '\t\t<Latitude>%s</Latitude>\n' % self.lat
        self.data18 = '\t\t<Longitude>%s</Longitude>\n' % self.lon
        self.data19 = '\t\t<Elevation>0</Elevation>\n'
        self.data20 = '\t\t<MagneticDeclination>0</MagneticDeclination>\n'
        self.data21 = '\t\t<Frequencies />\n'
        self.data22 = '\t\t<Type>PDZ</Type>\n'
        self.data23 = '\t\t<SignalCode />\n'
        self.data24 = '\t\t<IsACP>false</IsACP>\n'
        self.data25 = '\t\t<IsInOut>false</IsInOut>\n'
        self.data26 = '\t\t<IsInOutCIS>false</IsInOutCIS>\n'
        self.data27 = '\t\t<IsGateWay>false</IsGateWay>\n'
        self.data28 = '\t\t<IsTransferPoint>false</IsTransferPoint>\n'
        self.data29 = '\t\t<IsTransferPoint_ACP>false</IsTransferPoint_ACP>\n'
        self.data30 = '\t\t<IsInARZ>false</IsInARZ>\n'
        self.data31 = '\t\t<IsOutARZ>false</IsOutARZ>\n'
        self.data32 = '\t\t<IsInRA>false</IsInRA>\n'
        self.data33 = '\t\t<IsInAirway>false</IsInAirway>\n'
        self.data34 = '\t\t<IsMvl>true</IsMvl>\n'
        self.data35 = '\t\t<CorridorNumber />\n'
        self.data36 = '\t\t<Height>0</Height>\n'
        self.data37 = '\t\t<HeightAbs>0</HeightAbs>\n'
        self.data38 = '\t\t<AirportType>Airport</AirportType>\n'
        self.data39 = '\t\t<AirportUsageType>NotDefined</AirportUsageType>\n'
        self.data40 = '\t\t<AirportOwnerType>NotDefined</AirportOwnerType>\n'
        self.data41 = '\t\t<Class>Unknown</Class>\n'
        self.data42 = '\t\t<AftnAddr />\n'
        self.data43 = '\t\t<CallLetter />\n'
        self.data44 = '\t\t<WorkingTimeRange IsCancelled="false" minlevel="M/M=0/FL=0/FWD" maxlevel="M/M=16100/FL=528/FWD">\n'
        self.data45 = '\t\t\t<ObjectId>0</ObjectId>\n'
        self.data46 = '\t\t\t<Id>0</Id>\n'
        self.data47 = '\t\t\t<IntervalOfClosing>false</IntervalOfClosing>\n'
        self.data48 = '\t\t\t<Reserv>false</Reserv>\n'
        self.data49 = '\t\t\t<Kind>Always</Kind>\n'
        self.data50 = '\t\t\t<Begin>%s</Begin>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data51 = '\t\t\t<End>%s</End>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data52 = '\t\t\t<TimeSpanRanges />\n'
        self.data53 = '\t\t\t<Comment />\n'
        self.data54 = '\t\t\t<Sources />\n'
        self.data55 = '\t\t</WorkingTimeRange>\n'
        self.data56 = '\t\t<Runways />\n'
        self.data57 = '\t</MapPoint>\n'

    def make_list(self):
        self.data_list = [self.data2, self.data3, self.data4, self.data5, self.data6,
                          self.data7, self.data8, self.data9, self.data10, self.data11, self.data12, self.data13,
                          self.data14, self.data15, self.data16, self.data17, self.data18, self.data19, self.data20,
                          self.data21, self.data22, self.data23, self.data24, self.data25, self.data26, self.data27,
                          self.data28, self.data29, self.data30, self.data31, self.data32, self.data33, self.data34,
                          self.data35, self.data36, self.data37, self.data38, self.data39, self.data40, self.data41,
                          self.data41, self.data42, self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49, self.data50, self.data51, self.data52, self.data53, self.data54,
                          self.data55, self.data56, self.data57]
        return self.data_list


#lst = [version, code, code_lat, name, nameLat, magnetic, type, lat, lon, airport_type, AirportUsageType,
#           AirportOwnerType, class_, CallLetter, Id, ObjectId, IsInAirway]


class FamiliarNames:

    def __init__(self, lst, num):
        self.lst = lst
        version = lst[0]
        code = lst[1]
        code_lat = transliterate.translit(lst[1], 'ru', reversed=True)
        name = lst[1] if lst[3] is None else lst[3]
        name_lat = transliterate.translit(lst[1], 'ru', reversed=True) if lst[4] is None else ""
        magnetic = 0 if lst[5] is None else lst[5]
        type = "" if lst[6] is None else lst[6]
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
        IsInAirway = 'false' if lst[16] is None or lst[16] == 'false' else 'true'
        self.data0 = '<?xml version="1.0" encoding="utf-16"?>\n'
        self.data2 = """<MapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Version="0" IsDeleted="false">\n"""
        self.data3 = '\t<ObjectId>%s</ObjectId>\n' % num
        self.data4 = '\t<Id>%s</Id>\n' % num
        self.data5 = '\t<LocalChange>false</LocalChange>\n'
        self.data6 = '\t<LastUpdate>%s</LastUpdate>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data7 = '\t<Code>%s</Code>\n' % code
        self.data8 = '\t<CodeLat>%s</CodeLat>\n' % code_lat if code_lat != "" else '\t\t<CodeLat> />\n'
        self.data9 = '\t<Name>%s</Name>\n' % name
        self.data10 = '\t<NameLat>%s</NameLat>\n' % name_lat if name_lat != "" else '\t\t<NameLat />\n'
        self.data11 = '\t<Names />\n'
        self.data12 = '\t<NamesXml />\n'
        self.data13 = '\t<Comment />\n'
        self.data14 = '\t<BeginDate>0001-01-01T00:00:00</BeginDate>\n'
        self.data15 = '\t<EndDate>0001-01-01T00:00:00</EndDate>\n'
        self.data16 = '\t<ShowOnChart>true</ShowOnChart>\n'
        self.data17 = '\t<Latitude>%s</Latitude>\n' % lat
        self.data18 = '\t<Longitude>%s</Longitude>\n' % lon
        self.data19 = '\t<Elevation>0</Elevation>\n'
        self.data20 = '\t<MagneticDeclination>%s</MagneticDeclination>\n' % magnetic
        self.data21 = '\t<Frequencies />\n'
        self.data22 = '\t<Type>%s</Type>\n' % type
        self.data23 = '\t<SignalCode />\n'
        self.data24 = '\t<IsACP>false</IsACP>\n'
        self.data25 = '\t<IsInOut>false</IsInOut>\n'
        self.data26 = '\t<IsInOutCIS>false</IsInOutCIS>\n'
        self.data27 = '\t<IsGateWay>false</IsGateWay>\n'
        self.data28 = '\t<IsTransferPoint>%s</IsTransferPoint>\n' % 'true' if type == 'POD' else 'false'
        self.data29 = '\t<IsTransferPoint_ACP>false</IsTransferPoint_ACP>\n'
        self.data30 = '\t<IsInARZ>false</IsInARZ>\n'
        self.data31 = '\t<IsOutARZ>false</IsOutARZ>\n'
        self.data32 = '\t<IsInRA>false</IsInRA>\n'
        self.data33 = '\t<IsInAirway>%s</IsInAirway>\n' % IsInAirway
        self.data34 = '\t<IsMvl>true</IsMvl>\n'
        self.data35 = '\t<CorridorNumber />\n'
        self.data36 = '\t<Height>0</Height>\n'
        self.data37 = '\t<HeightAbs>0</HeightAbs>\n'
        self.data38 = '\t<AirportType>%s</AirportType>\n' % airport_type
        self.data39 = '\t<AirportUsageType>%s</AirportUsageType>\n' % AirportUsageType
        self.data40 = '\t<AirportOwnerType>%s</AirportOwnerType>\n' % AirportOwnerType
        self.data41 = '\t<Class>%s</Class>\n' % class_
        self.data42 = '\t<AftnAddr />\n'
        self.data43 = '\t<CallLetter>%s</CallLetter>\n' % CallLetter if CallLetter != "" else '\t<CallLetter >/\n'
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
        self.ObjectId = self.lst[15] if self.lst[15] != '0' else ""
        self.data3 = '\t<ObjectId>%s</ObjectId>\n' % self.ObjectId
        self.data4 = '\t<Id>%s</Id>\n' % self.id
        self.data_list = [self.data0, self.data2, self.data3, self.data4, self.data5, self.data6,
                          self.data7, self.data8, self.data9, self.data10, self.data11, self.data12, self.data13,
                          self.data14, self.data15, self.data16, self.data17, self.data18, self.data19, self.data20,
                          self.data21, self.data22, self.data23, self.data24, self.data25, self.data26, self.data27,
                          self.data28, self.data29, self.data30, self.data31, self.data32, self.data33, self.data34,
                          self.data35, self.data36, self.data37, self.data38, self.data39, self.data40, self.data41,
                          self.data42, self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49, self.data50, self.data51, self.data52, self.data53, self.data54,
                          self.data55, self.data56, self.data57]
        return self.data_list

    def make_list(self):
        self.data_list = [self.data2, self.data3, self.data4, self.data5, self.data6,
                          self.data7, self.data8, self.data9, self.data10, self.data11, self.data12, self.data13,
                          self.data14, self.data15, self.data16, self.data17, self.data18, self.data19, self.data20,
                          self.data21, self.data22, self.data23, self.data24, self.data25, self.data26, self.data27,
                          self.data28, self.data29, self.data30, self.data31, self.data32, self.data33, self.data34,
                          self.data35, self.data36, self.data37, self.data38, self.data39, self.data40, self.data41,
                          self.data42, self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49, self.data50, self.data51, self.data52, self.data53, self.data54,
                          self.data55, self.data56, self.data57]
        return self.data_list

    def simple_list(self):
        self.data_list = [self.data0, self.data2, self.data3, self.data4, self.data5, self.data6,
                          self.data7, self.data8, self.data9, self.data10, self.data11, self.data12, self.data13,
                          self.data14, self.data15, self.data16, self.data17, self.data18, self.data19, self.data20,
                          self.data21, self.data22, self.data23, self.data24, self.data25, self.data26, self.data27,
                          self.data28, self.data29, self.data30, self.data31, self.data32, self.data33, self.data34,
                          self.data35, self.data36, self.data37, self.data38, self.data39, self.data40, self.data41,
                          self.data42, self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49, self.data50, self.data51, self.data52, self.data53, self.data54,
                          self.data55, self.data56, self.data57]
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
    if item[14] is not None:
        point = FamiliarNames(item, real_num)
        point_xml = point.change_ID()
        new_value = {point.id: point_xml}
        result_old.update(new_value)
    else:
        point = FamiliarNames(item, real_num)
        point_xml = point.simple_list()
        new_value = {real_num: [point_xml, 1 if item[0] is None else int(item[0])+1]}
        result_old.update(new_value)

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
        for item in value[0]:
            draft.write(item)
    with open('draft.xml', 'r', encoding='utf-8') as draft_read:
        xml = draft_read.read()
    new_value = """(%s, 'MapPoint', '0', 'admin', '%s', '0', '%s', 'second') """ % (key, xml, str(value))
    lst_values.append(new_value)

body_query = ',\n'.join(lst_values)
full_query = begin_query + body_query + ';'

with open('query_old.sql', 'w', encoding='cp1251') as sql:
    sql.write(full_query)
