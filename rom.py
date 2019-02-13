#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class ROM:
    def __init__(self, nes):
        self.nes = nes
        self.PRG = 0
        self.CHR = 0
        self.MAPPER = 0

        self.RCB = 0
        self.OS_MIRROR = 0
        self.FS_MIRROR = 0
        self.TRAINER = 0
        self.SRAM = 0
        self.MIRRORING = 0

    def headercheck(self, file_name):
        rom_file = open(file_name, 'rb')
        header = rom_file.read()
        rom_file_size = rom_file.tell()
        print(' -- Detect Rom Size: %dkB'%(rom_file_size / 1024))

        # NES and EOF
        if header[0] != 0x4e or header[1] != 0x45 or header[2] != 0x53 or header[3] != 0x1a:
            print('header[0-3] is not NES and EOF')
            return False

        #print(header[4:])
        self.RPG = header[4]
        print(' -- %d x 16kB pages RPG found'%(self.RPG))
        self.CHR = header[5]
        print(' -- %d x 8kB pages CHR found'%(self.CHR))
        flag_6 = int(header[6])
        #print('Flag 6: %d'%(flag_6))
        flag_7 = int(header[7])
        #print('Flag 7: %d'%(flag_7))
        self.MAPPER =  (flag_6 >> 4) | (flag_7 & 0xf0)
        print('MAPPER: %d'%(self.MAPPER))
        self.MIRRORING = flag_6 & 0x01
        self.SRAM = flag_6 & 0x02
        self.TRAINER = flag_6 & 0x04
        self.FS_MIRROR = flag_6 & 0x08
        print('MIRRORING: %d'%(self.MIRRORING))
        print('SRAM: %d'%(self.SRAM))
        print('TRAINER: %d'%(self.TRAINER))
        print('FS_MIRROR: %d'%(self.FS_MIRROR))

        rom_file.close()

        return True

    def load(self, rom_file_name, mem):
        rom_file = open(rom_file_name, 'rb')
        self.romcache = rom_file.read()
        len16k = 16 * 1024
        len8k = 8 * 1024
        if self.RPG == 1:
            size = len16k
            for i in range(size):
                mem.cpu_mem[0x8000 + i] = self.romcache[16 + i]
                mem.cpu_mem[0xC000 + i] = self.romcache[16 + i]

            #mem.cpu_mem[0x8000:0x8000+size] = self.romcache[16:16+size]
            #mem.cpu_mem[0xC000:0xC000+size] = self.romcache[16:16+size]
        else:
            size = len16k
            for i in range(size):
                mem.cpu_mem[0x8000 + i] = self.romcache[16 + i]
                mem.cpu_mem[0xC000 + i] = self.romcache[16 + (self.RPG - 1) * len16k + i]
                # Reset Vector: PCL from 0xFFFC(Here is i: 0x3FFC and rom offset: 0x800C)
                #               PCH from 0xFFFD(Here is i: 0x3FFD and rom offset: 0x800D)
                #if (0xC000 + i == 0xFFFD):
                #    print('0xFFFD(i: 0x%x, rom offset: 0x%x): 0x%x'%(i, 16 + (self.RPG - 1) * len16k + i, self.romcache[16 + (self.RPG - 1) * len16k + i]))
            #mem.cpu_mem[0x8000:0x8000+size] = self.romcache[16:16+size]
            #mem.cpu_mem[0xC000:0xC000+size] = self.romcache[16+(self.RPG-1)*len16k:16+(self.RPG-1)*len16k+size]

        if self.CHR != 0:
            size = len8k
            offset = 16 + self.RPG * len16k
            for i in range(size):
                mem.ppu_mem[i] = self.romcache[offset + i]

            #offset = 16+self.RPG*len16k
            #mem.ppu_mem = self.romcache[offset:offset+len8k]
            #offset = 16+self.RPG*len16k+len8k
            #mem.tital = self.romcache[offset:offset+128]

        rom_file.close()
