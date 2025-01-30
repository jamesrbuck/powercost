# Set timestamp to be used in the log file.
$ts   = Get-Date -Format "yyyyMMdd-HHmm"
$log = "D:\a\EMU-2\logs\launch_" + $ts + ".txt"

# Run Program
# -----------
$basedir = "D:\git\powercost\src"
$script = "$basedir\Ponderosa_Electricity_Usage.py"
$Stream = [System.IO.StreamWriter]::new($log)
$Stream.WriteLine("script   = " + $script)
$Stream.WriteLine("basedir  = " + $basedir)
$Stream.WriteLine("log      = " + $log)

# Redirect standard output to the StreamWriter
[System.Console]::SetOut($Stream)

$process = Start-Process -FilePath "D:\Python\pythonw.exe" -ArgumentList "$script  --ini $basedir\Ponderosa_Electricity_Usage.ini" -WorkingDirectory $basedir -PassThru -NoNewWindow

$Stream.WriteLine("PID      = " + $process.Id)
$Stream.WriteLine("Name     = " + $process.Name)
$Stream.Close()

exit
