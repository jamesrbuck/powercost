# Script Ponderosa_Electricity_Usage.ps1

param(
   [string]$rundir,
   [string]$srcdir
)

# Set timestamp to be used in the log file.
$ts   = Get-Date -Format "yyyyMMdd-HHmm"

$log = $rundir + "logs\launch_" + $ts + ".txt"
$ini = $rundir + "Ponderosa_Electricity_Usage.ini"

# Run Program
# -----------
$script = "$srcdir\Ponderosa_Electricity_Usage.py"
$Stream = [System.IO.StreamWriter]::new($log)
$Stream.WriteLine("script   = " + $script)
$Stream.WriteLine("basedir  = " + $basedir)
$Stream.WriteLine("log      = " + $log)

# Redirect standard output to the StreamWriter
[System.Console]::SetOut($Stream)

$process = Start-Process -FilePath "D:\Python\pythonw.exe" -ArgumentList "$script --ini $ini -WorkingDirectory $rundir -PassThru -NoNewWindow

$Stream.WriteLine("PID      = " + $process.Id)
$Stream.WriteLine("Name     = " + $process.Name)
$Stream.Close()

exit
