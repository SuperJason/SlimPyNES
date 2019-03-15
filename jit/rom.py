#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class ROM():
    def __int__(self):
        self.PRG = 0
        self.CHR = 0
        self.MAPPER = 0

        self.RCB = 0
        self.OS_MIRROR = 0
        self.FS_MIRROR = 0
        self.TRAINER = 0
        self.SRAM = 0
        self.MIRRORING = 0

def rom_headercheck(rom, file_name):
    rom_file = open(file_name, 'rb')
    header = rom_file.read()
    rom_file_size = rom_file.tell()
    print(' -- Detect Rom Size: %dkB'%(rom_file_size / 1024))

    # NES and EOF
    if header[0] != 0x4e or header[1] != 0x45 or header[2] != 0x53 or header[3] != 0x1a:
        print('header[0-3] is not NES and EOF')
        return False

    #print(header[4:])
    rom.RPG = header[4]
    print(' -- %d x 16kB pages RPG found'%(rom.RPG))
    rom.CHR = header[5]
    print(' -- %d x 8kB pages CHR found'%(rom.CHR))
    flag_6 = int(header[6])
    #print('Flag 6: %d'%(flag_6))
    flag_7 = int(header[7])
    #print('Flag 7: %d'%(flag_7))
    rom.MAPPER =  (flag_6 >> 4) | (flag_7 & 0xf0)
    print('MAPPER: %d'%(rom.MAPPER))
    rom.MIRRORING = flag_6 & 0x01
    rom.SRAM = flag_6 & 0x02
    rom.TRAINER = flag_6 & 0x04
    rom.FS_MIRROR = flag_6 & 0x08
    print('MIRRORING: %d'%(rom.MIRRORING))
    print('SRAM: %d'%(rom.SRAM))
    print('TRAINER: %d'%(rom.TRAINER))
    print('FS_MIRROR: %d'%(rom.FS_MIRROR))

    rom_file.close()

    return True

def rom_load(rom, rom_file_name, cpu_mem, ppu_mem):
    rom_file = open(rom_file_name, 'rb')
    romcache = rom_file.read()
    len16k = 16 * 1024
    len8k = 8 * 1024
    if rom.RPG == 1:
        size = len16k
        for i in range(size):
            cpu_mem[0x8000 + i] = romcache[16 + i]
            cpu_mem[0xC000 + i] = romcache[16 + i]

        #cpu_mem[0x8000:0x8000+size] = romcache[16:16+size]
        #cpu_mem[0xC000:0xC000+size] = romcache[16:16+size]
    else:
        size = len16k
        for i in range(size):
            cpu_mem[0x8000 + i] = romcache[16 + i]
            cpu_mem[0xC000 + i] = romcache[16 + (rom.RPG - 1) * len16k + i]
            # Reset Vector: PCL from 0xFFFC(Here is i: 0x3FFC and rom offset: 0x800C)
            #               PCH from 0xFFFD(Here is i: 0x3FFD and rom offset: 0x800D)
            #if (0xC000 + i == 0xFFFD):
            #    print('0xFFFD(i: 0x%x, rom offset: 0x%x): 0x%x'%(i, 16 + (RPG - 1) * len16k + i, romcache[16 + (RPG - 1) * len16k + i]))
        #cpu_mem[0x8000:0x8000+size] = romcache[16:16+size]
        #cpu_mem[0xC000:0xC000+size] = romcache[16+(RPG-1)*len16k:16+(RPG-1)*len16k+size]

    if rom.CHR != 0:
        size = len8k
        offset = 16 + rom.RPG * len16k
        for i in range(size):
            ppu_mem[i] = romcache[offset + i]

        #offset = 16+RPG*len16k
        #ppu_mem = romcache[offset:offset+len8k]
        #offset = 16+RPG*len16k+len8k
        #tital = romcache[offset:offset+128]

    rom_file.close()
