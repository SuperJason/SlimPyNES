#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from rom import ROM 
from mem import MEMORY
from cpu import CPU
from ppu import PPU

import pygame
from pygame.locals import *

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
            0: self.pad1_DOWN,
            1: self.pad1_UP,
            2: self.pad1_LEFT,
            3: self.pad1_RIGHT,
            4: self.pad1_START,
            5: self.pad1_SELECT,
            6: self.pad1_A,
            7: self.pad1_B,
            }
        self.readcnt = 0

    def reset(self):
        for i in range(8):
            self.pads[i] = 0x40


class DISPLAY():
    class PALETTE():
        def __init__(self, r=0, g=0, b=0):
            self.r = r
            self.g = g
            self.b = b
    palette = [
                PALETTE(0x80,0x80,0x80),PALETTE(0x00,0x3D,0xA6),PALETTE(0x00,0x12,0xB0),PALETTE(0x44,0x00,0x96),
                PALETTE(0xA1,0x00,0x5E),PALETTE(0xC7,0x00,0x28),PALETTE(0xBA,0x06,0x00),PALETTE(0x8C,0x17,0x00),
                PALETTE(0x5C,0x2F,0x00),PALETTE(0x10,0x45,0x00),PALETTE(0x05,0x4A,0x00),PALETTE(0x00,0x47,0x2E),
                PALETTE(0x00,0x41,0x66),PALETTE(0x00,0x00,0x00),PALETTE(0x05,0x05,0x05),PALETTE(0x05,0x05,0x05),
                PALETTE(0xC7,0xC7,0xC7),PALETTE(0x00,0x77,0xFF),PALETTE(0x21,0x55,0xFF),PALETTE(0x82,0x37,0xFA),
                PALETTE(0xEB,0x2F,0xB5),PALETTE(0xFF,0x29,0x50),PALETTE(0xFF,0x22,0x00),PALETTE(0xD6,0x32,0x00),
                PALETTE(0xC4,0x62,0x00),PALETTE(0x35,0x80,0x00),PALETTE(0x05,0x8F,0x00),PALETTE(0x00,0x8A,0x55),
                PALETTE(0x00,0x99,0xCC),PALETTE(0x21,0x21,0x21),PALETTE(0x09,0x09,0x09),PALETTE(0x09,0x09,0x09),
                PALETTE(0xFF,0xFF,0xFF),PALETTE(0x0F,0xD7,0xFF),PALETTE(0x69,0xA2,0xFF),PALETTE(0xD4,0x80,0xFF),
                PALETTE(0xFF,0x45,0xF3),PALETTE(0xFF,0x61,0x8B),PALETTE(0xFF,0x88,0x33),PALETTE(0xFF,0x9C,0x12),
                PALETTE(0xFA,0xBC,0x20),PALETTE(0x9F,0xE3,0x0E),PALETTE(0x2B,0xF0,0x35),PALETTE(0x0C,0xF0,0xA4),
                PALETTE(0x05,0xFB,0xFF),PALETTE(0x5E,0x5E,0x5E),PALETTE(0x0D,0x0D,0x0D),PALETTE(0x0D,0x0D,0x0D),
                PALETTE(0xFF,0xFF,0xFF),PALETTE(0xA6,0xFC,0xFF),PALETTE(0xB3,0xEC,0xFF),PALETTE(0xDA,0xAB,0xEB),
                PALETTE(0xFF,0xA8,0xF9),PALETTE(0xFF,0xAB,0xB3),PALETTE(0xFF,0xD2,0xB0),PALETTE(0xFF,0xEF,0xA6),
                PALETTE(0xFF,0xF7,0x9C),PALETTE(0xD7,0xE8,0x95),PALETTE(0xA6,0xED,0xAF),PALETTE(0xA2,0xF2,0xDA),
                PALETTE(0x99,0xFF,0xFC),PALETTE(0xDD,0xDD,0xDD),PALETTE(0x11,0x11,0x11),PALETTE(0x11,0x11,0x11)
            ]
    def __init__(self, nes):
        self.nes = nes
        self.screen = None

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.nes.width, self.nes.hight))
        pygame.display.set_caption("NES Emulater")
        self.screen.fill([0x33,0x66,0x44])
        pygame.display.update()

    def set_pixel(self, x, y, nes_color):
        if x >= self.nes.width:
            return
        if y >= self.nes.hight:
            return
        r = self.palette[nes_color].r
        g = self.palette[nes_color].g
        b = self.palette[nes_color].b
        if self.nes.debug & self.nes.DISP_DBG:
            print('[%d] --- x: %d, y: %d, nes_color: %d --- r: %x, g: %x, b: %x ---'%(self.nes.cpu.dbg_cnt, x, y, nes_color, r, g, b))
        self.screen.set_at([x, y], [r, g, b])

    def update(self):
        pygame.display.update()


