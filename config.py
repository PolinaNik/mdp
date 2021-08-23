"""Конфигурационный файл"""

import math
from shapely.geometry import Point
from shapely import geometry
import numpy as np
import geog

#################################################################################################################
"""Настройки разбора картографии для СИНТЕЗА"""

# Минимальное расстояние между точками, на котором ставятся десигнаторы (в метрах)
d = 20000

# Трассы по согласованию
routes = {'A357', 'A492', 'A822', 'A823', 'A938', 'B124', 'B201',
          'B215', 'B478', 'B913', 'B914', 'B916', 'A900', 'W209',
          'W211', 'W212', 'W292', 'W293', 'W295', 'W307', 'W907'}

# Точки ПОД и ПДЗ
pod = {'ABAGO', 'ABERA', 'ABOMA', 'ABREP', 'ADITO', 'ADLAT',
       'ADNUR', 'AGEMO', 'AGUBI', 'AKOBI', 'AKSUN', 'ALAKA',
       'ALEPA', 'ALETI', 'AMUPI', 'ANAGO', 'ANIMO', 'APTIL',
       'ARDOK', 'ARDUL', 'ARELI', 'ARGOV', 'ARGUK', 'ARLAS',
       'ASKIB', 'ASNEN', 'AVGOK', 'BAGES', 'BAGOM', 'BAGUN',
       'BALET', 'BAMOT', 'BAPMA', 'BAPRI', 'BARIB', 'BASAT',
       'BASOK', 'BATUD', 'BEDNA', 'BELNA', 'BIKUR', 'BISIV',
       'BISUN', 'BOKNA', 'BUDES', 'BUMAD', 'BUMEN', 'BUMEP',
       'BURAP', 'DABUR', 'DAGES', 'DASKO', 'DIDEK', 'DIMED',
       'DIREB', 'DIVIL', 'DOLMA', 'DOSET', 'EMGOL', 'GALDI',
       'GIGAT', 'GIGRO', 'GIKOS', 'GIPAL', 'GIPUR', 'GIRAN',
       'GIRUD', 'GITMI', 'GODIK', 'GRUMA', 'GUGLA', 'IDELI',
       'IDMON', 'IDRUT', 'IGROD', 'INLIR', 'INSEM', 'ITVIS',
       'IVADA', 'KELUL', 'KENOM', 'KERET', 'KESAN', 'KOMEG',
       'KORES', 'KUMAP', 'KUNON', 'KUPER', 'KURIN', 'KUROP',
       'LALIR', 'LAMKA', 'LANRI', 'LASUP', 'LAVNI', 'LEBTA',
       'LEDIS', 'LEGRU', 'LEKBI', 'LEKMA', 'LEKPA', 'LISOL',
       'LITLU', 'LUBOK', 'LUKUT', 'LUMIN', 'LUNIB', 'LUPAS',
       'LUREP', 'LUSAK', 'MADAN', 'MAGIT', 'MAKIS', 'MARAN',
       'MASET', 'MAVUN', 'MOGIS', 'MOKSI', 'MOKUR', 'NABUK',
       'NALAM', 'NAMUK', 'NAROG', 'NASOD', 'NATOM', 'NEBES',
       'NEBUL', 'NELAD', 'NELAG', 'NELER', 'NETRI', 'NIDIS',
       'NIKTO', 'NIKTU', 'NILOT', 'NIMOR', 'NITIN', 'NODRO',
       'NOPSO', 'NUKSI', 'NULAR', 'NURBA', 'OBERI', 'ODEKO',
       'ODERI', 'OGMUS', 'OGROL', 'OGUMI', 'OKBER', 'OKILI',
       'OKRIG', 'OLGIR', 'OLMAK', 'OLMIS', 'OLUTA', 'OMARU',
       'OMOKA', 'OMONI', 'ORSUK', 'ORTEP', 'OSGEN', 'OSPIR',
       'OTLER', 'OTLIK', 'PELON', 'PELOT', 'PERAS', 'PEROD',
       'PERUB', 'PESOM', 'PIMAG', 'PIMUL', 'PINAK', 'PIRAL',
       'PIREM', 'RALOD', 'RANOL', 'RATOP', 'REGTA', 'REPIK',
       'RESDA', 'RIBMA', 'RIKMA', 'RILOP', 'RILTA', 'RIPLO',
       'RITEK', 'RIVAT', 'ROMEM', 'ROMUK', 'ROSNA', 'RUKOM',
       'RULAS', 'RUNUK', 'RUPON', 'SANAR', 'SARET', 'SEGUL',
       'SEGUN', 'SELDA', 'SIBIR', 'SIMLI', 'SM', 'SOLIK',
       'SOMUR', 'SONUK', 'SOROD', 'SOVIK', 'SURAN', 'SUROK',
       'SUTEK', 'TADIV', 'TAKAD', 'TEMRA', 'TERNU', 'TIFON',
       'TIGMA', 'TIMIT', 'TIRAK', 'TIRBI', 'TITOL', 'TOMSU',
       'TONPI', 'TOZAR', 'TUNET', 'TUNUN', 'TUSIP', 'UBOKA',
       'UDRIL', 'UGLIS', 'ULGOR', 'ULTAM', 'ULTUR', 'UMGUS',
       'UMKIN', 'UMOLA', 'UMRAK', 'UNELA', 'UREBI', 'URUSA',
       'UTAGI', 'UTOMI', 'VADOK', 'VASIN', 'VATIS'}

