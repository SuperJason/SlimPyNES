#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from rom import ROM 
from mem import MEMORY
from cpu import CPU

if __name__ == '__main__':
    if len(sys.argv) > 1:
        rom_file_name = sys.argv[1]
    else:
        rom_file_name= 'supermario.nes'

    rom = ROM()
    if rom.headercheck(rom_file_name) != True:
        exit()

    mem = MEMORY()
    rom.load(rom_file_name, mem)

    cpu = CPU(mem)
    cpu.reset()
    print(' -- NES Emulator Stating... --')

    cpu_is_running = 1
    while(cpu_is_running):
        cpu.execute(10)
        time.sleep(0.01)
        #cpu_is_running -= 1
