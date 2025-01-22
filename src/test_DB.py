from PonderosaDB import PonderosaDB
from time import time, ctime
import time
import os


dbConfig  = {'user': 'x', 'password': 'x', 'host': 'x', 'database': 'x', 'raise_on_warnings': True}

mytime    = time.localtime()
myDate    = time.strftime('%Y-%m-%d', mytime)
myHour    = time.strftime('%H:%M:%S', mytime)
myKwh     = 3.65

#myDate = 'XXX'  # Bad date as test for the exception

db = PonderosaDB(dbConfig)
db.insert(myDate, myHour, myKwh)
print(db)
