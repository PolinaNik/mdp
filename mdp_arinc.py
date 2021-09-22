"""Скрипт для внесения новых точек из ARINC в базу данных.

    Перед первым запуском нужно выполнить следующие шаги:
    1) Перед запуском необходимо сформировать дамп таблицы tbl_guides.
Дамп базы необходим для поиска всех id, во избежании формирвоания дупликатов при внесении новых точек.
В справочнике Points.xml находятся только id для точек, в то время как в самой таблице, помимо
точек, содержатся трассы, ограничения и прочее (и все содержат свои id).
Команда для формирования дампа таблицы следующая:
mysqldump -proot -uuser aftn_db tbl_guides > /path/to/save/

    2) Сормировать актуальный справочник Points.xml в отдельную папку, которая не используется программой.
И удалить Points.xml из рабочей директории _Debug/Data/Khabarovsk/Map/Points.xml
Для формирования справочника выпольнить следующие шаги:
    а) запустить программу mdp
    б) Файл -> Управление данными -> Управление БД -> Сохранить текущие справочники в XML файлы
    в) выйти из программы

    3) Иметь файл ARINC для МВЛ трасс"""

import xml.etree.ElementTree as ET
import transliterate
import datetime
from mdp_modules import modules
import re
import sys
import pymysql.cursors
import configparser

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("config.ini")  # читаем конфиг

connection = pymysql.connect(host=config['db']['host'],
                             user=config['db']['user'],
                             password=config['db']['password'],
                             database=config['db']['database'],
                             cursorclass=pymysql.cursors.DictCursor)

# Работа с файлами
file_arinc = input('Введите путь до ARINC с МВЛ трассами: ')

try:
    text = open(file_arinc, 'r', encoding='utf-8').readlines()
except:
    print('Неверно указан путь до ARINC с МВЛ трассами')
    sys.exit()

file_points = input('Введите путь до Points.xml: ')

try:
    with open(file_points, 'r', encoding='utf-8') as file:
        data = file.read()
except:
    print('Неверно указан путь до Points.xml')
    sys.exit()

file_guides = input('Введите путь до дампа таблицы tbl_guides.sql: ')

try:
    with open(file_guides, 'r', encoding='utf-8') as file:
        guides = file.read()
except:
    print('Неверно указан путь до дампа таблицы tbl_guides.sql')
    sys.exit()

print('Начало работы скрипта...')
print('Разбор дампа базы с целью нахождения максимального Id и ObjectId')
pat_obj_id = re.compile(r'(?<=\<ObjectId>)\d+(?=\<\/ObjectId>)')
pat_id = re.compile(r'(?<=\<Id>)\d+(?=\<\/Id>)')

all_id = re.findall(pat_id, guides)
all_obj_id = re.findall(pat_obj_id, guides)

# Максимальные id
max_id = max([int(item) for item in all_id])
print(f'Максимальный Id - {max_id}')
max_obj_id = max([int(item) for item in all_obj_id])
print(f'Максимальный ObjectId - {max_obj_id}')

# Начинаем парсить XML файл
print('Разбор XML файла...')
root = ET.fromstring(data)

# Находим ключевые значения, такие как: version, code, codelat, name , namelat, lon, lat, magnetic declination, type
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
    ShowOnChart = try_except(mappoint, 'ShowOnChart')
    Frequencies = try_except(mappoint, 'Frequencies')
    if lat and lon != None:
        lst = [version, code, code_lat, name, nameLat, magnetic, type_, lat, lon, airport_type, AirportUsageType,
               AirportOwnerType, class_, CallLetter, Id, ObjectId, IsACP, IsInOut, IsInOutCIS, IsGateWay,
               IsTransferPoint,
               IsTransferPoint_ACP, IsInAirway, IsMvl, LocalChange, ShowOnChart, Frequencies]
        names.append(lst)

POD_PDZ = []
for x in names:
    if x[6] == "POD" or x[6] == "PDZ":
        if len(x[1]) == 4:
            POD_PDZ.append(x)

# finding all points
print('Разбор ARINC...')
all_points = list(modules.get_points(text))
points = list(modules.get_data(all_points))
points = list(modules.unique(points))

# getting points only inside polygon
inside_points = list(modules.inside(points))

# transform coordinates from gradus to radians
rad_points = list(modules.radians(inside_points))

# getting names of mdp_points from XML file
mdp_points = [item[1] for item in names]

