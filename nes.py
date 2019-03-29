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
from pygame import surfarray

import numpy as np

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
        self.pads = np.ones(8, dtype=np.uint8) * 0x40
        self.PADS = {
                0: "pad1_A",
                1: "pad1_B",
                2: "pad1_SELECT",
                3: "pad1_START",
                4: "pad1_UP",
                5: "pad1_DOWN",
                6: "pad1_LEFT",
                7: "pad1_RIGHT",
                }
        self.readcnt = 0

    def bottons(self):
        self.nes.disp.getevent()
        for i in range(8):
            if self.pads[i] == 0x01:
                print(' -- ' + self.PADS[i] + ' pressed')

    def reset(self):
        for i in range(8):
            self.pads[i] = 0x40


class DISPLAY():
    palette = np.array([
                [0x80,0x80,0x80],[0x00,0x3D,0xA6],[0x00,0x12,0xB0],[0x44,0x00,0x96],
                [0xA1,0x00,0x5E],[0xC7,0x00,0x28],[0xBA,0x06,0x00],[0x8C,0x17,0x00],
                [0x5C,0x2F,0x00],[0x10,0x45,0x00],[0x05,0x4A,0x00],[0x00,0x47,0x2E],
                [0x00,0x41,0x66],[0x00,0x00,0x00],[0x05,0x05,0x05],[0x05,0x05,0x05],
                [0xC7,0xC7,0xC7],[0x00,0x77,0xFF],[0x21,0x55,0xFF],[0x82,0x37,0xFA],
                [0xEB,0x2F,0xB5],[0xFF,0x29,0x50],[0xFF,0x22,0x00],[0xD6,0x32,0x00],
                [0xC4,0x62,0x00],[0x35,0x80,0x00],[0x05,0x8F,0x00],[0x00,0x8A,0x55],
                [0x00,0x99,0xCC],[0x21,0x21,0x21],[0x09,0x09,0x09],[0x09,0x09,0x09],
                [0xFF,0xFF,0xFF],[0x0F,0xD7,0xFF],[0x69,0xA2,0xFF],[0xD4,0x80,0xFF],
                [0xFF,0x45,0xF3],[0xFF,0x61,0x8B],[0xFF,0x88,0x33],[0xFF,0x9C,0x12],
                [0xFA,0xBC,0x20],[0x9F,0xE3,0x0E],[0x2B,0xF0,0x35],[0x0C,0xF0,0xA4],
                [0x05,0xFB,0xFF],[0x5E,0x5E,0x5E],[0x0D,0x0D,0x0D],[0x0D,0x0D,0x0D],
                [0xFF,0xFF,0xFF],[0xA6,0xFC,0xFF],[0xB3,0xEC,0xFF],[0xDA,0xAB,0xEB],
                [0xFF,0xA8,0xF9],[0xFF,0xAB,0xB3],[0xFF,0xD2,0xB0],[0xFF,0xEF,0xA6],
                [0xFF,0xF7,0x9C],[0xD7,0xE8,0x95],[0xA6,0xED,0xAF],[0xA2,0xF2,0xDA],
                [0x99,0xFF,0xFC],[0xDD,0xDD,0xDD],[0x11,0x11,0x11],[0x11,0x11,0x11]
            ], np.uint8)
    def __init__(self, nes):
        self.nes = nes
        self.screen = None
        self.pixels = np.zeros((self.nes.width + 8, self.nes.hight + 16), dtype=np.uint8)

    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.nes.width, self.nes.hight))
        pygame.display.set_caption("NES Emulater")
        self.screen.fill([0x33,0x66,0x44])
        pygame.display.update()

    def update(self):
        self.surf = self.palette[self.pixels[0:self.nes.width, 0:self.nes.hight]]
        surfarray.blit_array(self.screen, self.surf)
        pygame.display.flip()

    def getevent(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                print('QUIT event, so exit! ###')
                exit()
            if event.type == pygame.KEYDOWN:
                #print(' -----  DOWN event.key' + str(event.key))
                if event.key == pygame.K_ESCAPE:
                    print(' ### K_ESCAPE is pressed, so exit! ###')
                    exit()
                if event.key == pygame.K_j:
                    self.nes.in_put.pad1_A = 0x01
                    self.nes.in_put.pads[0]= 0x01
                if event.key == pygame.K_k:
                    self.nes.in_put.pad1_B = 0x01
                    self.nes.in_put.pads[1]= 0x01
                if event.key == pygame.K_z:
                    self.nes.in_put.pad1_SELECT = 0x01
                    self.nes.in_put.pads[2]= 0x01
                if event.key == pygame.K_x:
                    self.nes.in_put.pad1_START = 0x01
                    self.nes.in_put.pads[3]= 0x01
                if event.key == pygame.K_w:
                    self.nes.in_put.pad1_UP = 0x01
                    self.nes.in_put.pads[4]= 0x01
                if event.key == pygame.K_s:
                    self.nes.in_put.pad1_DOWN = 0x01
                    self.nes.in_put.pads[5]= 0x01
                if event.key == pygame.K_a:
                    self.nes.in_put.pad1_LEFT = 0x01
                    self.nes.in_put.pads[6]= 0x01
                if event.key == pygame.K_d:
                    self.nes.in_put.pad1_RIGHT = 0x01
                    self.nes.in_put.pads[7]= 0x01
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_j:
                    self.nes.in_put.pad1_A = 0x40
                    self.nes.in_put.pads[0]= 0x40
                if event.key == pygame.K_k:
                    self.nes.in_put.pad1_B = 0x40
                    self.nes.in_put.pads[1]= 0x40
                if event.key == pygame.K_z:
                    self.nes.in_put.pad1_SELECT = 0x40
                    self.nes.in_put.pads[2]= 0x40
                if event.key == pygame.K_x:
                    self.nes.in_put.pad1_START = 0x40
                    self.nes.in_put.pads[3]= 0x40
                if event.key == pygame.K_w:
                    self.nes.in_put.pad1_UP = 0x40
                    self.nes.in_put.pads[4]= 0x40
                if event.key == pygame.K_s:
                    self.nes.in_put.pad1_DOWN = 0x40
                    self.nes.in_put.pads[5]= 0x40
                if event.key == pygame.K_a:
                    self.nes.in_put.pad1_LEFT = 0x40
                    self.nes.in_put.pads[6]= 0x40
                if event.key == pygame.K_d:
                    self.nes.in_put.pad1_RIGHT = 0x40
                    self.nes.in_put.pads[7]= 0x40

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
    NES_TIME_DBG = 0x2000

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

        self.debug = self.NES_TIME_DBG

    def start(self):
        counter = 0
        print(' -- NES Emulator Stating... --')

        self.cpu_is_running = 1
        while(self.cpu_is_running):
            if self.debug & self.NES_TIME_DBG:
                time_start = time.time()
                print('[%d] -- NES CPU Loop Start -- '%(self.cpu.dbg_cnt))
            self.cpu.execute(self.start_init)

            # Set ppu status bit7 to 1 and enter vblank
            self.ppu.status |= 0x80
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

            self.in_put.bottons()

            #time.sleep(self.delay)
            if self.debug & self.NES_TIME_DBG:
                time_now = time.time()
                print(time_now - time_start)

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
