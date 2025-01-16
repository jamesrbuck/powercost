# Track My Usage of Electricity

## Background

I purchased an EMU-2 home energy display from Puget Sound Energy (PSE).  The EMU-2 unit is manufactured by Rainforest Automation.  PSE intended customers to use the EMU-2 to ascertain how much electricity each appliance uses in an effort to reduce electricity usage.  A customer would put batteries in the unit, walk around and turn on and off various appliances to see the usage.  My intent from the start was to track the kWh electricity usage over time.  I can see what hours of the day have the most usage and I can track the daily usage as I progress through the monthly billing cycle.

## Scripting Electricity Data Collection

I searched for a way to script the collection of data. I found the emu_power Python library that automated the interface between Python and the EMU-2 serial device.  The same Python script can run on Linux and Windows computers with the only difference being the device name.  Windows 11 has a USB-Serial emulation port.

emu_power is based on the XML spec for the Rainforest RAVEN API.  The spec is similar to the API that the EMU-2 device uses.

```
Windows Port: COM5
Linux Port: /dev/ttyACM0
```

emu-power 1.51: https://pypi.org/project/emu-power/

## Design

### Overview

The EMU-2 reports the instaneous electricity usage when queried.  It returns a value in Kilowatt Hours (kWh) as if that amount was used for a full hour.  I wanted to get a total of electricity used for each whole hour.  I decided to take a reading every minute and add that value to an accumulator.  At the end of the hour, the script divides that amount by the number of readings which is usually 60.  This value is written to a tab-separated file.

### How to Run

The values are written within an infinite loop and the script must be externally stopped (i.e., killed) if desired.  The script can be run from the command line and it will check a file to see if it is already running.  It will stop if there is another instance running.  I created a Windows Scheduled Task in an effort to make the execution of the script as automated as possible.  The ohly trigger event was "System Startup" since the script is always running (but sleep()'ing most of time).  I ran into problems when I tried to added schedule triggers to force the script to start if it somehow failed.  I gave this up since the script is reliable.

![Windows Scheduler](./WindowsScheduledTask.jpg)

### Functions

I soon realized that I needed to put the values into a database.  This allowed me to use my SQL skills to query the results in different ways.  The next step was to setup a MySQL database to receive the values.

* def insertDB(myDate, myHour, mykWh): A self-contained function to insert a record into the database.
* class MySignalHandler:
  * def setup(self,thePID,theAR): Initialize signal handler and the variables PID and AR
  * def catch(self, signalNumber, frame): Get the current time, set a message and print the message; remove file indicating the script is running; flush STDOUT and STDERR; call os.kill() to kill itself.
* def main(): Only runs code if the script is run as a top-level script.

The script has a main() function that contains the most of the code.  main() is used to ensure that the script is run as top-level script.

### Logic

* if __name__ == '__main__':
  * Get command line arguments with parser
  * Read confifuration file with config
  * If script-is-executing file exists, exit
  * Redirect STDOUT and STDERR to log file
  * Get config values into script variables
  * Setup signal handler
  * Create script-is-executing file
  * Call main()

* main():
  * while True:
    * If Stop-File exists, exit
    * Retry loop on call to api.get_instantaneous_demand()
    * Check if call failed and exit if it did
    * Get values: demand, divisor, multiplier, kw
    * Check if we're still in the same hour and add to kWh if so
    * else write kWh out, stop_serial() and start_serial() to refresh serial connection
    * Retry loop on start_serial()
    * Check if it's Midnight and print summary if it is.  Note that this code is obsolete since we're also inserting values into the database.
    * sleep 60 seconds


### Database

**DB_setup.sql**

```
create database pse

use pse;

CREATE TABLE `pse`.`usage_e` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `UDate` DATE NOT NULL,
  `UTime` TIME NOT NULL,
  `kWh` DECIMAL(7,3) NULL DEFAULT 0.0,
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `I_USAGE_E_UNIQUE` (`ID` ASC) VISIBLE)
COMMENT = 'Puget Sound Energy Electricity Usage for The Ponderosa';
```

**DB_hourly.sql**

```
use pse;

select
   UDate,
   substring(UTime,1,5) as the_hour,
   kWh
from
   usage_e
order by
   ID desc;
```

**DB_daily.sql**

```
use pse;

select
   UDate as Date
   ,ELT(dayofweek(UDate),'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') as DoW
   ,round(sum(kWh)/count(kWh),3) as kWh_Hr_avg
   ,count(kWh) as hours
   ,sum(kWh) as kWh_day_total
   ,round(((sum(kWh)/count(kWh))*24*0.105),2) as kWh_day_total_cost
   ,round((sum(kWh)/count(kWh))*24,3) as kWh_24hr_est
from
   usage_e
where
   UDate >='2022-11-05' and
   UDate <='2022-12-04'
group by
   UDate
order by
   UDate
;
```

## Windows 11 Hardware View

Note: The COMx value changed occasionally but is always below "Ports (COM & LPT)".

![Device Manager](./WinDev01.jpg)
![Properties General](./WinDev02.jpg)
![Properties Port Settings](./WinDev03.jpg)
![Properties Driver](./WinDev04.jpg)
