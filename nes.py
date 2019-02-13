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
        self.status_tmp = 0

        # used to flip between first and second write (0x2005)
        self.bgscr_f = 0

        # used to flip between first and second write (0x2006)
        self.ppu_addr_h = 0

        self.addr = 0x2000
        self.addr_tmp = 0x2000

        # ppu control registers
        self.control_1 = 0
        self.control_2 = 0

        # used for scrolling techniques
        self.loopyT = 0
        self.loopyV = 0
        self.loopyX = 0

    # memory[0x2000]
    def exec_nmi_on_vblank(self):
        return self.control_1 & 0x80 # 1 = Generate VBlank NMI
    def sprite_16(self):
        return self.control_1 & 0x20 # 1 = Sprites 8x16/8x8
    def background_addr_hi(self):
        return self.control_1 & 0x10 # 1 = BG pattern adr $0000/$1000
    def sprite_addr_hi(self):
        return self.control_1 & 0x08 # 1 = Sprite pattern adr $0000/$1000
    def increment_32(self):
        return self.control_1 & 0x04 # 1 = auto increment 1/32

    def reset(self):
        print(' -- PPU Reset --')

class INPUT():
    def __init__(self, nes):
        self.nes = nes
        self.pad1_DOWN = 0x40
        self.pad1_UP = 0x40
        self.pad1_LEFT = 0x40
        self.pad1_RIGHT = 0x40
        self.pad1_START = 0x40
        self.pad1_SELECT = 0x40
        self.pad1_A = 0x40
        self.pad1_B = 0x40
        self.pads = {
            1: self.pad1_DOWN,
            2: self.pad1_UP,
            3: self.pad1_LEFT,
            4: self.pad1_RIGHT,
            5: self.pad1_START,
            6: self.pad1_SELECT,
            7: self.pad1_A,
            8: self.pad1_B,
            }
        self.readcnt = 0

    def reset(self):
        for i in range(1, 8):
            self.pads[i] = 0x40

class NES():
    # cpu speed
    PAL_SPEED = 1773447

    # vblank int
    PAL_VBLANK_INT = PAL_SPEED / 50

    # scanline refresh (hblank)
    PAL_SCANLINE_REFRESH = PAL_VBLANK_INT / 313

    # vblank int cycle timeout
    PAL_VBLANK_CYCLE_TIMEOUT = (313 - 240) * PAL_VBLANK_INT / 313

    def __init__(self, cpu=None, ppu=None, mem=None, rom=None, in_put=None):
        self.cpu = cpu
        self.ppu = ppu
        self.mem = mem
        self.rom = rom
        self.in_put = in_put
        # PAL
        self.start_init = 341
        self.vblank_init = self.PAL_VBLANK_INT
        self.vblank_cycle_timeout = self.PAL_VBLANK_CYCLE_TIMEOUT
        self.scanline_refresh = self.PAL_SCANLINE_REFRESH

    def start(self):
        counter = 0
        print(' -- NES Emulator Stating... --')

        self.cpu_is_running = 1
        while(self.cpu_is_running):
            print(' -- NES CPU Loop Start --')
            cpu.execute(nes.start_init)
            # Set ppu status bit7 to 1 and enter vblank
            ppu.status = 0x80
            mem.cpu_mem[0x2002] = ppu.status
            counter += cpu.execute(12)
            #self.cpu_is_running -= 1
            if self.ppu.exec_nmi_on_vblank():
                counter += cpu.nmi(counter);

            counter += cpu.execute(self.vblank_cycle_timeout)

            # vblank ends (ppu status bit7) is set to 0, sprite_zero (ppu status bit6) is set to 0
            ppu.status &= 0x3f

            # and write to mem
            mem.write(0x2002, ppu.status)

            ppu.loopyV = ppu.loopyT

            for scanline in range(0, 240):
                counter += cpu.execute(self.scanline_refresh)

            time.sleep(0.01)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        rom_file_name = sys.argv[1]
    else:
        rom_file_name= 'supermario.nes'

    nes = NES()
    rom = ROM(nes)
    if rom.headercheck(rom_file_name) != True:
        exit()
    nes.rom = rom

    mem = MEMORY(nes)
    rom.load(rom_file_name, mem)
    nes.mem = mem

    cpu = CPU(nes)
    nes.cpu = cpu
    cpu.reset()

    ppu = PPU(nes)
    nes.ppu = ppu
    ppu.reset()

    in_put = INPUT(nes)
    nes.in_put = in_put
    in_put.reset()

    nes.start()
