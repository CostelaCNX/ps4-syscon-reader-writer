#!/usr/bin/env python2

import filecmp
import serial
import os
import time
import sys
import colorama
import hashlib
import serial.tools.list_ports
from colorama import init, Fore, Style, Back

BLOCKSIZE = 1024

colorama.init()

def print_banner():
    print(Fore.BLACK + Back.CYAN + "*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + "     ___           __    _  ____________  ___          __      " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + "    / _ \___ _____/ /__ / |/ / __/ __/  |/  /__  ___  / /__    " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "   / // / _ `/ __/  '_//    / _/_\ \/ /|_/ / _ \/ _ \/  '_/    " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + "." + Fore.WHITE + Back.BLACK + "  /____/\_,_/_/ /_/\_\/_/|_/___/___/_/  /_/\___/_//_/_/\_\     " + Fore.BLACK + Back.CYAN + ".")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "                                                               " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "  /\\_/\\    and BwE Presents....                                " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + " ( ~.~ )   "+ Fore.CYAN + "The Original Syscon Reader " + Fore.WHITE + "Version 3.0" + "              " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + " (>   <)                                                       " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*" + Back.BLACK + Style.RESET_ALL + "\n")


os.system('cls')
print_banner()

syscon_hashes = {
    "2.26": "263BD07F5B80F64ACA8A107FEE27EE08",
    "2.23_4": "F7E0A6157FA9C04944B927051B5D4196",
    "2.23_3": "C42C250BBB7B30ACD2F3960CFAD9C8E3",
    "2.23_2": "A7D36425E5881770B2E9C4F925CED39F",
    "2.23_1": "39A1BDD270D0DC2BDCE8D81E7525AF41",
    "2.13_5": "D89B1256E2A3B2D4C3044BFB5F44E8A5",
    "2.13_4": "D72B5263F90BF0A196764F8C8572C952",
    "2.13_3": "581D42D6A6C83992521420A23F02427C",
    "2.13_2": "45EBE778279CA58B6BF200FF1BD2CB9E",
    "2.13_1": "1C70248C249F0AC4F0C5555499AFA6EF",
    "2.06_2": "FA4DDDB3F17315ECC028BF725B7702B1",
    "2.06_1": "6741017A1499384DD7B07DC6DEF28D1E",
    "1.0B": "BAEA46D4D5BF6D9B00B51BDA40DB0F48",
    "1.00": "125CD5CC2D854E5F2812F060A7031044",
    "1.00D": "1F302ACB86F76D8148A2697E396A332A",
    "1.0BD": "B57B4A9F72FEAC1D212E577D6B8E8098",
    "2.06_1D": "AAA48C7B49237A1618CF97CB2BB0F6A2",
    "2.06_2D": "827CA23CD1B853D730FB9FC6C67EE783",
    "2.13_1D": "C2480931C397B2E8A92995751E7E07DF",
    "2.13_2D": "4EE8F0F7DA0B991F6EBBCF3256F355DE",
    "2.13_3D": "DA0624402A72BFE44E5E6B15282B00E3",
    "2.13_4D": "57A70A08475E8AC9630458B8F4898EA0",
    "2.13_5D": "0C2D1C14B8E9FA42BB74BE63ADAE04E1",
    "2.23_1D": "7023E24401BEB142BEC7C644E5343996",
    "2.23_2D": "F2FA41E9D693BF5A4FCF3DBD8189483E",
    "2.23_3D": "F49E143B692CAF13688ED853874C7390",
    "2.23_4D": "27CA52CADF19BA6A33D2DF321A1FC0B2",
    "2.26D": "62703902E60DFDCC3FDB8749433DBFEC",
    
}
def dump(s):
    #print "=======================================================\n"
    print "Opening Serial Port: {}".format(port.upper())
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=5)
    except serial.serialutil.SerialException as e:
        print(Fore.RED + "\nError: Unable to open serial port " + port + Style.RESET_ALL)
        print ("\nPress Enter to Exit...")
        raw_input()  
        sys.exit(1) 
    print "\nWaiting...\n"
    time.sleep(2)
    ser.write(chr(0x00))
    size = 0
    start_time = time.time()
    threshold = 360
    while size == 0:
        elapsed_time = time.time() - start_time
        if elapsed_time > threshold:
            print "{0:60}".format(Fore.RED + "\nChip Timeout! Check Connections!\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)
        try:            
            resp = ser.read(1)
        except serial.serialutil.SerialException as e:
            print "{0:60}".format(Fore.RED + "\nSerial Exception: Access Denied (USB Unplugged?)\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)
        except KeyboardInterrupt:
            print "{0:60}".format(Fore.RED + "\nProgram Interrupted By User\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)
        if resp=="\xEE":
            print "{0:60}".format(Fore.RED + "\nChip Unresponsive! Check Connections!\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)
        if resp=="\x00":
            print "{0:60}".format(Fore.YELLOW + "Glitching..." + Style.RESET_ALL),'\r',
            sys.stdout.flush()
        if resp =="\x91":
            print("{0:60}".format(Fore.GREEN + "Chip Responded 0x91 (OCD Connect CMD)" + Style.RESET_ALL))
            while 1:
                resp = ser.read(1)
                if resp =="\x94":
                    print(Fore.GREEN + "Chip Responded 0x94 (OCD EXEC CMD)\n" + Style.RESET_ALL)
                    print "Saving Dump As {}\n".format(s)
                    f = open(s, 'wb')
                    f.close()
                    size = BLOCKSIZE 
                    counter = 0
                    ser.read(1)
                    break
    while 1:
        try:
            data = ser.read(size)
            counter += size
            size = BLOCKSIZE
            f = open(s, 'ab')
            data = str(data)
            f.write(data)
            f.close()
            print "Dumping: {}/512KB".format(os.stat(s).st_size/1023),'\r',
            sys.stdout.flush()
            if counter>=(BLOCKSIZE*512):
                print(Fore.GREEN + "\n\nDone!" + Style.RESET_ALL)
                print ("\nElapsed Time: {:0.4f} Seconds\n".format(time.time() - start_time))
                ser.close()
                time.sleep(1)
                break
        except serial.serialutil.SerialException as e:
            print "{0:60}".format(Fore.RED + "\n\nSerial Exception: Access Denied (USB Unplugged?)\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)
        except KeyboardInterrupt:
            print "{0:60}".format(Fore.RED + "\n\nProgram Interrupted By User\n" + Style.RESET_ALL),'\r',
            sys.stdout.flush()
            print ("\nPress Enter to Exit...")
            raw_input()  
            sys.exit(1)

def main(port):
	if  len(port) <= 1:
		print (Fore.RED + "\nError: Invalid COM Port!" + Style.RESET_ALL)
		print ("\nPress Enter to Exit...")
		raw_input()  
		sys.exit(1)
		return 0

	os.system('cls')
	print_banner()
	f = ["syscon1.bin", "syscon2.bin"]
	for val in f:
		dump(val)
	comp = filecmp.cmp(f[0], f[1])
	print "=======================================================\n"
	print "Comparing Files...."
	if comp:
		print (Fore.GREEN + "\nFiles Match!" + Style.RESET_ALL)
		print "\n=======================================================\n"
		print "Validating Syscon Firmware...."

		f = open(f[0], 'rb')
		f.seek(0x0)
		data = f.read(0x60000)
		hash = hashlib.md5(data).hexdigest()
		hash = hash.upper()
		key_value_pairs = syscon_hashes.items()
		if hash in [v for k, v in key_value_pairs]:
			for number, desired_hash in syscon_hashes.items():
				if hash == desired_hash:
					print(Fore.GREEN + "\nSyscon Firmware " + number + " Valid!" + Style.RESET_ALL)
		else:
			print (Fore.RED + "\nDanger! Syscon Firmware Invalid!" + Style.RESET_ALL)
			print ("\nPress Enter to Exit...")
			raw_input()  
			sys.exit(1)

	else:
		print (Fore.RED + "\nDanger! Files Do NOT Match!" + Style.RESET_ALL)
		print ("\nPress Enter to Exit...")
		raw_input()  
		sys.exit(1)


	print ("\nPress Enter to Exit...")
	raw_input()  
	sys.exit(1)

	
if __name__ == '__main__':
	print_banner()

	ports = list(serial.tools.list_ports.comports())
	auto_ports = []
	for port in ports:
		if "USB-SERIAL CH340" in port[1]:
			auto_ports.append(port[0])

	if auto_ports:
		if len(auto_ports) > 1:
			print(Fore.YELLOW + "Multiple Syscon Readers (Or CH340's) Found At " + ", ".join(auto_ports) + Style.RESET_ALL)
			port = raw_input("Enter COM Port (Example COM4): ")
		else:
			print(Fore.GREEN + "Syscon Reader Found At " + auto_ports[0] + Style.RESET_ALL)
			port = auto_ports[0]
	else:
		port = raw_input("Enter COM Port (Example COM4): ")


	if not port: 
		print(Fore.RED + "\nError: No port specified. Exiting program." + Style.RESET_ALL)
		print ("\nPress Enter to Exit...")
		raw_input()  
		sys.exit(1) 

	main(port)
    
