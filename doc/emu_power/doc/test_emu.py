#!/usr/bin/python

# https://stackoverflow.com/questions/15828910/raspberry-pi-rainforest-emu-2-python-read-time-from-sce-smart-meter

# lsusb
# -----
# Bus 001 Device 004: ID 04b4:0003 Cypress Semiconductor Corp. RFA-Z105-2 HW2.7.3 EMU-2

# root@raspberrypi:/dev/serial/by-id# ll
# total 0
# drwxr-xr-x 2 root root 60 Mar 20 17:30 ./
# drwxr-xr-x 4 root root 80 Mar 20 17:30 ../
# lrwxrwxrwx 1 root root 13 Mar 20 17:30 usb-Rainforest_Automation__Inc._RFA-Z105-2_HW2.7.3_EMU-2-if00 
#     -> ../../ttyACM0


from emu_power import Emu

print("==> Instantiate api with Emu(synchronous=True)")
#api = Emu(synchronous=True)
api = Emu(debug=True,timeout=5,synchronous=True)

print("\n==> api.start_serial() ...")
api.start_serial("/dev/ttyACM0")

print("\n==> response = api.get_device_info() ...")
response = api.get_device_info()

print("\n==> response = api.get_connection_status() ...")
response = api.get_connection_status()

print("\n==> response = api.get_schedule() ...")
response = api.get_schedule()

print("\n==> response = api.get_meter_info() ...")
response = api.get_meter_info()

print("\n==> response = api.get_instantaneous_demand() ...")
response = api.get_instantaneous_demand()


