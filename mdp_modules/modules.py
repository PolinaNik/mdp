import re
import math

import transliterate
from shapely.geometry import Point
from itertools import groupby
from mdp_modules import poly_settings


# Поиск всех точек в файле ARINC
def get_points(list):
    for i in range(len(list)):
        line = list[i]
        pat1 = re.compile(r'^(SEEUP ).+')
        pat2 = re.compile(r'^(TEEUD).+')
        pat3 = re.compile(r'^(SPACP ).+')
        pat4 = re.compile(r'^(SEEUU).+')
        pat5 = re.compile(r'^(SEEUP).+')
        pat6 = re.compile(r'^(SEEUP UH).+')
        pat7 = re.compile(r'(?=[^0-9]{5})(?:.+)')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        s4 = pat4.search(line)
        s5 = pat5.search(line)
        s6 = pat6.search(line)
        name = line[13:18]
        s7 = pat7.search(name)
        if len(line) >= 41:
            if line[32] == 'N' and line[41] == 'E' and not s1 \
                    and not s2 and not s3 and not s4 and not s5:
                yield line
            if line[32] == 'N' and line[41] == 'E' and s6 and s7:
                pat8 = re.compile(r'\s|\S+')
                s8 = pat8.search(name)
                point = s8.group()
                if len(point) == 5:
                    yield line


"""Выбор только имени и коррдинаты точки, за исключением точки с координатами Хабаровска 
(это нужно для исключения дальнейших ошибок при рассчетах)"""


def get_data(file):
    for i in range(len(file)):
        line = file[i]
        name = line[13:18]
        coord = line[32:51]
        N = line[32]
        E = line[41]
        pat = re.compile(r'\s|\S+')
        s = pat.search(name)
        ind = line[19:21]
        pat2 = re.compile(r'[0-9]+')
        s2 = pat2.search(name)
        if s and N == 'N' and E == 'E' and coord != 'N48314100E135111700' and not s2:
            point = s.group()
            if len(point) > 1:
                yield point, coord, ind


# Получение координат точек для дальнешего сравнения с базой
def data(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        lat = line[1][5:7]
        lon = line[1][15:17]
        yield name, lat, lon


# Полигон для Синтеза
poly = poly_settings.poly_sintez


# Сравнение точек из файла ARINC с зоной полигона для СИНТЕЗА
def inside(points):
    for i in range(len(points)):
        line = points[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600
        lat = lat * math.pi / 180
        lon = lon * math.pi / 180
        p = Point(lat, lon)
        if poly.contains(p):
            yield line


# Получение имен точек
def names(points):
    for i in range(len(points)):
        line = points[i]
        name = line[0]
        yield name


# Выбираем только уникальные названия
def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    for x in unique_list:
        yield x


# Пересчитываем градусы в радианы
def radians(list1):
    for i in range(len(list1)):
        line = list1[i]
        gr_lat = int(line[1][1:3])
        min_lat = int(line[1][3:5])
        sec_lat = int(line[1][5:7])
        mili_lat = int(line[1][7:9])
        lat = gr_lat + min_lat / 60 + sec_lat / 3600 + mili_lat / 216000
        gr_lon = int(line[1][10:13])
        min_lon = int(line[1][13:15])
        sec_lon = int(line[1][15:17])
        mili_lon = int(line[1][17:19])
        lon = gr_lon + min_lon / 60 + sec_lon / 3600 + mili_lon / 216000
        yield line[0], lat, lon


# Нахождение трасс в документе ARINC
def get_routes(file):
    for i in range(len(file)):
        line = file[i]
        pat1 = re.compile(r'^(SEEUER ).+')
        pat2 = re.compile(r'^(SPACER ).+')
        pat3 = re.compile(r'^(SCANER ).+')
        s1 = pat1.search(line)
        s2 = pat2.search(line)
        s3 = pat3.search(line)
        if s1:
            points = s1.group()
            yield points
        if s2:
            points = s2.group()
            yield points
        if s3:
            points = s3.group()
            yield points


def get_route_info(list1_r):
    for i in range(len(list1_r)):
        line = list1_r[i]
        name = line[13:18]
        point = line[29:34]
        number = int(line[26:28])
        pat = re.compile(r'[^\s]+')
        s = pat.search(name)
        s2 = pat.search(point)
        name = s.group()
        point = s2.group()
        ind = line[34:36]
        min = line[83:88]
        max = line[93:98]
        yield name, point, ind, number, min, max


# Получаем список с трассами, которые лежат в зоне ответсвенности из ARINC
def select_routes(routes, inside_points):
    for i in range(len(routes)):
        line = routes[i]
        route = line[0]
        point = line[1]
        ind = line[2]
        for q in range(len(inside_points)):
            line2 = inside_points[q]
            point2 = line2[0]
            ind2 = line2[2]
            coord = line2[1]
            if point == point2 and ind == ind2:
                yield route, point, ind, coord, line[3], line[4], line[5]


# Считаем трассы, где точек больше двух
def count_list(list1):
    for i in range(len(list1)):
        line = list1[i]
        len1 = len(line)
        if len1 > 1:
            yield line


def counter_of_points(routes):
    for key, group in groupby(routes, lambda x: x[0]):
        for i, each in enumerate(group, start=1):
            yield "{}".format(key), "{}".format(each[1]), "{}".format(each[2]), "{}".format(i), "{}".format(
                each[3]), "{}".format(each[5]), "{}".format(each[6]), "{}".format(each[4])



# Формируем слой с точками, которые участвуют в трассах (ничего лишнего)
def only_in_trass(more):
    only_in_trass_points = []
    for x in more:
        new = []
        new.append(x[1])
        new.append(x[4])
        new.append(x[2])
        new = tuple(new)
        only_in_trass_points.append(new)
    return only_in_trass_points


# Пересчитываем градусы в радианы
def gradus(list1):
    for i in range(len(list1)):
        line = list1[i]
        cord = f'{line[1][1:7]}С{line[1][10:17]}В'
        yield line[0], cord


def transform(lat, lon):
    f_gr = math.trunc(lat)
    l_gr = math.trunc(lon)
    f_min = math.trunc((lat - f_gr) * 60)
    l_min = math.trunc((lon - l_gr) * 60)
    f_sec = math.ceil(((lat - f_gr) * 60 - f_min) * 60)
    l_sec = math.ceil(((lon - l_gr) * 60 - l_min) * 60)
    result = str(f_gr) + str(f_min) + str(f_sec) + 'С' + str(l_gr) + str(l_min) + str(l_sec) + 'В'
    return result


def insert_arinc(lst):
    name = lst[0]
    coord = lst[1]
    new_lst = ['PDZ', transliterate.translit(name, 'ru'), name,
               transliterate.translit(name, 'ru'), name, coord, 0]
    return new_lst


def insert_old(lst):
    type = lst[6]
    code = lst[1]
    code_lat = transliterate.translit(lst[1], 'ru', reversed=True) if lst[2] is None else lst[2]
    name = lst[1] if lst[3] is None else lst[3]
    name_lat = transliterate.translit(lst[1], 'ru', reversed=True) if lst[4] is None else lst[4]
    coord = transform(float(lst[7]), float(lst[8]))
    magdecl = 0 if lst[5] is None else lst[5]
    new_lst = [type, code, code_lat, name, name_lat, coord, magdecl]
    return new_lst


