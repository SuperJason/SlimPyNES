#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class PPU():
    def __init__(self, mem):
        self.mem = mem

        self.status = 0
        self.status_tmp = 0

        # used to flip between first and second write (0x2005)
        self.bgscr_f = 0

        # used to flip between first and second write (0x2006)
        self.addr_h = 0

        self.addr = 0x2000
        self.addr_tmp = 0x2000

        # ppu control registers
        self.control_1 = 0
        self.control_2 = 0

        # used for scrolling techniques
        self.loopyT = 0
        self.loopyV = 0
        self.loopyX = 0

        self.sprite_address = 0

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

    # memory[0x2001]
    def sprite_on(self):
        return self.control_2 & 0x10 # 1 = Show sprite
    def background_on(self):
        return self.control_2 & 0x08 # 1 = Show background
    def sprite_clipping_off(self):
        return self.control_2 & 0x04 # 1 = No clipping
    def background_clipping_off(self):
        return self.control_2 & 0x02 # 1 = No clipping
    def monochrome_on(self):
        return self.control_2 & 0x01 # 1 = Display monochrome

    # memory[0x2002]
    def vblank_on(self):
        return self.status & 0x80 # 1 = In VBlank
    def sprite_zero(self):
        return self.status & 0x40 # 1 = PPU has hit Sprite #0
    def scanline_sprite_count(self):
        return self.status & 0x20 # 1 = More than 8 sprites on current scanline
    def vram_write_flag(self):
        return self.status & 0x10 # 1 = Writes to VRAM are ignored

    def reset(self):
        print(' -- PPU Reset --')