pdz = {'ABKEN', 'ABLAM', 'ABNAK', 'ABORI', 'ABSED', 'ADKOT',
       'ADLEP', 'AGAPO', 'AGBIS', 'AGIDU', 'AGITA', 'AGOSU',
       'AGUKA', 'AGUNI', 'AKOLA', 'ALODI', 'AMBAR', 'AMERA',
       'AMKUD', 'ANGAR', 'ARAGE', 'ARDEL', 'ARNUP', 'ASMER',
       'ASNEM', 'BABID', 'BADAG', 'BADNA', 'BADOM', 'BAGDU',
       'BAKAT', 'BAKUM', 'BANAS', 'BANIR', 'BANOP', 'BAPRU',
       'BARUL', 'BASNI', 'BEBAT', 'BEBLI', 'BEKES', 'BEKSA',
       'BELAK', 'BELIM', 'BEMOR', 'BEMUS', 'BENAN', 'BENOK',
       'BEPEL', 'BERER', 'BESPA', 'BIRBO', 'BIRLU', 'BULOD',
       'BURKA', 'BURUK', 'DEFOR', 'DELIP', 'DELUK', 'DENEM',
       'DEPAS', 'DEPOR', 'DERIG', 'DIBOS', 'DILAD', 'DILUN',
       'DIRUL', 'DISOP', 'DISPU', 'DITOR', 'DITSA', 'DOKIR',
       'DOLET', 'DOMON', 'DONIS', 'DOTAK', 'ELNAS', 'ERGER',
       'ERMIS', 'ERONO', 'GEMRA', 'GIGOR', 'GILEB', 'GIMES',
       'GINOL', 'GIRAM', 'GISEL', 'GITAK', 'GITEN', 'GOGNI',
       'GOMUN', 'GORAR', 'GUBIS', 'GUBOL', 'GUDLI', 'GUDMA',
       'GUDNA', 'IBOLI', 'IBOMA', 'IDBUR', 'IDIGA', 'IDREM',
       'IGODA', 'IKADA', 'INBOR', 'INPID', 'INRIL', 'IPREL',
       'IPSON', 'IRLAK', 'KALMI', 'KEGES', 'KENER', 'KERAG',
       'KESIK', 'KESUL', 'KILMI', 'KIZON', 'KODEN', 'KUKEL',
       'KULAL', 'KUNAB', 'LADES', 'LAKIN', 'LAKTA', 'LALET',
       'LAPNI', 'LASNI', 'LASTA', 'LATAK', 'LATMA', 'LEPRO',
       'LIGDA', 'LIKON', 'LIMKU', 'LIRSA', 'LUKAM', 'LUMEK',
       'LUNED', 'LUPAT', 'LURED', 'LUROM', 'LURUN', 'LUTEL',
       'LUTUN', 'MABUT', 'MAGOR', 'MANIT', 'MANOD', 'MATEN',
       'MATUK', 'MEGEP', 'MILFA', 'MIZAL', 'MOKET', 'MOLUT',
       'MOMES', 'MORAB', 'MOROG', 'MOSOL', 'MUFTA', 'NALEB',
       'NAMUL', 'NASAN', 'NATUN', 'NEBAR', 'NEBIM', 'NEBKA',
       'NEDAL', 'NEGOD', 'NEKUT', 'NELAG', 'NENUR', 'NERLI',
       'NESAD', 'NIBRI', 'NIBUL', 'NIKRA', 'NIKRI', 'NILOM',
       'NIMEN', 'NIMLI', 'NINON', 'NIPIN', 'NIROT', 'NOKDA',
       'NOSTI', 'NOTLU', 'OBENA', 'OBUTA', 'ODEKA', 'ODENA',
       'ODEPI', 'ODIBA', 'ODONA', 'ODONI', 'OGIBA', 'OGNIT',
       'OGULA', 'OKNAR', 'OKSOD', 'OLAMA', 'OLDAN', 'OLEGO',
       'OLEPU', 'OLGEN', 'OMAVI', 'OMIGU', 'OSBET', 'OTMIR',
       'OTRUN', 'PABSI', 'PAKLI', 'PAREN', 'PARIS', 'PEMUK',
       'PENOK', 'PERID', 'PESEB', 'PIGUB', 'PIKUS', 'PUMNA',
       'RATNU', 'REBKA', 'REDGA', 'REDNA', 'RELPI', 'RENSI',
       'REZOK', 'RIDLO', 'RIDNO', 'RIGIM', 'RIMEG', 'RIPAG',
       'ROPMI', 'ROTNI', 'RUDOS', 'RUGIM', 'RUNET', 'RUSOT',
       'RUTAL', 'SIRVU', 'SOKMU', 'SOLNI', 'SONAB', 'SONAG',
       'SONID', 'SOPIN', 'SOPON', 'SORED', 'SOROG', 'SORUS',
       'SOTEL', 'SOTIR', 'SUBEK', 'SUKOP', 'SUMOG', 'TAKOB',
       'TEBSA', 'TEKMO', 'TELGI', 'TENLA', 'TERBO', 'TERNI',
       'TIRIS', 'TISUL', 'TODTE', 'TORMA', 'TOTRU', 'TUKAN',
       'TUPEK', 'TUPNA', 'TUTIB', 'UBADA', 'UDELU', 'ULMIK',
       'UNAMO', 'UPODA', 'URETA', 'URIMA', 'UTOGA', 'VANUL',
       'VELTA', 'VIBIR', 'VITIM', 'WZ'}

