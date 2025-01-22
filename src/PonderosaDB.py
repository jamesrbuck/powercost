import mysql.connector
from mysql.connector.errors import Error

class PonderosaDB:
    def __init__(self,dbConfig):
        self.record_stmt = {}
        self.record_data = {}
        self.dbConfig = dbConfig

    def insert(self,myDate,myHour,mykWh):
        try:
            conn = mysql.connector.connect(**self.dbConfig)
            self.record_stmt = ("INSERT INTO usage_e (UDate, UTime, kWh) VALUES (%(UDate)s, %(UTime)s, %(kWh)s)" )
            self.record_data = { 'UDate': myDate, 'UTime':myHour,  'kWh': mykWh }
            cursor = conn.cursor()
            cursor.execute(self.record_stmt,self.record_data)
            conn.commit()
        except mysql.connector.Error as err:
            print(f"PonderosaDB.py: MySQL Error: {err}")
            raise
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def __str__(self):
        return(f"record_stmt = {self.record_stmt}\n" +
             f"record_data = {self.record_data}")
