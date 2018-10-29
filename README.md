Scrapy Booking.com website

*********************************

Настройка и поднятие проекта
 
Требования к программному обеспечению(Windows 10)

Парсер работает для версии python 3.6, далее необходимо установить pipenv: 
pip install pipenv.
Затем зайти в shell: pipenv shell и установить следующее программное обеспечение:
pipenv install pillow pypiwin32 scrapy sqlalchemy image mysqlclient==1.3.12 sqlalchemy-migrate

Или использовать Pipfile from gitlab для обновления программного обеспечения:
для этого необходимо зайти в shell: pipenv shell и прописать pipenv update

*********************************

Запуск парсера

Справка по командам парсера.
 
Для получения справки по командам парсера необходимо выполнить команду:

scrapy parse_booking --help

Появится справка по входным параметрам парсера

--help, -h              show this help message and exit

--city=CITY             City code. Must be an integer, according to internal
                        Booking.com id for location
                                                
--checkin=CHECKIN       Checkin date in ISO (YYYY-MM-DD) format

--checkout=CHECKOUT     Checkout date in ISO (YYYY-MM-DD) format

--proxy, -p             Use proxy servers

--cr=CONCURRENT_REQUESTS
                        Use maximum concurrent requests (default: 16)
                        
--crpd=CONCURRENT_REQUESTS_PER_DOMAIN
                        Use concurrent requests per domain (default: 16)
                        
--crpip=CONCURRENT_REQUESTS_PER_IP
                        Use concurrent requests per ip (default: 16)                    

*********************************

Пример запуска парсера для определенной локации и дат(например, Lviv) из командной строки:

scrapy parse_booking --city=-1045268 --checkin=2018-10-17 --checkout=2018-10-18,

где city - город, в представлении целого числа;

checkin - дата заезда;

checkout - дата отьезда.

Если необходимо подключить прокси, то добавить параметр --proxy, -p

Если необходимо подключить параллельные запросы, то добавить значение параметра 
--cr=целое число, по умолчанию 16

Если необходимо подключить параллельные запросы c домена, то добавить значение параметра 
--crpd=целое число, по умолчанию 16

Если необходимо подключить параллельные запросы с IP, то добавить значение параметра 
--crpip=целое число, по умолчанию 16

Картинка отеля сохраняется в папку full с использованием Media Pipeline scrapy,

а картинка комнат в папку rooms (комната по номеру id из booking, 
с использованием библиотеки urllib.request python)

*********************************

Для отправки статистики и уведомлений на почту необходимо прописать в settings.py

MAIL_USER = 'example@gmail.com'

MAIL_PASS = ''

*********************************

Создание базы данных  и миграции

Создать базу, прописать параметры соединения в CONNECTION_STRING в settings.py:

drivername - драйвер базы данных, например, mysql; user - логин пользователя; 
passwd - пароль; host - хост; port - порт; db_name - имя базы данных.

Перед запуском миграций необходимо запустить python database/manage.py version_control, 
если база новосозданная
Для запуска миграций необходмо выполнить python database/manage.py upgrade

*********************************

Выполнена настройка ведения файловых логов, 
настроены уровни записи ошибок в файл log.txt и в консоль.

*********************************

Перечень тестов:
*********************************
test 1: city => -1045268 => Lviv 
scrapy parse_booking --city=-1045268 --checkin=2018-10-17 --checkout=2018-10-18
*********************************
test 2: city => -3253342 =>Phuket
scrapy parse_booking --city=-3253342 --checkin=2018-10-07 --checkout=2018-10-08
*********************************
test 3: city => -372490 => Barcelona
scrapy parse_booking --city=-372490 --checkin=2018-12-30 --checkout=2018-12-31 --cr=32
*********************************
test 4: city => -1049092 => Odessa
scrapy parse_booking --city=-1049092 --checkin=2018-10-10 --checkout=2018-10-11 --cr=32
*********************************
test 5: city => -126693 => Roma
scrapy parse_booking --city=-126693 --checkin=2018-12-10 --checkout=2018-12-13 --cr=32
*********************************
test 6: city => 20014181 => Los Angeles
scrapy parse_booking --city=20014181 --checkin=2018-09-30 --checkout=2018-10-01
*********************************
test 7: city => -764696 => Marmaris
scrapy parse_booking --city=-764696 --checkin=2018-10-07 --checkout=2018-10-08
*********************************
test 8: city => -1058303 => Vinnitsa
scrapy parse_booking --city=-1058303 --checkin=2018-10-19 --checkout=2018-10-20
*********************************
test 9: city => -1898541 => Beijing
scrapy parse_booking --city=-1898541 --checkin=2018-09-30 --checkout=2018-10-01 --cr=32
*********************************
test 10: city => -1044367  => Kyiv
scrapy parse_booking --city=-1044367 --checkin=2018-09-30 --checkout=2018-10-01 --cr=32
*********************************
test 11: city => -780112 => Хайфа
scrapy parse_booking --city=-780112 --checkin=2018-10-19 --checkout=2018-10-20 -p
*********************************
test 12: city => -2173088 => Portu
scrapy parse_booking --city=-2173088 --checkin=2018-12-30 --checkout=2018-12-31 --cr=32
*********************************
test 13: city => -1364995 => Хельсинки
scrapy parse_booking --city=-1364995 --checkin=2018-12-07 --checkout=2018-12-08 --cr=32
*********************************
test 14: city => 20015732 => Сан-Франциско
scrapy parse_booking --city=20015732 --checkin=2018-12-15 --checkout=2018-12-16
*********************************
test 15: city => -570760 => Оттава
scrapy parse_booking --city=-570760 --checkin=2018-12-21 --checkout=2018-12-22
*********************************
test 16: city => -534433 => Варшава
scrapy parse_booking --city=-534433 --checkin=2018-12-28 --checkout=2018-12-29
*********************************
test 17: city => -513922 => Лодзь
scrapy parse_booking --city=-513922 --checkin=2018-12-01 --checkout=2018-12-02 --cr=32
*********************************
test 18: city => -1057311 => Ужгород
scrapy parse_booking --city=-1057311 --checkin=2018-11-01 --checkout=2018-11-02 --cr=32
*********************************
test 19: city => -1153951 => Бухарест
scrapy parse_booking --city=-1153951 --checkin=2018-11-15 --checkout=2018-11-16 
*********************************
test 20: city => -1995499 => Вена
scrapy parse_booking --city=-1995499 --checkin=2018-11-21 --checkout=2018-11-22