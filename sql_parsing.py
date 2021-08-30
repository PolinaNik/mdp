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