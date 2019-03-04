#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import sys

class PPU():
    def __init__(self, nes):
        self.mem = nes.mem
        self.nes = nes

        # gfx cache -> [hor] [ver]
        self.bgcache = np.zeros((256 + 8) * (256 + 8), dtype=np.uint8).reshape(256 + 8, 256 + 8)
        self.sprcache = np.zeros((256 + 8) * (256 + 8), dtype=np.uint8).reshape(256 + 8, 256 + 8)

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

        # used to export the current scanline for the debugger
        self.current_scanline = 0

        self.scale = 1

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

    def render_background(self, scanline):
        bit1 = np.zeros(8, np.uint8)
        bit2 = np.zeros(8, np.uint8)
        tile = np.zeros(8, np.uint8)

        self.current_scanline = scanline

        if self.nes.debug & self.nes.PPU_BG_DBG:
            print('[%d] --- start scanline: %d (%x) ---'%(self.nes.cpu.dbg_cnt, scanline, scanline))

        # loopy scanline start -> v:0000010000011111=t:0000010000011111 | v=t
        self.loopyV &= 0xfbe0
        self.loopyV |= (self.loopyT & 0x041f)

        x_scroll = (self.loopyV & 0x1f)
        y_scroll = (self.loopyV & 0x03e0) >> 5

        nt_addr = 0x2000 + (self.loopyV & 0x0fff)
        at_addr = 0x2000 + (self.loopyV & 0x0c00) + 0x03c0 + ((y_scroll & 0xfffc) << 1) + (x_scroll >> 2)

        if (y_scroll & 0x0002) == 0:
            if (x_scroll & 0x0002) == 0:
                attribs = (self.nes.mem.ppu_mem[at_addr] & 0x03) << 2
            else:
                attribs = (self.nes.mem.ppu_mem[at_addr] & 0x0C)
        else:
            if (x_scroll & 0x0002) == 0:
                attribs = (self.nes.mem.ppu_mem[at_addr] & 0x30) >> 2
            else:
                attribs = (self.nes.mem.ppu_mem[at_addr] & 0xC0) >> 4

        if False: #self.nes.cpu.dbg_cnt == 370815:
            print('[%d] nt_addr: %x, loopyT: %x, loopyV: %x, loopyX: %x'%(self.nes.cpu.dbg_cnt, nt_addr, self.loopyT, self.loopyV, self.loopyX))
            print('[%d] y_scroll: %x, x_scroll: %x, mem[%x]: %x, attribs: %x'%(self.nes.cpu.dbg_cnt, y_scroll, x_scroll, at_addr, self.nes.mem.ppu_mem[at_addr], attribs))

        # draw 33 tiles in a scanline (32 + 1 for scrolling)
        for tile_count in range(33):
            # nt_data (ppu_memory[nt_addr]) * 16 = pattern table address
            pt_addr = (self.nes.mem.ppu_mem[nt_addr] << 4) + ((self.loopyV & 0x7000) >> 12)
            #print('### DBG ### ppu_mem[%x]: %x, pt_addr: %d'%(nt_addr, self.nes.mem.ppu_mem[nt_addr], pt_addr))

            # check if the pattern address needs to be high
            if self.background_addr_hi():
                pt_addr += 0x1000

            # fetch bits from pattern table
            for i in range(8)[::-1]:
                bit1[7 - i] = bool((self.nes.mem.ppu_mem[pt_addr] >> i) & 0x01)
                bit2[7 - i] = bool((self.nes.mem.ppu_mem[pt_addr + 8] >> i) & 0x01)
                #print(' ### DBG ### ppu_mem[%x]: %x, ppu_mem[%x]: %x, bit1[%d]: %d, bit2[%d]: %d'%(pt_addr, self.nes.mem.ppu_mem[pt_addr], pt_addr + 8, self.nes.mem.ppu_mem[pt_addr + 8], 7 - i, bit1[7 - i], 7 - i, bit2[7 - i]))

            # merge bits
            for i in range(8):
                if (bit1[i] == 0) and (bit2[i] == 0):
                    tile[i] = 0
                elif (bit1[i] == 1) and (bit2[i] == 0):
                    tile[i] = 1
                elif (bit1[i] == 0) and (bit2[i] == 1):
                    tile[i] = 2
                elif (bit1[i] == 1) and (bit2[i] == 1):
                    tile[i] = 3

            if False: #self.nes.cpu.dbg_cnt == 370815:
                print(' ### DBG ### %s(), tile_count: %d, attribs: %x, tile: %x, %x, %x, %x, %x, %x, %x, %x'%(
                        sys._getframe().f_code.co_name,
                        tile_count,
                        attribs,
                        tile[0],
                        tile[1],
                        tile[2],
                        tile[3],
                        tile[4],
                        tile[5],
                        tile[6],
                        tile[7]))
            # merge colour
            for i in range(8)[::-1]:
                # pixel transparency check
                if tile[7 - i] != 0:
                    tile[7 -i] += attribs

            if (tile_count == 0) and (self.loopyX != 0):
                for i in range(8 - self.loopyX):
                    # cache pixel
                    self.bgcache[(tile_count << 3) + i][scanline] = tile[self.loopyX + i]

                    # draw pixel
                    if (self.nes.enable_background == 1) and (self.background_on()) and (self.nes.skipframe == 0):
                        if self.scale > 1:
                            for s_y in range(scale):
                                for s_x in range(scale):
                                    disp_x = ((tile_count << 3) + i) * self.scale + s_x
                                    disp_y = scanline * self.scale + s_y
                                    disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[self.loopyX + i])]
                                    self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                        else:
                            disp_x = (tile_count << 3) + i
                            disp_y = scanline
                            disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[self.loopyX + i])]
                            self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
            elif (tile_count == 32) and (self.loopyX != 0):
                for i in range(self.loopyX):
                    # cache pixel
                    self.bgcache[(tile_count << 3) + i - self.loopyX][scanline] = tile[i]

                    # draw pixel
                    if (self.nes.enable_background == 1) and (self.background_on()) and (self.nes.skipframe == 0):
                        if self.scale > 1:
                            for s_y in range(scale):
                                for s_x in range(scale):
                                    disp_x = ((tile_count << 3) + i - self.loopyX) * self.scale + s_x
                                    disp_y = scanline * self.scale + s_y
                                    disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[i])]
                                    self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                        else:
                            disp_x = (tile_count << 3) + i - self.loopyX
                            disp_y = scanline
                            disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[self.loopyX + i])]
                            self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
            else:
                for i in range(8):
                    # cache pixel
                    self.bgcache[(tile_count << 3) + i - self.loopyX][scanline] = tile[i]

                    # draw pixel
                    if (self.nes.enable_background == 1) and (self.background_on()) and (self.nes.skipframe == 0):
                        if self.scale > 1:
                            for s_y in range(scale):
                                for s_x in range(scale):
                                    disp_x = ((tile_count << 3) + i - self.loopyX) * self.scale + s_x
                                    disp_y = scanline * self.scale + s_y
                                    disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[i])]
                                    self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                        else:
                            if False: #self.nes.cpu.dbg_cnt == 370815:
                                print(' ### DBG ### %s(), tile_count: %d, loopyX: %d, scanline: %d, tile[%d]: %x'%(sys._getframe().f_code.co_name, tile_count, self.loopyX, scanline, i, tile[i]))
                            disp_x = (tile_count << 3) + i - self.loopyX
                            disp_y = scanline
                            disp_color = self.nes.mem.ppu_mem[0x3f00 + (tile[i])]
                            #print('### DBG ### disp_x: %d'%(disp_x))
                            self.nes.disp.set_pixel(disp_x, disp_y, disp_color)

            nt_addr += 1
            x_scroll += 1

            # boundary check
            # dual-tile
            if (x_scroll & 0x0001) == 0:
                # quad-tile
                if (x_scroll & 0x0003) == 0:
                    # check if we crossed a nametable
                    if (x_scroll & 0x1f) == 0:
                        # switch name/attrib tables
                        nt_addr ^= 0x0400
                        at_addr ^= 0x0400
                        nt_addr -= 0x0020
                        at_addr -= 0x0008
                        x_scroll -= 0x0020
                    at_addr += 1

                if (y_scroll & 0x0002) == 0:
                    if (x_scroll & 0x0002) == 0:
                        attribs = (self.nes.mem.ppu_mem[at_addr] & 0x03) << 2
                    else:
                        attribs = (self.nes.mem.ppu_mem[at_addr] & 0x0C)
                else:
                    if (x_scroll & 0x0002) == 0:
                        attribs = (self.nes.mem.ppu_mem[at_addr] & 0x30) >> 2
                    else:
                        attribs = (self.nes.mem.ppu_mem[at_addr] & 0xC0) >> 4

        # subtile y_offset == 7
        if (self.loopyV & 0x7000) == 0x7000:
            # subtile y_offset = 0
            self.loopyV &= 0x8fff

            # nametable line == 29
            if (self.loopyV & 0x03e0) == 0x03a0:
                # switch nametables (bit 11)
                self.loopyV ^= 0x0800

                # name table line = 0
                self.loopyV &= 0xfc1f
            else:
                # nametable line == 31
                if (self.loopyV & 0x03e0) == 0x03e0:
                    # name table line = 0
                    self.loopyV &= 0xfc1f
                else:
                    self.loopyV += 0x0020
        else:
            # next subtile y_offset
            self.loopyV += 0x1000

    def check_sprite_hit(self, scanline):
        # sprite zero detection
        # print(' ### DBG ### check_sprite_hit: scanline: %d'%(scanline))
        for i in range(self.nes.width):
            # print(' ### DBG ### bgcache[%d][%d] = 0x%x, sprcache[%d][%d] = 0x%x'%(i, scanline - 1, self.bgcache[i][scanline - 1], i, scanline - 1, self.sprcache[i][scanline - 1]))
            if (self.bgcache[i][scanline - 1] > 0) and (self.sprcache[i][scanline - 1] > 0):
                # set the sprite zero flag
                if self.nes.debug & self.nes.PPU_SPR_DBG:
                    print('debug [%d]: sprite zero found at x:%d, y:%d'%(self.nes.cpu.dbg_cnt, i, scanline - 1))
                self.status |= 0x40

    def render_sprite(self, y, x, pattern_num, attribs, spr_nr):
        if self.nes.debug & self.nes.PPU_SPR_DBG:
            print('[%d] (spritedebug [%d]): hor = %x, ver = %x, pattern_number = %d, attribs = %d'%(self.nes.cpu.dbg_cnt, spr_nr, x, y, pattern_num, attribs))
        color_bit1 = bool(attribs & 0x01)
        color_bit2 = bool(attribs & 0x02)
        disp_spr_back = bool(attribs & 0x20)
        flip_spr_hor = bool(attribs & 0x40)
        flip_spr_ver = bool(attribs & 0x80)

        bit1 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
        bit2 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
        sprite = np.zeros(8 * 16, np.uint8).reshape(8, 16)
        if self.nes.debug & self.nes.PPU_SPR_DBG:
            print('[%d] (spritedebug [%d]): attribs [%x] -> color_bit1 [%x] -> color_bit2 [%x] -> disp_spr_back [%d] -> flip_spr_hor [%d] -> flip_spr_ver [%d]'%(self.nes.cpu.dbg_cnt, spr_nr, attribs, color_bit1, color_bit2, disp_spr_back, flip_spr_hor, flip_spr_ver))

        if not self.sprite_addr_hi():
            sprite_pattern_table = 0x0000
        else:
            sprite_pattern_table = 0x1000

	    # pattern_number * 16
        spr_start = sprite_pattern_table + ((pattern_num << 3) << 1)
        if self.nes.debug & self.nes.PPU_SPR_DBG:
            print('[%d] (spritedebug [%d]): pattern_number = %d [hex %x], sprite_patterntable start addr = %x, ppu mem value = %x'%(self.nes.cpu.dbg_cnt, spr_nr, pattern_num, pattern_num, sprite_pattern_table + (pattern_num * 16), self.nes.mem.ppu_mem[sprite_pattern_table + (pattern_num * 16)]))

        #for i in range(8):
        #    print('### DBG ### spr_start: %d, memory[%d] = 0x%x, memory[%d] = 0x%x'%(spr_start, spr_start + i, self.nes.mem.ppu_mem[spr_start + i], spr_start + 8 + i, self.nes.mem.ppu_mem[spr_start + 8 + i]))
        if not self.sprite_16():
            # 8 x 8 sprites
            # fetch bits
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(8):
                        bit1[7 - i][j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[7 - i][j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8):
                    for j in range(8):
                        bit1[i][j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[i][j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(8)[::-1]:
                        bit1[7 - i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[7 - i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8):
                    for j in range(8)[::-1]:
                        bit1[i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)

            # merge bits
            for i in range(8):
                for j in range(8):
                    if (bit1[i][j] == 0) and (bit2[i][j] == 0):
                        sprite[i][j] = 0
                    elif (bit1[i][j] == 1) and (bit2[i][j] == 0):
                        sprite[i][j] = 1
                    elif (bit1[i][j] == 0) and (bit2[i][j] == 1):
                        sprite[i][j] = 2
                    elif (bit1[i][j] == 1) and (bit2[i][j] == 1):
                        sprite[i][j] = 3
                    #print('### DBG ### sprite[%d][%d] = 0x%x'%(i, j, sprite[i][j]))

            # add sprite attribute colors
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(8):
                        if sprite[7 - i][j] != 0:
                            sprite[7 - i][j] += ((attribs & 0x03) << 2)
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8):
                    for j in range(8):
                        if sprite[i][j] != 0:
                            sprite[i][j] += ((attribs & 0x03) << 2)
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(8)[::-1]:
                        if sprite[7 - i][7 - j] != 0:
                            sprite[7 - i][7 - j] += ((attribs & 0x03) << 2)
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8):
                    for j in range(8)[::-1]:
                        if sprite[i][7 - j] != 0:
                            sprite[i][7 - j] += ((attribs & 0x03) << 2)

            for i in range(8):
                for j in range(8):
                    # cache pixel for sprite zero detection
                    if spr_nr == 0:
                        self.sprcache[x + i][y + j] = sprite[i][j]
                        #print(' ### DBG ### %s(): %d, sprcache[%d][%d] = 0x%x, i: %d, j: %d, x: %d, y: %d'%(sys._getframe().f_code.co_name, sys._getframe().f_lineno, x + i, y + j, self.sprcache[x + i][y + j], i, j ,x, y))

                    if sprite[i][j] != 0:
                        # sprite priority check
                        if not disp_spr_back:
                            if (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                                # draw pixel
                                if self.scale > 1:
                                    for s_y in range(scale):
                                        for s_x in range(scale):
                                            disp_x = (x + i) * self.scale + s_x
                                            disp_y = (y + j) * self.scale + s_y
                                            disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                            self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                                else:
                                    disp_x = x + i
                                    disp_y = y + j
                                    disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                    #print('---s 88 10 --- i: %d, j: %d, disp_x: %d'%(i, j, disp_x))
                                    self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                        else:
                            if (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                                # draw the sprite pixel if the background pixel is transparent (0)
                                if self.bgcache[x + i][y + j] == 0:
                                    # draw pixel
                                    if self.scale > 1:
                                        for s_y in range(scale):
                                            for s_x in range(scale):
                                                disp_x = (x + i) * self.scale + s_x
                                                disp_y = (y + j) * self.scale + s_y
                                                disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                                self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                                    else:
                                        disp_x = x + i
                                        disp_y = y + j
                                        disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                        #print('---s 88 11 --- i: %d, j: %d, disp_x: %d'%(i, j, disp_x))
                                        self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
        else:
            # 8 x 16 sprites
            # fetch bits
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(16):
                        bit1[7 - i][j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[7 - i][j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8):
                    for j in range(16):
                        bit1[i][j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[i][j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(16)[::-1]:
                        bit1[7 - i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[7 - i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8):
                    for j in range(16)[::-1]:
                        bit1[i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + j] >> i) & 0x01)
                        bit2[i][7 - j] = bool((self.nes.mem.ppu_mem[spr_start + 8 + j] >> i) & 0x01)

            # merge bits
            for i in range(8):
                for j in range(16):
                    if (bit1[i][j] == 0) and (bit2[i][j] == 0):
                        sprite[i][j] = 0
                    elif (bit1[i][j] == 1) and (bit2[i][j] == 0):
                        sprite[i][j] = 1
                    elif (bit1[i][j] == 0) and (bit2[i][j] == 1):
                        sprite[i][j] = 2
                    elif (bit1[i][j] == 1) and (bit2[i][j] == 1):
                        sprite[i][j] = 3

            # add sprite attribute colors
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(16):
                        if sprite[7 - i][j] != 0:
                            sprite[7 - i][j] += ((attribs & 0x03) << 2)
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                for i in range(8):
                    for j in range(16):
                        if sprite[i][j] != 0:
                            sprite[i][j] += ((attribs & 0x03) << 2)
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8)[::-1]:
                    for j in range(16)[::-1]:
                        if sprite[7 - i][15 - j] != 0:
                            sprite[7 - i][15 - j] += ((attribs & 0x03) << 2)
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                for i in range(8):
                    for j in range(16)[::-1]:
                        if sprite[i][15 - j] != 0:
                            sprite[i][15 - j] += ((attribs & 0x03) << 2)

            for i in range(8):
                for j in range(16):
                    # cache pixel for sprite zero detection
                    if spr_nr == 0:
                        self.sprcache[x + i][y + j] = sprite[i][j]
                        #print(' ### DBG ### %s(): %d, sprcache[%d][%d] = 0x%x, i: %d, j: %d, x: %d, y: %d'%(sys._getframe().f_code.co_name, sys._getframe().f_lineno, x + i, y + j, self.sprcache[x + i][y + j], i, j ,x, y))

                    if sprite[i][j] != 0:
                        # sprite priority check
                        if not disp_spr_back:
                            if (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                                # draw pixel
                                if self.scale > 1:
                                    for s_y in range(scale):
                                        for s_x in range(scale):
                                            disp_x = (x + i) * self.scale + s_x
                                            disp_y = (y + j) * self.scale + s_y
                                            disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                            self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                                else:
                                    disp_x = x + i
                                    disp_y = y + j
                                    disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                    #print('---s 816 10 --- i: %d, j: %d, disp_x: %d'%(i, j, disp_x))
                                    self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                        else:
                            # draw the sprite pixel if the background pixel is transparent (0)
                            if self.bgcache[x + i][y + j] == 0:
                                if (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                                    # draw pixel
                                    if self.scale > 1:
                                        for s_y in range(scale):
                                            for s_x in range(scale):
                                                disp_x = (x + i) * self.scale + s_x
                                                disp_y = (y + j) * self.scale + s_y
                                                disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                                self.nes.disp.set_pixel(disp_x, disp_y, disp_color)
                                    else:
                                        disp_x = x + i
                                        disp_y = y + j
                                        disp_color = self.nes.mem.ppu_mem[0x3f10 + (sprite[i][j])]
                                        #print('---s 816 11 --- i: %d, j: %d, disp_x: %d'%(i, j, disp_x))
                                        self.nes.disp.set_pixel(disp_x, disp_y, disp_color)


    def render_sprites(self):
        # clear sprite cache
        self.sprcache[:][:] = 0
        # fetch all 64 sprites out of the sprite memory 4 bytes at a time and render the sprite
        # sprites are drawn in priority from sprite 64 to 0
        for i in range(64)[::-1]:
            y = self.nes.mem.sprite_mem[i * 4]
            x = self.nes.mem.sprite_mem[i * 4 + 3]
            pattern_num = self.nes.mem.sprite_mem[i * 4 + 1]
            attribs = self.nes.mem.sprite_mem[i * 4 + 2]
            self.render_sprite(y, x, pattern_num, attribs, i)