# Создание полигона с зоной ответственности для SINTEZ
ROMES_lat = math.radians(52 + 25 / 60 + 41 / 3600)
ROMES_lon = math.radians(113 + 53 / 60 + 29 / 3600)

ROGOR_lat = math.radians(57 + 43 / 60 + 6 / 3600)
ROGOR_lon = math.radians(115 + 1 / 60 + 32 / 3600)

KONUD_lat = math.radians(59 + 17 / 60 + 56 / 3600)
KONUD_lon = math.radians(123 + 35 / 60 + 51 / 3600)

RODOK_lat = math.radians(66 + 33 / 60 + 44 / 3600)
RODOK_lon = math.radians(137 + 10 / 60 + 13 / 3600)

TURAN_lat = math.radians(65 + 43 / 60 + 49 / 3600)
TURAN_lon = math.radians(150 + 46 / 60 + 21 / 3600)

LANSA_lat = math.radians(62 + 15 / 60 + 7 / 3600)
LANSA_lon = math.radians(157 + 32 / 60 + 8 / 3600)

OGEMA_lat = math.radians(62 + 25 / 60)
OGEMA_lon = math.radians(166 + 6 / 60 + 9 / 3600)

MURTA_lat = math.radians(56 + 22 / 60 + 9 / 3600)
MURTA_lon = math.radians(163 + 43 / 60 + 11 / 3600)

OGDEN_lat = math.radians(49 + 29 / 60 + 12 / 3600 + 90 / 216000)
OGDEN_lon = math.radians(161 + 2 / 60 + 15 / 3600 + 50 / 216000)

CUTEE_lat = math.radians(46 + 24 / 60 + 54 / 3600)
CUTEE_lon = math.radians(162 + 18 / 60 + 36 / 3600)

KALIG_lat = math.radians(42 + 58 / 60 + 53 / 3600 + 89 / 216000)
KALIG_lon = math.radians(155 + 40 / 60 + 8 / 3600 + 40 / 216000)

KALNA_lat = math.radians(39 + 9 / 60 + 13 / 3600 + 81 / 216000)
KALNA_lon = math.radians(149 + 49 / 60 + 31 / 3600 + 81 / 216000)

NANAC_lat = math.radians(38 + 54 / 60 + 22 / 3600 + 71 / 216000)
NANAC_lon = math.radians(143 + 13 / 60 + 40 / 3600 + 77 / 216000)

