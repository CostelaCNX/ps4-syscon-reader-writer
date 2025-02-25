#! python3
import filecmp
import serial
import os
import time
import sys
import colorama
import hashlib
import serial.tools.list_ports
import math
import re
import base64
import subprocess
from distutils.version import StrictVersion
from colorama import init, Fore, Style, Back
import random
import platform
import struct
import datetime
import os
import base64
import zlib
import subprocess
import tempfile
import shutil

BLOCKSIZE = 1024

version = "2.5"

colorama.init()

def print_banner():
    print(Fore.BLACK + Back.CYAN + "*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + "     ___           __    _  ____________  ___          __      " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + "    / _ \___ _____/ /__ / |/ / __/ __/  |/  /__  ___  / /__    " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "   / // / _ `/ __/  '_//    / _/_\ \/ /|_/ / _ \/ _ \/  '_/    " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + "." + Fore.WHITE + Back.BLACK + "  /____/\_,_/_/ /_/\_\/_/|_/___/___/_/  /_/\___/_//_/_/\_\     " + Fore.BLACK + Back.CYAN + ".")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "                                                               " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + ":" + Fore.WHITE + Back.BLACK + "  /\\_/\\    and BwE Presents....                                " + Fore.BLACK + Back.CYAN + ":")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + " ( ~.~ )   "+ Fore.CYAN + "The Original Syscon Writer " + Fore.WHITE + "Version " + version + "              " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "|" + Fore.WHITE + Back.BLACK + " (>   <)                                                       " + Fore.BLACK + Back.CYAN + "|")
    print(Fore.BLACK + Back.CYAN + "*-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-*" + Back.BLACK + Style.RESET_ALL + "\n")

os.system('cls' if os.name == 'nt' else 'clear')
print_banner()

def checksum(data):
    csum = 0
    for d in data:
        csum += d
        csum &= 255

    csum -= 1
    csum &= 255
    return csum

def write(port, file, full, rew_ocd, confirm):
    if rew_ocd:
        input(Fore.RED + '\nWarning: OCD Flag (0x85) Will Be Written. Please Confirm...' + Style.RESET_ALL)
    print('\n==============================================================\n')
    print('Opening Serial Port: {}'.format(port))
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=5)
    except serial.serialutil.SerialException as e:
        print(Fore.RED + '\nError: Unable to Open Serial Port' + Style.RESET_ALL)
        print('\nPress Enter to Exit...')
        input()
        sys.exit(1)

    seek = 0 if full else 393216
    end_seek = 524288 if full else 458752
    arg = 4 + (full << 1) + rew_ocd
    print('\nWaiting...')
    start_time = time.time()
    threshold = 120
    while 1:
        elapsed_time = time.time() - start_time
        if elapsed_time > threshold:
            print('{0:60}'.format(Fore.RED + '\nWriter/Chip Timeout! Check Connections (Or Re-Install CH340 Drivers)!\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)
        resp = ser.read(1)
        if resp == b'\xff':
            print(Fore.GREEN + '\nChip Response!' + Style.RESET_ALL)
            time.sleep(1)
            ser.write(bytes([arg]))
            continue
        if resp == b'\xee':
            print('{0:60}'.format(Fore.RED + '\nChip Unresponsive! Check Connections!\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)
        if resp == b'\xf3' or resp == b'\xf4':
            print('\x1b[31mCannot Unlock OCD! Potential Brick!')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)
            return 0
        if resp == b'\xf2':
            print(Fore.GREEN + '\nOCD Unlocked!' + Fore.RESET)
        if resp == b'U':
            print(Fore.GREEN + 'OCD Programming Started...\n' + Fore.RESET)
        if resp == b'\x00':
            print(Fore.GREEN + '\nChip Glitching!' + Fore.RESET)
            sys.stdout.flush()
        if resp == b'\x10':
            try:
                f = open(file, 'rb')
                f.seek(seek)
                counter = seek
            except IOError as e:
                print('{0:60}'.format(Fore.RED + '\nCannot Open File!\n' + Style.RESET_ALL), '\r', end='')
                sys.stdout.flush()
                print('\nPress Enter to Exit...')
                input()
                sys.exit(1)

            input(Fore.RED + 'Write Process Will Begin. Please Confirm...' + Style.RESET_ALL)
            start_time = time.time()
            print('\nOpening File: {}\n\r\nErasing Blocks...'.format(file))
            print(Fore.RED + '\nDo Not Touch Chip or Reader!\n\r' + Style.RESET_ALL)
            print('==============================================================\n')
            while 1:
                counter += 512
                data = bytearray(f.read(512))
                c = checksum(data)
                data.append(c)
                while 1:
                    resp = ser.read(1)
                    if resp != b'\x01':
                        continue
                    ser.write(data)
                    resp = bytearray(ser.read(3))
                    if len(resp) != 3:
                        print(Fore.RED + 'Data Transfer Error! Check Board!\nPotentially Defective CH340 Chip/Driver!' + Style.RESET_ALL)
                        sys.stdout.flush()
                        print('\nPress Enter to Exit...')
                        input()
                        sys.exit(1)
                    if resp[2] == 17:
                        print(' {}Writing Offset: 0x{:06X}, Write Code: 0x{:02X}, Resp Code: 0x{:02X}'.format(Fore.GREEN if resp[1] == 0 else Fore.RED, counter - 1, resp[0], resp[1]))
                        break
                    else:
                        print(Fore.RED + 'Error @ Offset: 0x{:06X}, Write Code: 0x{:02X}, Resp Code: 0x{:02X}'.format(counter - 1, resp[0], resp[1]) + Style.RESET_ALL)

                if counter >= end_seek - 1:
                    print('')
                    print('Done!')
                    break

            print(Style.RESET_ALL + '\nElapsed time: {:0.4f} seconds'.format(time.time() - start_time))
            if not confirm:
                print('\nPress Enter to Exit...')
                input()
            ser.close()
            break

    if confirm:
        try:
            f = ['confirm.bin']
            for val in f:
                dump(val, port)

            with open(f[0], 'rb') as file1:
                contents1 = file1.read()
            with open(file, 'rb') as file2:
                contents2 = file2.read()
            comp = True
        except IOError as e:
            print('{0:60}'.format(Fore.RED + 'Confirm File Issue - Cannot Compare Files! (Do It Manually!)\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)

        try:
            for i in range(len(contents1)):
                if i == 195:
                    continue
                if contents1[i] != contents2[i]:
                    comp = False
                    break

            print('==============================================================\n')
            print('Comparing Files (Except OCD Flag)....')
            if comp:
                print(Fore.GREEN + '\nFiles Match!' + Style.RESET_ALL)
                print('\nPress Enter to Exit...')
                input()
            else:
                print(Fore.RED + '\nDanger! Files Do NOT Match!' + Style.RESET_ALL)
                print('\nPress Enter to Exit...')
                input()
        except IndexError as e:
            print('{0:60}'.format(Fore.RED + 'Cannot Compare Files! (Do It Manually!)\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)

def dump(s, port):
    print('\n==============================================================\n')
    print('Verifying Successful Write....\n')
    print('Opening Serial Port: {}'.format(port))
    try:
        ser = serial.Serial(port, baudrate=115200, timeout=5)
    except serial.serialutil.SerialException as e:
        print(Fore.RED + '\nError: Unable to open serial port ' + port + Style.RESET_ALL)
        print('\nPress Enter to Exit...')
        input()
        sys.exit(1)

    print('Waiting...\n')
    time.sleep(2)
    ser.write(bytes([0]))
    size = 0
    start_time = time.time()
    threshold = 120
    while size == 0:
        elapsed_time = time.time() - start_time
        if elapsed_time > threshold:
            print('{0:60}'.format(Fore.RED + '\nChip Timeout! Check Connections!\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)
        resp = ser.read(1)
        if resp == b'\xee':
            print('{0:60}'.format(Fore.RED + '\nChip Unresponsive! Check Connections!\n' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
            print('\nPress Enter to Exit...')
            input()
            sys.exit(1)
        if resp == b'\x00':
            print('{0:60}'.format(Fore.YELLOW + 'Glitching...' + Style.RESET_ALL), '\r', end='')
            sys.stdout.flush()
        if resp == b'\x91':
            print('{0:60}'.format(Fore.GREEN + 'Chip Responded 0x91 (OCD Connect CMD)' + Style.RESET_ALL))
            while 1:
                resp = ser.read(1)
                if resp == b'\x94':
                    print(Fore.GREEN + 'Chip Responded 0x94 (OCD EXEC CMD)\n' + Style.RESET_ALL)
                    print('Saving Dump As {}\n'.format(s))
                    f = open(s, 'wb')
                    f.close()
                    size = BLOCKSIZE
                    counter = 0
                    ser.read(1)
                    break

    while 1:
        data = ser.read(size)
        counter += size
        size = BLOCKSIZE
        f = open(s, 'ab')
        f.write(data)
        f.close()
        print('Dumping: {}/512KB'.format(os.stat(s).st_size // 1024), '\r', end='')
        sys.stdout.flush()
        if counter >= BLOCKSIZE * 512:
            print(Fore.GREEN + '\n\nDone!' + Style.RESET_ALL)
            print('\nElapsed Time: {:0.4f} Seconds\n'.format(time.time() - start_time))
            ser.close()
            time.sleep(1)
            break

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    ports = list(serial.tools.list_ports.comports())
    auto_ports = []
    for port in ports:
        if 'USB-SERIAL CH340' in port[1]:
            auto_ports.append(port[0])

    if auto_ports:
        if len(auto_ports) > 1:
            print(Fore.YELLOW + "Multiple Syscon Writers (Or CH340's) Found At " + ', '.join(auto_ports) + Style.RESET_ALL)
            port = input('Enter COM Port (Example COM4): ')
        else:
            print(Fore.GREEN + 'Syscon Writer Found At ' + auto_ports[0] + Style.RESET_ALL)
            port = auto_ports[0]
    else:
        port = input('Enter COM Port (Example COM4): ')
    if not port:
        print(Fore.RED + '\nError: No port specified. Exiting program.' + Style.RESET_ALL)
        print('\nPress Enter to Exit...')
        input()
        sys.exit(1)
    files = [f for f in os.listdir('.') if f.endswith('.bin') and os.path.getsize(f) == 524288]
    if not files:
        print(Fore.RED + '\nError: No Syscon Files Found.' + Style.RESET_ALL)
        print('\nPress Enter to Exit...')
        input()
        sys.exit(1)
    if len(files) == 1:
        file = files[0]
        print(Fore.GREEN + '\nSyscon File Found: {}'.format(file) + Style.RESET_ALL)
    else:
        print('\nMultiple Syscon Files Found:\n')
        for i, f in enumerate(files):
            print('{}. {}'.format(i + 1, f))

        selection = input('\nMake a Selection: ')
        if selection.isdigit() and int(selection) > 0 and int(selection) <= len(files):
            file = files[int(selection) - 1]
            print(Fore.GREEN + '\nSelected Syscon: {}'.format(file) + Style.RESET_ALL)
        else:
            print('Invalid Selection. Exiting program.')
            sys.exit(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    print(Fore.GREEN + 'Syscon Dump ' + file + ' Selected!\n' + Style.RESET_ALL)
    print('1. Write Per Console Data Only (0x60000+) - Fastest/Safest')
    print('2. Write Entire Chip Excluding Block 1 - Overwrites Firmware')
    print('3. Write Entire Chip Including Block 1 & Enable OCD (Unlock/Debug) - Recommend First Time Writing Only')
    option = input('\nSelect Writing Option (1-3): ')
    if option == '1':
        rew_ocd = False
        full = False
    elif option == '2':
        full = True
        rew_ocd = False
    elif option == '3':
        rew_ocd = True
        full = True
    else:
        print(Fore.RED + '\nError: Invalid Option Selected.' + Style.RESET_ALL)
        print('\nPress Enter to Exit...')
        input()
        sys.exit(1)
    confirm = input('\nConfirm Dump After Writing? (y/n): ')
    if confirm == 'y':
        confirm = True
    else:
        confirm = False
    write(port, file, full, rew_ocd, confirm)