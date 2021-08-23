import datetime
import transliterate
import modules
from sys import argv

text = open('/home/polina/PycharmProjects/MULTI_ARINC/ARINC and dump/GKOVD_DV2108Bv15.txt', 'r', encoding='utf-8').readlines()
all_points = list(modules.get_points(text))
points = list(modules.get_data(all_points))
points = list(modules.unique(points))
inside_points = list(modules.inside(points))
rad_points = list(modules.gradus(inside_points))


with open('Points.xml', 'r', encoding='utf-8') as file:
    data = file.readlines()


class FillXML:

    def __init__(self, object_id, id, name, lat, lon):
        self.object_id = object_id
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        #self.data0 = '\ufeff<?xml version="1.0" encoding="utf-16"?>\n'
        #self.data1 = '<ArrayOfMapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n'
        self.data2 = '\t<MapPoint Version="3" IsDeleted="false">\n'
        self.data3 = '\t\t<ObjectId>%s</ObjectId>\n' % self.object_id
        self.data4 = '\t\t<Id>%s</Id>\n' % self.id
        self.data5 = '\t\t<LocalChange>true</LocalChange>\n'
        self.data6 = '\t\t<LastUpdate>%s</LastUpdate>\n' % datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.data7 = '\t\t<Code>%s</Code>\n' % transliterate.translit(self.name, 'ru')
        self.data8 = '\t\t<CodeLat>%s</CodeLat>\n' % self.name
        self.data9 = '\t\t<Name>%s</Name>\n' % transliterate.translit(self.name, 'ru')
        self.data10 = '\t\t<NameLat>%s</NameLat>\n' % self.name
        self.data11 = '\t\t<Names />\n'
        self.data12 = '\t\t<NamesXml />\n'
        self.data13 = '\t\t<Comment />\n'
        self.data14 = '\t\t<BeginDate>0001-01-01T00:00:00</BeginDate>\n'
        self.data15 = '\t\t<EndDate>0001-01-01T00:00:00</EndDate>\n'
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
                          self.data21, self.data22, self.data23, self.data24, self.data25,self.data26, self.data27,
                          self.data28, self.data29, self.data30, self.data31, self.data32, self.data33, self.data34,
                          self.data35, self.data36, self.data37, self.data38, self.data39, self.data40, self.data41,
                          self.data41, self.data42, self.data43, self.data44, self.data45, self.data46, self.data47,
                          self.data48, self.data49, self.data50, self.data51, self.data52, self.data53, self.data54,
                          self.data55, self.data56, self.data57]
        return self.data_list

result = []

for num, item in enumerate(rad_points):
    real_num = num + 1
    point = FillXML(real_num, real_num, item[0], item[1], item[2])
    point_xml = point.make_list()
    result.append(point_xml)

with open('result.xml', 'w') as output:
    output.write('\ufeff<?xml version="1.0" encoding="utf-16"?>\n')
    output.write('<ArrayOfMapPoint xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">\n')
    for point in result:
        for item in point:
            output.write(item)
    output.write('</ArrayOfMapPoint>')