USUBA_lat = math.radians(38 + 32 / 60 + 14 / 3600 + 2 / 216000)
USUBA_lon = math.radians(140 + 9 / 60 + 44 / 3600 + 88 / 216000)

BASIN_lat = math.radians(38 + 7 / 60 + 15 / 3600 + 60 / 216000)
BASIN_lon = math.radians(138 + 56 / 60 + 31 / 3600 + 32 / 216000)

TATAM_lat = math.radians(37 + 55 / 60 + 50 / 3600 + 34 / 216000)
TATAM_lon = math.radians(138 + 6 / 60 + 13 / 3600 + 14 / 216000)

KAMSA_lat = math.radians(37 + 43 / 60 + 4 / 3600 + 88 / 216000)
KAMSA_lon = math.radians(133 + 44 / 60 + 1 / 3600 + 52 / 216000)

TENAS_lat = math.radians(37 + 38 / 60 + 20 / 3600)
TENAS_lon = math.radians(131 + 34 / 60 + 27 / 3600)

HAMUN_lat = math.radians(39 + 55 / 60 + 18 / 3600)
HAMUN_lon = math.radians(127 + 31 / 60 + 6 / 3600)

OTABO_lat = math.radians(44 + 27 / 60 + 15 / 3600)
OTABO_lon = math.radians(123 + 54 / 60 + 54 / 3600)

ABVAX_lat = math.radians(47 + 27 / 60 + 36 / 3600)
ABVAX_lon = math.radians(120 + 35 / 60 + 21 / 3600)

ROMES = Point(ROMES_lat, ROMES_lon)
ROGOR = Point(ROGOR_lat, ROGOR_lon)
KONUD = Point(KONUD_lat, KONUD_lon)
RODOK = Point(RODOK_lat, RODOK_lon)
TURAN = Point(TURAN_lat, TURAN_lon)
LANSA = Point(LANSA_lat, LANSA_lon)
OGEMA = Point(OGEMA_lat, OGEMA_lon)
MURTA = Point(MURTA_lat, MURTA_lon)
OGDEN = Point(OGDEN_lat, OGDEN_lon)
CUTEE = Point(CUTEE_lat, CUTEE_lon)
KALIG = Point(KALIG_lat, KALIG_lon)
KALNA = Point(KALNA_lat, KALNA_lon)
NANAC = Point(NANAC_lat, NANAC_lon)
USUBA = Point(USUBA_lat, USUBA_lon)
BASIN = Point(BASIN_lat, BASIN_lon)
TATAM = Point(TATAM_lat, TATAM_lon)
KAMSA = Point(KAMSA_lat, KAMSA_lon)
TENAS = Point(TENAS_lat, TENAS_lon)
HAMUN = Point(HAMUN_lat, HAMUN_lon)
OTABO = Point(OTABO_lat, OTABO_lon)
ABVAX = Point(ABVAX_lat, ABVAX_lon)

pointlist = [ROMES, ROGOR, KONUD, RODOK, TURAN, LANSA,
             OGEMA, MURTA, OGDEN, CUTEE, KALIG, KALNA,
             NANAC, USUBA, BASIN, TATAM, KAMSA, TENAS,
             HAMUN, OTABO, ABVAX, ROMES]

poly_sintez = geometry.Polygon([[p.x, p.y] for p in pointlist])

###################################################################################################
"""Настройки разбора картографии для локатора"""

# Выбор радиуса окружности полигона в метрах
radius = 500000

# Координаты цента в точке HAB
HAB_lat = 48 + 31 / 60 + 41 / 3600
HAB_lon = 135 + 11 / 60 + 17 / 3600

p = geometry.Point([HAB_lon, HAB_lat])
n_points = 20
angles = np.linspace(0, 360, n_points)
polygon_radar = geog.propagate(p, angles, radius)

poly_radar = geometry.Polygon(polygon_radar)

##############################################################################################################################
"""Настройки разбора картографии для КОРИНФ"""
# Создание полигона с зоной ответственности для КОРИНФ
radius_kor = 800000
# Выбор радиуса окружности полигона в метрах
center_lat = 51 + 20 / 60
center_lon = 130

p_kor = geometry.Point([center_lon, center_lat])
n_points_kor = 20
angles_kor = np.linspace(0, 360, n_points_kor)
polygon_kor = geog.propagate(p_kor, angles_kor, radius_kor)

poly_kor = geometry.Polygon(polygon_kor)