# getting names from arinc file and transliterate them into russian
arinc_points = [transliterate.translit(item[0], 'ru') for item in rad_points]

print('Нахождение общих точек')
# finding common points in mdp and arinc
common_points = [item for item in arinc_points if item in mdp_points]

print('Нахождение точек из Points, которые не совпали c ARINC')
# finding non common points
non_common_points = [item for item in names if
                     item[1] not in arinc_points and len(item[1]) == 5 and (item[6] == 'POD' or item[6] == 'PDZ')]

# Common points with old parameters from XML file
common_points_params = [item for item in names if item[1] in common_points]

print('Присваивание общим точкам новых координат из ARINC')
# Common points with old params and new coordinatse from arinc
common_points_arinc = sorted([item for item in rad_points if transliterate.translit(item[0], 'ru') in common_points])

# Replace with new coordinates from arinc
for x in common_points_arinc:
    for y in common_points_params:
        if transliterate.translit(x[0], 'ru') == y[1]:
            y[7] = x[1]
            y[8] = x[2]

common_points_params_sorted = sorted(common_points_params, key=lambda x: transliterate.translit(x[1], 'ru'))

print('Нахождение новых 5-буквенных точек из ARINC')
new_arinc_points = [item for item in rad_points if
                    transliterate.translit(item[0], 'ru') not in common_points and len(item[0]) == 5]

# Airdromes, GeoPoints, Landing and other types we should save
other_points = [item for item in names if item[1] not in common_points and item[6] != "POD"
                and item[6] != "PDZ"]

first = [('Type', 'Code', 'CodeLat', 'Name', 'NameLat', 'Coord', 'MagDecl'
          , 'Elevation', 'H', 'Habs', 'Comment')]

final_old = common_points_params + other_points + POD_PDZ + non_common_points


class FillXML:

    def __init__(self, id, object_id, name, lat, lon):
        self.object_id = object_id
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.sample = f"""<?xml version="1.0" encoding="utf-16"?>
<MapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Version="1" IsDeleted="false">
    <ObjectId>{self.object_id}</ObjectId>
    <Id>{self.id}</Id>
    <LocalChange>true</LocalChange>
    <LastUpdate>{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}</LastUpdate>
    <Code>{transliterate.translit(self.name, 'ru')}</Code>
    <CodeLat>{self.name}</CodeLat>
    <Name>{transliterate.translit(self.name, 'ru')}</Name>
    <NameLat>{self.name}</NameLat>
    <Names />
    <NamesXml />
    <Comment />
    <BeginDate>0001-01-01T00:00:00</BeginDate>
    <EndDate>0001-01-01T00:00:00</EndDate>
    <ShowOnChart>true</ShowOnChart>
    <Latitude>{self.lat}</Latitude>
    <Longitude>{self.lon}</Longitude>
    <Elevation>0</Elevation>
    <MagneticDeclination>0</MagneticDeclination>
    <Frequencies />
    <Type>PDZ</Type>
    <IsACP>false</IsACP>
    <IsInOut>false</IsInOut>
    <IsInOutCIS>false</IsInOutCIS>
    <IsGateWay>false</IsGateWay>
    <IsTransferPoint>false</IsTransferPoint>
    <IsTransferPoint_ACP>false</IsTransferPoint_ACP>
    <IsInAirway>false</IsInAirway>
    <IsMvl>true</IsMvl>
    <AirportType>Aerodrome</AirportType>
    <AirportUsageType>NotDefined</AirportUsageType>
    <AirportOwnerType>NotDefined</AirportOwnerType>
    <Class>Unknown</Class>
    <AftnAddr />
    <CallLetter />
    <WorkingTimeRange IsCancelled="false" minlevel="M/M=0/FL=0/FWD" maxlevel="M/M=16100/FL=528/FWD">
        <ObjectId>0</ObjectId>
        <Id>0</Id>
        <IntervalOfClosing>false</IntervalOfClosing>
        <Reserv>false</Reserv>
        <Kind>Always</Kind>
        <Begin>2020-12-03T00:00:00Z</Begin>
        <End>2021-01-03T00:00:00Z</End>
        <TimeSpanRanges />
        <Comment />
        <Sources />
        </WorkingTimeRange>
        <Runways />
        </MapPoint>"""

    def new(self):
        return self.sample


