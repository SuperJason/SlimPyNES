#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from cpu import CPU, cpu_execute, cpu_reset
from rom import ROM, rom_headercheck, rom_load
from mem import cpu_mem, ppu_mem, mem_read, mem_write

start_init = 341

def nes_start(cpu):
    counter = 0
    print(' -- NES Emulator Stating... --')
    cpu_is_running = 1000
    while(cpu_is_running):
        print(' -- cpu_is_running: %d --'%(cpu_is_running))
        cpu_execute(cpu, start_init)
        cpu_is_running -= 1

if __name__ == '__main__':
    rom_file_name= '../supermario.nes'

    cpu = CPU()
    rom = ROM()
    if rom_headercheck(rom, rom_file_name) != True:
        exit()

    print('MIRRORING: %d'%(rom.MIRRORING))
    rom_load(rom, rom_file_name, cpu_mem, ppu_mem)

    cpu_reset(cpu)
    nes_start(cpu)
