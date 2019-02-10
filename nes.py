#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from rom import ROM 
from mem import MEMORY
from cpu import CPU

class PPU():
    def __init__(self, mem):
        self.mem = mem
        self.status = 0

    def reset(self):
        print(' -- PPU Reset --')

class NES():
    def __init__(self):
        # PAL
        self.start_init = 341

if __name__ == '__main__':
    if len(sys.argv) > 1:
        rom_file_name = sys.argv[1]
    else:
        rom_file_name= 'supermario.nes'

    nes = NES()
    rom = ROM()
    if rom.headercheck(rom_file_name) != True:
        exit()

    mem = MEMORY()
    rom.load(rom_file_name, mem)

    cpu = CPU(mem)
    cpu.reset()
    ppu = PPU(mem)
    ppu.reset()
    print(' -- NES Emulator Stating... --')

    cpu_is_running = 1
    while(cpu_is_running):
        cpu.execute(nes.start_init)
        time.sleep(0.01)
        # Set ppu status bit7 to 1 and enter vblank
        ppu.status = 0x80
        print(' -$-$-$-$-$- cpu_mem[%x]: %x -$-$-$-$-$-'%(0x2002, mem.cpu_mem[0x2002]))
        mem.cpu_mem[0x2002] = ppu.status
        print(' -#-#-#-#-#- cpu_mem[%x]: %x -#-#-#-#-#-'%(0x2002, mem.cpu_mem[0x2002]))
        cpu.execute(12)
        #cpu_is_running -= 1
