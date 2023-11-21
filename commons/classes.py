import sys
from django.db import connections
import pyodbc
import ftplib
import traceback
from django.conf import settings

class cursores:
    def __init__(self, nombre_bd):
        self.nombre_bd = nombre_bd
        self.cursor = connections[self.nombre_bd].cursor()

    def ejecutar_consulta(self, consulta):
        try:
            self.cursor.execute(consulta)
            return self.cursor.fetchall()
        except Exception:
            e = sys.exc_info()[1]
            print(e)
    def get_cursor(self):
        return self.cursor
    def close_cursor(self):
        self.cursor.close()

class conexion_comerssia:
    def __init__(self):
        self.server = 'tcp:comerssiamirror.eastus2.cloudapp.azure.com,38693'
        self.database = 'BIGJOHN'
        self.username = 'bigjohn'
        self.password = '2UMIrtsqCEmkv'
        self.cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cursor = self.cnxn.cursor()
    def get_cursor(self):
        return self.cursor

class conexion_ftp:
    def __init__(self):
        try:
            self.__ftp = ftplib.FTP('srv09.comerssia.com')
            self.__ftp.login('bigjohn', 'A1ktm23o')
        except:
            traceback.print_exc()
    
    def obtener_ftp_salida(self):
        try:
            self.__ftp.cwd('Interfaces/Salida')
            self.__ftp.encoding='utf-8'
            self.__ftp.sendcmd('OPTS UTF8 ON')
            return self.__ftp
        except:
            traceback.print_exc()
   