class FamiliarNames:

    def __init__(self, lst):
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
        ShowOnChart = lst[25] if lst[25] is not None else 'true'
        Frequencies = lst[26] if lst[26] is not None else ""
        self.data0 = '<?xml version="1.0" encoding="utf-16"?>\n'
        self.data2 = f"""<MapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Version="{version}" IsDeleted="false">\n"""
        self.data3 = f'\t<ObjectId>{new_obj_id}</ObjectId>\n'
        self.data4 = f'\t<Id>{new_id}</Id>\n'
        self.data5 = f'\t<LocalChange>{LocalChange}</LocalChange>\n'
        self.data6 = f'\t<LastUpdate>{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}</LastUpdate>\n'
        self.data7 = f'\t<Code>{code}</Code>\n'
        self.data8 = f'\t<CodeLat>{code_lat}</CodeLat>\n' if code_lat != "" else '\t\t<CodeLat />\n'
        self.data9 = f'\t<Name>{name}</Name>\n'
        self.data10 = f'\t<NameLat>{name_lat}</NameLat>\n' if name_lat != "" else '\t\t<NameLat />\n'
        self.data11 = '\t<Names />\n'
        self.data12 = '\t<NamesXml />\n'
        self.data13 = '\t<Comment />\n'
        self.data14 = '\t<BeginDate>0001-01-01T00:00:00</BeginDate>\n'
        self.data15 = '\t<EndDate>0001-01-01T00:00:00</EndDate>\n'
        self.data16 = f'\t<ShowOnChart>{ShowOnChart}</ShowOnChart>\n'
        self.data17 = f'\t<Latitude>{lat}</Latitude>\n'
        self.data18 = f'\t<Longitude>{lon}</Longitude>\n'
        self.data19 = '\t<Elevation>0</Elevation>\n'
        self.data20 = f'\t<MagneticDeclination>{magnetic}</MagneticDeclination>\n'
        self.data21 = f'\t<Frequencies>{Frequencies}</Frequencies>\n'
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
                          self.data13, self.data14, self.data15, self.data16, self.data17, self.data18,
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


print('Составление списка с новыми точками...')
result_new = {}
for num, item in enumerate(new_arinc_points):
    new_id = num + max_id + 1
    new_obj_id = num + max_obj_id + 1
    point = FillXML(new_id, new_obj_id, item[0], item[1], item[2])
    point_xml = point.new()
    new_value = {new_id: [point_xml, 1]}
    result_new.update(new_value)

print('Составление списка со старыми точками...')
result_old = {}
for num, item in enumerate(final_old):
    if item[14] and item[15] is not None:
        point = FamiliarNames(item)
        point_xml = point.change_ID()
        new_value = {point.id: [point_xml, 1 if item[0] is None else int(item[0]) + 1]}
        result_old.update(new_value)

begin_query = "INSERT INTO `tbl_guides` (`guides_id`, `code`, `is_backup`, `user`, `xml_value`, `isdeleted`, `version`, `arm_name`) VALUES "
lst_values = []

print('Формирование зароса SQL на добавление точек...')
for key, value in result_old.items():
    with open('tmp_files/draft.xml', 'w', encoding='utf-8') as draft:
        for item in result_old[key][0]:
            for param in item:
                draft.write(param)
    with open('tmp_files/draft.xml', 'r', encoding='utf-8') as draft_read:
        xml = draft_read.read()
        new_value = """(%s, 'MapPoint', '0', 'admin', '%s', '0', '%s', 'second') """ % (key, xml, result_old[key][1])
        lst_values.append(new_value)

for key, value in result_new.items():
    with open('tmp_files/draft.xml', 'w', encoding='utf-8') as draft:
        for item in result_new[key][0]:
            for param in item:
                draft.write(param)
    with open('tmp_files/draft.xml', 'r', encoding='utf-8') as draft_read:
        xml = draft_read.read()
        new_value = """(%s, 'MapPoint', '0', 'admin', '%s', '0', '%s', 'second') """ % (key, xml, result_new[key][1])
        lst_values.append(new_value)

body_query = ',\n'.join(lst_values)
full_query = begin_query + body_query + ';'

with open('new_query.sql', 'w', encoding='utf-8') as new_sql:
    new_sql.write(full_query)

print('Запросы в БД new_query.sql сформирован')
permission = input('Удалить точки из базы и добавить новые? Y/N :')

if permission == 'Y':
    with connection:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "DELETE FROM tbl_guides WHERE code='MapPoint'"
            cursor.execute(sql)
            cursor.execute(full_query)
            print('Скрипт завершен. Запросы выполнились.')
else:
    print('Скрипт завершен. Запросы в БД не выполнились.')
