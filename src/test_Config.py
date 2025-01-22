from PonderosaConfig import PonderosaConfig
from time import time, ctime
import time
import os

INI = "D:/git/powercost/src/Ponderosa_Electricity_Usage.ini"
startTS = time.strftime('%Y%m%d-%H%M%S', time.localtime())
PC = PonderosaConfig(INI,startTS)

log_dir  = PC.getlog_dir()
log_file = PC.getlog_file()
out_file = PC.getout_file()
out_dir  = PC.getout_dir()
the_port = PC.getthe_port()
dbConfig = PC.getdbConfig()

print( f"log_dir   = \"{log_dir}\"" )
print( f"the_port   = \"{the_port}\"" )
print( f"out_dir   = \"{out_dir}\"" )
print( f"startTS   = \"{startTS}\"" )
print( f"dbConfig   = \"{dbConfig}\"" )
