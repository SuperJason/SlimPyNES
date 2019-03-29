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

        # draw 33 tiles in a scanline (32 + 1 for scrolling)
        x_scroll_array = np.arange(33, dtype=np.uint64) + x_scroll
        x_scroll_0x1f_mask = (x_scroll_array > 31).astype(np.uint64)
        x_scroll_array -= (x_scroll_0x1f_mask * 0x0020)

        y_scroll_array = np.zeros(33, dtype=np.uint64) + y_scroll

        nt_addr_array = np.arange(33, dtype=np.uint64) + nt_addr
        nt_addr_array ^= (x_scroll_0x1f_mask * 0x0400)
        nt_addr_array -= (x_scroll_0x1f_mask * 0x0020)

        offset = x_scroll & 0x0003
        quad_list_36 = (np.ones((4,9), dtype=np.uint64) * np.arange(9, dtype=np.uint64)).T.reshape(1, 36)[0]
        at_addr_array_meta = quad_list_36[offset:offset + 33]
        at_addr_array = at_addr_array_meta + at_addr
        index_0x20 = 0x20 - x_scroll
        at_addr_array[index_0x20:] = (np.ones(33 - index_0x20, dtype=np.uint64) * at_addr_array[index_0x20 - 1]) ^ 0x0400
        at_addr_array[index_0x20:] -= 0x0008
        at_addr_array[index_0x20:] += (quad_list_36[0:33 - index_0x20] + 1)

        if self.nes.debug & self.nes.PPU_BG_DBG:
            print('[%d] nt_addr: %x, loopyT: %x, loopyV: %x, loopyX: %x'%(self.nes.cpu.dbg_cnt, nt_addr, self.loopyT, self.loopyV, self.loopyX))

        attribs_array_0 = (self.nes.mem.ppu_mem[at_addr_array] & 0x03) << 2
        attribs_array_1 = (self.nes.mem.ppu_mem[at_addr_array] & 0x0C)
        attribs_array_2 = (self.nes.mem.ppu_mem[at_addr_array] & 0x30) >> 2
        attribs_array_3 = (self.nes.mem.ppu_mem[at_addr_array] & 0xC0) >> 4

        x_scroll_0x0001_mask_tmp = ((x_scroll_array & 0x0001) == 0)
        x_scroll_0x0001_mask_tmp[0] = True
        attribs_mask_0 = (x_scroll_0x0001_mask_tmp & ((y_scroll_array & 0x0002) == 0) & ((x_scroll_array & 0x0002) == 0)).astype(np.uint64)
        attribs_mask_1 = (x_scroll_0x0001_mask_tmp & ((y_scroll_array & 0x0002) == 0) & ((x_scroll_array & 0x0002) != 0)).astype(np.uint64)
        attribs_mask_2 = (x_scroll_0x0001_mask_tmp & ((y_scroll_array & 0x0002) != 0) & ((x_scroll_array & 0x0002) == 0)).astype(np.uint64)
        attribs_mask_3 = (x_scroll_0x0001_mask_tmp & ((y_scroll_array & 0x0002) != 0) & ((x_scroll_array & 0x0002) != 0)).astype(np.uint64)
        attribs_mask_all_revert = ((attribs_mask_0 + attribs_mask_1 + attribs_mask_2 + attribs_mask_3) == 0).astype(np.uint64)

        attribs_array = attribs_array_0 * attribs_mask_0 + attribs_array_1 * attribs_mask_1
        attribs_array += attribs_array_2 * attribs_mask_2 + attribs_array_3 * attribs_mask_3

        # Jason: make sure on changes attribes keep the last value
        attribs_array[1:] += attribs_array[:-1] * attribs_mask_all_revert[1:]

        # nt_data (ppu_memory[nt_addr]) * 16 = pattern table address
        pt_addr_array = (self.nes.mem.ppu_mem[nt_addr_array].astype(np.uint64) << 4) + ((self.loopyV & 0x7000) >> 12)

        # check if the pattern address needs to be high
        if self.background_addr_hi():
            pt_addr_array += 0x1000

        bit1_array = (np.ones((33, 8)) * (1 << np.arange(8))).astype(np.uint8)
        bit1_array &= ((np.ones((33, 8)).T * self.nes.mem.ppu_mem[pt_addr_array]).T).astype(np.uint8)
        bit1_array = (bit1_array > 0) * 1
        bit1_array = bit1_array[:, ::-1]

        bit2_array = (np.ones((33, 8)) * (1 << np.arange(8))).astype(np.uint8)
        bit2_array &= ((np.ones((33, 8)).T * self.nes.mem.ppu_mem[pt_addr_array + 8]).T).astype(np.uint8)
        bit2_array = (bit2_array > 0) * 2
        bit2_array = bit2_array[:, ::-1]

        tile_array = bit1_array + bit2_array
        tile_array_tmp = (tile_array > 0) * (np.ones((33, 8)).T * attribs_array.T).astype(np.uint8).T
        tile_array = tile_array + tile_array_tmp

        tiles = tile_array.reshape(1, 33 * 8)[0]
        self.bgcache[0:32*8, scanline] = tiles[self.loopyX:32*8+self.loopyX]
        disp_color = self.nes.mem.ppu_mem[0x3f00 + tiles[self.loopyX:32*8+self.loopyX]]
        if (self.nes.enable_background == 1) and (self.background_on()) and (self.nes.skipframe == 0):
            self.nes.disp.pixels[0:32*8, scanline] = disp_color

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
        if ((np.transpose(self.bgcache)[scanline - 1] > 0) & (np.transpose(self.sprcache)[scanline - 1] > 0)).any():
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

        if not self.sprite_16():
            # 8 x 8 sprites
            # fetch bits
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(64, dtype=np.uint8).reshape(8, 8)).T
                bit1[::-1, 0:8] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[::-1, 0:8] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(64, dtype=np.uint8).reshape(8, 8)).T
                bit1[:, 0:8] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[:, 0:8] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(64, dtype=np.uint8).reshape(8, 8)).T
                bit1[::-1, 7::-1] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[::-1, 7::-1] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(64, dtype=np.uint8).reshape(8, 8)).T
                bit1[::-1, 7::-1] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[::-1, 7::-1] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2

            # merge bits
            sprite = bit1 + bit2

            # add sprite attribute colors
            tmp_sprite = ((sprite > 0) * ((attribs & 0x03) << 2)).astype(np.uint8)
            sprite[0:8, 0:8] += tmp_sprite[0:8, 0:8]

            if spr_nr == 0:
                self.sprcache[x:x+8, y:y+8] = sprite[0:8, 0:8]
            if not disp_spr_back:
                if (x < self.nes.width) and (y < self.nes.hight) and (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                    sprite_mask = np.ones((8, 8), np.uint8) - (sprite[0:8, 0:8] > 0) * 1
                    disp_color_bg = self.nes.disp.pixels[x:x+8, y:y+8]
                    disp_color_spr = self.nes.mem.ppu_mem[0x3f10 + sprite[0:8, 0:8]]
                    sprite_masked_color_base = np.ones((8, 8), np.uint8) * self.nes.mem.ppu_mem[0x3f10] * sprite_mask
                    disp_color = disp_color_bg * sprite_mask + disp_color_spr - sprite_masked_color_base
                    self.nes.disp.pixels[x:x+8, y:y+8] = disp_color
            else:
                if (x < self.nes.width) and (y < self.nes.hight) and (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                    bg_mask = np.ones((8, 8), np.uint8) - (self.bgcache[x:x+8, y:y+8] > 0) * 1
                    disp_color_bg = self.nes.disp.pixels[x:x+8, y:y+8]
                    disp_color_spr = self.nes.mem.ppu_mem[0x3f10 + sprite[0:8, 0:8]]
                    sprite_masked_color_base = np.ones((8, 8), np.uint8) * self.nes.mem.ppu_mem[0x3f10] * bg_mask
                    disp_color = disp_color_spr * bg_mask + disp_color_bg - sprite_masked_color_base
                    self.nes.disp.pixels[x:x+8, y:y+8] = disp_color
        else:
            # 8 x 16 sprites
            # fetch bits
            if not bool(flip_spr_hor) and not bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(8*16, dtype=np.uint8).reshape(8, 16)).T
                bit1[::-1, :] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[::-1, :] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif bool(flip_spr_hor) and not bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(8*16, dtype=np.uint8).reshape(8, 16)).T
                bit1[:, :] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[:, :] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif not bool(flip_spr_hor) and bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(8*16, dtype=np.uint8).reshape(8, 16)).T
                bit1[::-1, ::-1] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[::-1, ::-1] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2
            elif bool(flip_spr_hor) and bool(flip_spr_ver):
                t = ((1 << np.arange(8)) * np.ones(8*16, dtype=np.uint8).reshape(8, 16)).T
                bit1[:, ::-1] = ((t & self.nes.mem.ppu_mem[spr_start:spr_start+8]) > 0) * 1
                bit2[:, ::-1] = ((t & self.nes.mem.ppu_mem[spr_start+8:spr_start+8+8]) > 0) * 2

            # merge bits
            sprite = bit1 + bit2

            # add sprite attribute colors
            tmp_sprite = ((sprite > 0) * ((attribs & 0x03) << 2)).astype(np.uint8)
            sprite[:, :] += tmp_sprite[:, :]

            if spr_nr == 0:
                self.sprcache[x:x+8, y:y+16] = sprite[0:8, 0:16]
            if not disp_spr_back:
                if (x < self.nes.width) and (y < self.nes.hight) and (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                    sprite_mask = np.ones((8, 16), np.uint8) - (sprite[0:8, 0:16] > 0) * 1
                    disp_color_bg = self.nes.disp.pixels[x:x+8, y:y+16]
                    disp_color_spr = self.nes.mem.ppu_mem[0x3f10 + sprite[0:8, 0:16]]
                    sprite_masked_color_base = np.ones((8, 16), np.uint8) * self.nes.mem.ppu_mem[0x3f10] * sprite_mask
                    disp_color = disp_color_bg * sprite_mask + disp_color_spr - sprite_masked_color_base
                    self.nes.disp.pixels[x:x+8, y:y+16] = disp_color
            else:
                if (x < self.nes.width) and (y < self.nes.hight) and (self.nes.enable_sprites == 1) and (self.sprite_on()) and (self.nes.skipframe == 0):
                    bg_mask = np.ones((8, 16), np.uint8) - (self.bgcache[x:x+8, y:y+16] > 0) * 1
                    disp_color_bg = self.nes.disp.pixels[x:x+8, y:y+16]
                    disp_color_spr = self.nes.mem.ppu_mem[0x3f10 + sprite[0:8, 0:16]]
                    sprite_masked_color_base = np.ones((8, 16), np.uint8) * self.nes.mem.ppu_mem[0x3f10] * bg_mask
                    disp_color = disp_color_spr * bg_mask + disp_color_bg - sprite_masked_color_base
                    self.nes.disp.pixels[x:x+8, y:y+16] = disp_color

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