class NES():
    # cpu speed
    PAL_SPEED = 1773447

    # vblank int
    PAL_VBLANK_INT = PAL_SPEED / 50

    # scanline refresh (hblank)
    PAL_SCANLINE_REFRESH = PAL_VBLANK_INT / 313

    # vblank int cycle timeout
    PAL_VBLANK_CYCLE_TIMEOUT = (313 - 240) * PAL_VBLANK_INT / 313

    # Emulater Debug
    CPU_NMI_DBG = 0x02
    PPU_DBG = 0x10
    PPU_BG_DBG = 0x20
    PPU_SPR_DBG = 0x40
    DISP_DBG = 0x100

    def __init__(self, cpu=None, ppu=None, mem=None, rom=None, disp=None, in_put=None):
        self.cpu = cpu
        self.ppu = ppu
        self.mem = mem
        self.rom = rom
        self.disp = disp
        self.in_put = in_put
        # PAL
        self.start_init = 341
        self.vblank_init = self.PAL_VBLANK_INT
        self.vblank_cycle_timeout = self.PAL_VBLANK_CYCLE_TIMEOUT
        self.scanline_refresh = self.PAL_SCANLINE_REFRESH
        self.hight = 240
        self.width = 256

        self.enable_background = 1
        self.enable_sprites = 1

        self.fullscreen = 0
        self.scale = 1

        self.frameskip = 0
        self.skipframe = 0

        # 10 ms
        self.delay = 0.001

        self.debug = 0

    def start(self):
        counter = 0
        print(' -- NES Emulator Stating... --')

        self.cpu_is_running = 1
        while(self.cpu_is_running):
            print('[%d] -- NES CPU Loop Start -- '%(self.cpu.dbg_cnt))
            self.cpu.execute(self.start_init)

            # Set ppu status bit7 to 1 and enter vblank
            self.ppu.status = 0x80
            self.mem.cpu_mem[0x2002] = self.ppu.status
            counter += self.cpu.execute(12)

            #print('debug [%d] --- entering VBLANK! ---'%(self.cpu.dbg_cnt))
            if self.ppu.exec_nmi_on_vblank():
                if self.debug & self.CPU_NMI_DBG:
                    print('[%d] vblank = on'%(self.cpu.dbg_cnt))
                counter += self.cpu.nmi(counter);

            counter += self.cpu.execute(self.vblank_cycle_timeout)

            # vblank ends (ppu status bit7) is set to 0, sprite_zero (ppu status bit6) is set to 0
            self.ppu.status &= 0x3f

            # and write to mem
            self.mem.write(0x2002, self.ppu.status)

            self.ppu.loopyV = self.ppu.loopyT

            if self.skipframe > self.frameskip:
                self.skipframe = 0

            for scanline in range(240):
                if not self.ppu.sprite_zero():
                    self.ppu.check_sprite_hit(scanline)

                self.ppu.render_background(scanline)

                counter += self.cpu.execute(self.scanline_refresh)

            self.ppu.render_sprites()

            if self.skipframe == 0:
                self.disp.update()

            self.skipframe += 1

            #time.sleep(self.delay)

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

    disp = DISPLAY(nes)
    nes.disp = disp
    disp.init()

    in_put = INPUT(nes)
    nes.in_put = in_put
    in_put.reset()

    nes.start()
