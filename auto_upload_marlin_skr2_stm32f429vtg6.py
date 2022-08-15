#################################################################################################################################
#
#	This stuff works for me with (tested just 2 main setups):
#		Microsoft Visual Studio Code
#			Version: 1.68.1
#			Commit: 30d9c6cd9483b2cc586687151bcbcd635f373630
#			Date: 2022-06-15T02:58:26.441Z
#			Electron: 17.4.7
#			Chromium: 98.0.4758.141
#			Node.js: 16.13.0
#			V8: 9.8.177.13-electron.0
#			OS: Linux x64 5.13.0-51-generic#
#           Version: 1.70.0
#           Commit: da76f93349a72022ca4670c1b84860304616aaa2
#           Date: 2022-08-04T04:38:48.541Z
#           Electron: 18.3.5
#           Chromium: 100.0.4896.160
#           Node.js: 16.13.2
#           V8: 10.0.139.17-electron.0
#           OS: Linux x64 5.15.0-41-generic#
#		Ubuntu 
#           20.04.4 LTS Focal Fossa
#		PlatformIO 
#           Core 6.0.2·Home 3.4.2
#           Core 6.1.3 Home 3.4.3
#       Marlin
#		    Marlin-bugfix-2.0.x, date 220422, time 16:15
#		    Marlin-bugfix-2.1.x, date 220617, time 17:38
#           Marlin-bugfix-2.1.x, date 220822, time 17:52
#		Bigtreetech SKR 2 with STM32F429VGT6 and a working/mounted SDcard
#
#	ellensp gave me an older example. Thanks a lot, you showed me the way!
#
#	Be aware, there are no other people who tried this yet! 
#
#	Expected behaviour:
#       Compilation of Marlin firmware, automatic upload to your SKR 2 over SDcard without resetting your SKR 2 by push button or power recycle.
#
#	IMPORTANT: Before you start, you have to do five tasks! 
#
#   		Task one: Insert path of your SDCARD in SKR 2 (important entries in this python script are marked with 'hcet14')!
#
#   		Task two: Copy this script to /root//buildroot/share/PlatformIO/scripts/ (/root/ = top directory in Visual Studio Code)!
#    
#		Task three: Copy stm32f4.ini to /root/ini (or change marked entries with 'hcet14')!   	
#    
#   		Task four: Check your platformio.ini for 'default_envs = BIGTREE_SKR_2_F429_USB'!
#
#		Task five: Make sure your SDCARD is mounted!
#	
#	Be aware! You use this on your own risk! 
#	
#	In ABM Panel choose 'BIGTREE_SKR_2_F429_USB Upload' button (see also 'abm_panel.png')!
#
###################################################################################################################################

# Version_220710
# licensed under GPLv3

from __future__ import print_function

from tkinter import Tk, filedialog
from tkinter import messagebox

import pioutil
import os
import glob
import shutil
import serial
import time
import re
import serial.tools.list_ports

path_sdcard = '/media/hcet/CPOC/' #hcet14:Insert path of your SDCARD in SKR 2!!!
path_platformio = (os.getcwd())   #current working directory of PlatformIO

#delete all .bin files on your sdcard
files = glob.glob(path_sdcard + '*.bin')	
for f in files:
    os.remove(f)

#rename FIRMWARE.CUR, if existing, to FIRMWARE_old.CUR
try:
	f = open(path_sdcard + '/FIRMWARE.CUR')
	f.close()
except IOError:
    print("File not accessible")
else:
	os.rename((path_sdcard + '/FIRMWARE.CUR'), (path_sdcard + '/FIRMWARE_old.CUR'))  #rename FIRMWARE.CUR to FIRMWARE_old.CUR



if pioutil.is_pio_build():

	Import("env")

	def print_error(e):
		print('\nUnable to find destination disk (%s)\n' %( e ) )

	def before_upload(source, target, env):
			
		upload_disk = ''

		root = Tk() # pointing root to Tk() to use it as Tk() in program.
		root.withdraw() # hides small tkinter window.

		root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.

		#upload_disk = filedialog.askdirectory(initialdir = path_sdcard, title="Select the root of your SDCARD") # Returns opened path as str, initialdir = Root of your SDCARD
		upload_disk = path_sdcard #use above tk window, if you want to choose where to upload new fw

		#make a backup of the new firmware
		if os.path.exists('.pio/build/BIGTREE_SKR_2_F429_USB/backup'):
			print (".pio/build/BIGTREE_SKR_2_F429_USB/backup exist")
		else:
			os.mkdir('.pio/build/BIGTREE_SKR_2_F429_USB/backup')

		global bu

		data = os.listdir('.pio/build/BIGTREE_SKR_2_F429_USB/')
		for bu in data:
			if bu.startswith("firmware-") and bu.endswith(".bin"):
				print('NAME:', bu)
				print('DATA:', data)
				old_file = os.path.join('.pio/build/BIGTREE_SKR_2_F429_USB/', bu)
				print('OLD_FILE:', old_file)
				shutil.copy(old_file, '.pio/build/BIGTREE_SKR_2_F429_USB/backup')

		#rename fresh firmware-date-time.bin in /root/.pio/build/BIGTREE_SKR_2_F429_USB/ to firmware.bin
		global name
		
		data = os.listdir('.pio/build/BIGTREE_SKR_2_F429_USB/')
		new_file = os.path.join('.pio/build/BIGTREE_SKR_2_F429_USB/', "firmware.bin")
		print('NEW_FILE;', new_file)
		
		for name in data:
			if name.startswith("firmware-") and name.endswith(".bin"):
				print('NAME:', name)
				print('DATA:', data)
				old_file = os.path.join('.pio/build/BIGTREE_SKR_2_F429_USB/', name)
				print('OLD_FILE:', old_file)
				os.rename(old_file, new_file)



		
		if not upload_disk:
			print_error('Canceled')
			return
		else:
			env.Replace(
				UPLOAD_FLAGS="-P$UPLOAD_PORT"
			)
			env.Replace(UPLOAD_PORT=upload_disk)
		
		#copy firmware.bin from /root/.pio/build/BIGTREE_SKR_2_F429_USB/
		shutil.copy('.pio/build/BIGTREE_SKR_2_F429_USB/firmware.bin', path_sdcard)
		
		#reads baudrate of SERIAL_PORT -1 from Configuration.h
		with open(path_platformio + '/Marlin/Configuration.h', 'r') as f:
			for l in f.readlines():
				if re.search(r'\#define BAUDRATE\b', l):
					print(l)
					baudrate_ser_1=l
					print(baudrate_ser_1)
					baudrate = int(''.join(list(filter(lambda x: x.isdigit(), baudrate_ser_1))))
					print(baudrate)

		#detects the current serial port used by your SKR 2 (for me, it changes with every reboot between ttyACM0 and ttyACM1)
		ports = serial.tools.list_ports.comports()

		for port, desc, hwid in sorted(ports):
			print("{}: {} [{}]".format(port, desc, hwid))
			ser = serial.Serial(port, baudrate)	#set serial port + baudrate
			time.sleep(2)
			ser.write("M997\r\n".encode())	#Firmware update
			time.sleep(1)
			ser.close()

		time.sleep(1)
		#hcet14: final info message, uncomment if you want it!
		#messagebox.showinfo(title='New fw should have been uploaded to your SKR 2!', message='New fw should have been uploaded to your SKR 2!')
			
	env.AddPreAction("upload", before_upload)
	
	
	
	
	
