import os
from configparser import BasicInterpolation, ConfigParser

class PonderosaConfig:
    def __init__(self,INIFile,startTS):
        self.INIFile = INIFile
        self.startTS = startTS

        config = ConfigParser()
        config.read(INIFile)
        self.log_dir   = config.get('setup','log_dir')
        self.log_file  = "\\EMU_log_" + startTS + ".txt"
        self.out_file  = "\\EMU_out_" + startTS + ".txt"
        self.the_port  = config.get('setup','the_port')
        self.out_dir   = config.get('setup','out_dir')

        self.dbUser             = config.get('database','dbUser')
        self.dbPassword         = config.get('database','dbPassword')
        self.dbHost             = config.get('database','dbHost')
        self.dbName             = config.get('database','dbName')
        self.dbRaiseOnWarnings  = config.getboolean('database','dbRaiseOnWarnings')
        self.dbConfig = {
            'user': self.dbUser,
            'password': self.dbPassword,
            'host': self.dbHost,
            'database': self.dbName,
            'raise_on_warnings': self.dbRaiseOnWarnings
        }

    def __str__(self):
        return(f"log_dir   = \"{self.log_dir}\"\n" +
        f"log_file  = \"{self.log_file}\"\n" +
        f"the_port  = \"{self.the_port}\"\n" +
        f"out_dir   = \"{self.out_dir}\"\n" +
        f"startTS   = \"{self.startTS}\"\n" +
        f"dbConfig  = {self.dbConfig}")

    def getlog_dir(self):
        return(self.log_dir)

    def getlog_file(self):
        return(self.log_file)

    def getout_file(self):
        return(self.out_file)

    def getthe_port(self):
        return(self.the_port)

    def getout_dir(self):
        return(self.out_dir)

    def getdbConfig(self):
        return(self.dbConfig)
