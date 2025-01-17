echo off

set PATH=D:\git\powercost\src:%PATH%

rem ---------------------------------------------------------------------------
rem Make sure hour has leading zero
rem ---------------------------------------------------------------------------
:: Get the time separator
FOR /F "TOKENS=3" %%D IN ('REG QUERY ^"HKEY_CURRENT_USER\Control Panel\International^" /v sTime ^| Find ^"REG_SZ^"') DO (Set _time_sep=%%D)


FOR /f "tokens=1,2,3 delims=:.%_time_sep%" %%G IN ("%time%") DO (
Set "_hr=%%G"
Set "_min=%%H"
Set "_sec=%%I"
)

::strip any leading spaces
Set _hr=%_hr: =%

::ensure the hours have a leading zero
if 1%_hr% LSS 20 Set _hr=0%_hr%

set hhmm=%_hr%%_min%

rem Set timestamp to be used in the backup log file.
set ts=%date:~10,4%%date:~4,2%%date:~7,2%_%hhmm%
set log=D:\a\EMU-2\logs\launch_%ts%.txt

echo on

rem ---------------------------------------------------------------------------
rem Run Program
rem ---------------------------------------------------------------------------
D:\Python\pythonw.exe D:\a\EMU-2\code\Ponderosa_Electricity_Usage.py --ini D:\a\EMU-2\code\Ponderosa_Electricity_Usage.ini %1 > %log% 2>&1

pause
exit 0
