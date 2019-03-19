#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class MEMORY():
    def __init__(self, nes):
        self.nes = nes
        # 64k main memory
        self.cpu_mem = np.zeros(64*1024, dtype=np.uint8)
        # 16k video memory
        self.ppu_mem = np.zeros(16*1024, dtype=np.uint8)
        # 256b sprite memory
        self.sprite_mem = np.zeros(256, dtype=np.uint8)
        self.tital = ''

    def ppu_write(self, addr, value):
        if addr == 0x2000:
            self.nes.ppu.addr_tmp = value
            self.nes.ppu.control_1 = value
            self.cpu_mem[addr] = value
            self.nes.ppu.loopyT &= 0xf3ff # (0000110000000000)
            self.nes.ppu.loopyT |= (value & 3) << 10 # (00000011)
            return

        if addr == 0x2001:
            self.nes.ppu.addr_tmp = value
            self.nes.ppu.control_2 = value
            self.cpu_mem[addr] = value
            return

        # sprite_memory address register
        if addr == 0x2003:
            self.nes.ppu.addr_tmp = value
            self.nes.ppu.sprite_address = value
            self.cpu_mem[addr] = value
            return

        # sprite_memory i/o register
        if addr == 0x2004:
            #print('###DBG### ppu_write() 0x2004, sprite_address: %x, data: %x'%(self.nes.ppu.sprite_address, value))
            self.nes.ppu.addr_tmp = value
            self.sprite_mem[self.nes.ppu.sprite_address] = value
            self.nes.ppu.sprite_address += 1
            self.cpu_mem[addr] = value
            return

        # vram address register #1 (scrolling)
        if addr == 0x2005:
            self.nes.ppu.addr_tmp = value

            if self.nes.ppu.bgscr_f == 0:
                self.nes.ppu.loopyT &= 0xffe0 # (0000000000011111)
                self.nes.ppu.loopyT |= (value & 0xf8) >> 3 # (11111000)
                self.nes.ppu.loopyX = value & 0x07 # (00000111)

                self.nes.ppu.bgscr_f = 1
                self.cpu_mem[addr] = value
                return

            if self.nes.ppu.bgscr_f == 1:
                self.nes.ppu.loopyT &= 0xfc1f # (0000001111100000)
                self.nes.ppu.loopyT |= (value & 0xf8) << 2 # (0111000000000000)
                self.nes.ppu.loopyT &= 0x8fff # (11111000)
                self.nes.ppu.loopyT |= (value & 0x07) << 12 # (00000111)

                self.nes.ppu.bgscr_f = 0
                self.cpu_mem[addr] = value
                return

        # vram address register #2
        if addr == 0x2006:
            self.nes.ppu.addr_tmp = value

            # First write -> Store the high byte 6 bits and clear out the last two
            if self.nes.ppu.addr_h == 0:
                self.nes.ppu.addr = value << 8
                self.nes.ppu.loopyT &= 0x00ff # (0011111100000000)
                self.nes.ppu.loopyT |= (value & 0x3f) << 8 # (1100000000000000) (00111111)

                if self.nes.debug & self.nes.PPU_DBG:
                    print('[%d] 0x2006 first = %x, ppu_addr = %x, loopyT: %x'%(self.nes.cpu.dbg_cnt, value, self.nes.ppu.addr, self.nes.ppu.loopyT));
                self.nes.ppu.addr_h = 1
                self.cpu_mem[addr] = value
                return

            # Second write -> Store the low byte 8 bits
            if self.nes.ppu.addr_h == 1:
                self.nes.ppu.addr |= value
                self.nes.ppu.loopyT &= 0xff00 # (0000000011111111)
                self.nes.ppu.loopyT |= value # (11111111)
                self.nes.ppu.loopyV = self.nes.ppu.loopyT # v=t

                if self.nes.debug & self.nes.PPU_DBG:
                    print('[%d] 0x2006 second = %x, ppu_addr = %x, loopyT: %x'%(self.nes.cpu.dbg_cnt, value, self.nes.ppu.addr, self.nes.ppu.loopyT));
                self.nes.ppu.addr_h = 0
                self.cpu_mem[addr] = value
                return

        # vram i/o register
        if addr == 0x2007:
            # if the vram_write_flag is on, vram writes should ignored
            if self.nes.ppu.vram_write_flag():
                return

            self.nes.ppu.addr_tmp = value

            if self.nes.debug & self.nes.PPU_DBG:
                print('[%d] 0x2007 -> writing [%x] to ppu_memory[%x]'%(self.nes.cpu.dbg_cnt, value, self.nes.ppu.addr));

            self.ppu_mem[self.nes.ppu.addr] = value

            # nametable mirroring
            if self.nes.ppu.addr > 0x1999 and self.nes.ppu.addr < 0x3000:
                if self.nes.rom.OS_MIRROR == 1:
                    self.ppu_mem[self.nes.ppu.addr + 0x400] = value
                    self.ppu_mem[self.nes.ppu.addr + 0x800] = value
                    self.ppu_mem[self.nes.ppu.addr + 0x1200] = value
                elif self.nes.rom.FS_MIRROR == 1:
                    print('FS_MIRRORING detected! do nothing')
                else:
                    if self.nes.rom.MIRRORING == 0:
                        # horizontal
                        self.ppu_mem[self.nes.ppu.addr + 0x400] = value
                    else:
                        # vertical
                        self.ppu_mem[self.nes.ppu.addr + 0x800] = value

            # palette mirror
            if self.nes.ppu.addr == 0x3f10:
                self.ppu_mem[0x3f00] = value

            self.nes.ppu.addr_tmp = self.nes.ppu.addr

            if not self.nes.ppu.increment_32():
                self.nes.ppu.addr += 1
            else:
                self.nes.ppu.addr += 0x20

            self.cpu_mem[addr] = value
            return

        # transfer 256 bytes of memory into sprite_memory
        if addr == 0x4014:
            for i in range(256):
                self.sprite_mem[i] = self.cpu_mem[0x100 * value + i]
            #for i in range(16):
            #    print('###DBG### ppu_write() 0x4014, value: %x, [%x, %x, %x, %x], [%x, %x, %x, %x], [%x, %x, %x, %x], [%x, %x, %x, %x]'%(value,
            #      self.sprite_mem[i*16+0], self.sprite_mem[i*16+1], self.sprite_mem[i*16+2], self.sprite_mem[i*16+3],
            #      self.sprite_mem[i*16+4], self.sprite_mem[i*16+5], self.sprite_mem[i*16+6], self.sprite_mem[i*16+7],
            #      self.sprite_mem[i*16+8], self.sprite_mem[i*16+9], self.sprite_mem[i*16+10], self.sprite_mem[i*16+11],
            #      self.sprite_mem[i*16+12], self.sprite_mem[i*16+13], self.sprite_mem[i*16+14], self.sprite_mem[i*16+15],
            #      ))
            return

    def write(self, addr, value):
        # PPU Status
        if addr == 0x2002:
            self.cpu_mem[addr] = value
            return

        # PPU Video Memory area
        if addr > 0x1fff and addr < 0x4000:
            self.ppu_write(addr, value)
            return

        # Sprite DMA Register
        if addr == 0x4014:
            self.ppu_write(addr, value)
            return

        # Joypad 1
        if addr == 0x4016:
            self.cpu_mem[addr] = 0x40
            return

        # Joypad 2
        if addr == 0x4017:
            self.cpu_mem[addr] = 0x48
            return
        # APU Sound Registers
        if addr > 0x3fff and addr < 0x4016:
            self.cpu_mem[addr] = value
            return

        # SRAM Registers
        if addr > 0x5fff and addr < 0x8000:
            if self.nes.rom.SRAM == 1:
                self.nes.write_sav()
            self.cpu_mem[addr] = value
            return

        # RAM registers
        if addr < 0x2000:
            self.cpu_mem[addr] = value
            self.cpu_mem[addr + 2048] = value # mirror of 0-800
            self.cpu_mem[addr + 4096] = value # mirror of 0-800
            self.cpu_mem[addr + 6144] = value # mirror of 0-800
            return

        if self.nes.rom.MAPPER == 1:
            self.nes.mappers.mmc1_access(addr, value)
            return

        if self.nes.rom.MAPPER == 2:
            self.nes.mappers.unrom_access(addr, value)
            return

        if self.nes.rom.MAPPER == 3:
            self.nes.mappers.cnrom_access(addr, value)
            return

        if self.nes.rom.MAPPER == 4:
            self.nes.mappers.mmc3_access(addr, value)
            return

        self.cpu_mem[addr] = value

    def read(self, addr):
        # this is ram or rom so we can return the address
        if addr < 0x2000 or addr > 0x7FFF:
            return self.cpu_mem[addr]

        # the addresses between 0x2000 and 0x5000 are for input/ouput
        if addr == 0x2002:
            self.nes.ppu.status_tmp = self.nes.ppu.status
            # set ppu status (D7) to 0 (vblank_on)
            self.nes.ppu.status &= 0x7f
            self.write(0x2002, self.nes.ppu.status)
            # set ppu_status (D6) to 0 (sprite_zero)
            self.nes.ppu.status &= 0x1f
            self.write(0x2002, self.nes.ppu.status)
            # reset VRAM Address Register #1
            self.nes.ppu.bgscr_f = 0x00
            # reset VRAM Address Register #2
            self.nes.ppu.addr_h = 0x00
            # return bits 7-4 of unmodifyed ppu_status with bits 3-0 of the ppu_addr_tmp
            return (self.nes.ppu.status_tmp & 0xe0) | (self.nes.ppu.addr_tmp & 0x1f)

        if addr == 0x2007:
            tmp = self.nes.ppu.addr_tmp
            self.nes.ppu.addr_tmp = self.nes.ppu.addr
            if self.nes.ppu.increment_32() == 0:
                self.nes.ppu.addr += 1
            else:
                self.nes.ppu.addr += 0x20

            return self.ppu_mem[tmp]

        # APU data (sound)
        if addr == 0x4015:
            return self.cpu_mem[addr]

        # joypad1 data
        if addr == 0x4016:
            self.cpu_mem[addr] = self.nes.in_put.pads[self.nes.in_put.readcnt]
            if self.nes.in_put.readcnt == 7:
                self.nes.in_put.readcnt  = 0
            else:
                self.nes.in_put.readcnt += 1
            return self.cpu_mem[addr]

        if addr == 0x4017:
            return self.cpu_mem[addr]

        return self.cpu_mem[addr]
