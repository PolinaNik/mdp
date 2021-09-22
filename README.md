# mdp
Версия python - 3.8

Необходимые пакеты -> requirements.txt

# Установка
1) Скачать репозиторий. В репозитории в папке parsing_files содержится версия ARINC на август 2021 года, дамп таблицы tbl_quides.sql и файл Points.xml. Эти файлы можно заменить.
2) Зайти в папку репозитория, установить необходимые пакеты командой ``` pip -r requirements.txt ```.
3) Скрипт для парсинга и изменения называется mdp_arinc.py. Конфигурационные параметры для соединения с базой данных находятся в config.ini

# Подготовка к запуску скрипта
1) Перед запуском необходимо сформировать дамп таблицы tbl_guides. Дамп этой таблицы необходим для поиска id всех объектов: точек, трасс, ограничений и пр. Это требуется для того, чтобы при формировании новых точек и присваивании им id не возникло конфликта дублирования при добавлении в базу данных.

    Дамп таблицы для поиска всех id парсится с помощью регулярных выражений. Однако, для получения информации о всех точках и параметрах такой способ не удобен, поэтому нужно   сформировать справочник Points.xml.

    Команда для формирования дампа таблицы следующая: ``` mysqldump -proot -uuser aftn_db tbl_guides > /path/to/save/ ```

2) Сформировать справочник Points.xml можно следующим образом:
    а) запустить программу mdp
    б) Файл -> Управление данными -> Управление БД -> Сохранить текущие справочники в XML файлы
    в) выйти из программы

3) Из рабочей директории _Debug/Data/Khabarovsk/Map удалить файл Points.xml

# Запуск скрипта
 Скрипт называется mdp_arinc.py
 
 
 Выполняется командой ``` python3 mdp_arinc.py ```
 
 Скрипт полностью интерактивный, каждый шаг описывается в терминале. Пути до файлов (arinc.txt, Points.xml, tbl_guides.sql) запросятся самим скриптом 
 и пользователю придется их ввести. Для выполненя запроса на удаление точек и добавление новых в базу данных необходимо разрешение пользователя.
 
 Если разрешение не получено - создается запрос new_query.sql в папке с программой. Для выполнения вручную нужно сделать 2 шага:
 1) ``` mysql -uroot -puser -e "DELETE FROM tbl_guides WHERE code='MapPoint';" aftn_db ```
 2) ``` mysql -uroot -puser aftn_db < new_query.sql ```
