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
            self.nes.ppu.control1 = value
            self.cpu_mem[addr] = value
            self.nes.ppu.loopyT &= 0xf3ff
            self.nes.ppu.loopyT |= (value & 3) << 10
            return
        #TODO
        if addr == 0x2001:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # sprite_memory address register
        if addr == 0x2003:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # sprite_memory i/o register
        if addr == 0x2004:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # vram address register #1 (scrolling)
        if addr == 0x2005:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # vram address register #2
        if addr == 0x2006:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # vram i/o register
        if addr == 0x2007:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

        # transfer 256 bytes of memory into sprite_memory
        if addr == 0x4014:
            print(" ### ppu_write() Not impliment yet, addr: 0x%x, value: 0x%x"%(addr, value))
            exit()
            return

    def write(self, addr, value):
        # PPU Status
        if addr == 0x2002:
            self.cpu_mem[addr] = value
            return

        # PPU Video Memory area
        if addr > 0x1fff and addr < 0x4000:
            self.nes.mem.ppu_write(addr, value)
            return

        # Sprite DMA Register
        if addr == 0x4014:
            self.nes.mem.ppu_write(addr, value)
            return

        # Joypad 1
        if addr == 0x4016:
            self.nes.mem.cpu_mem[addr] = 0x40
            return

        # Joypad 2
        if addr == 0x4017:
            self.nes.mem.cpu_mem[addr] = 0x48
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
            self.nes.mem.cpu_mem[addr] = value
            self.nes.mem.cpu_mem[addr + 2048] = value # mirror of 0-800
            self.nes.mem.cpu_mem[addr + 4096] = value # mirror of 0-800
            self.nes.mem.cpu_mem[addr + 6144] = value # mirror of 0-800
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

        self.nes.mem.cpu_mem[addr] = value

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
            # reset VRAM Address Register #1
            self.nes.ppu.bgscr_f = 0x00
            # reset VRAM Address Register #2
            self.nes.ppu.addr_h = 0x00
            # return bits 7-4 of unmodifyed ppu_status with bits 3-0 of the ppu_addr_tmp
            return (self.nes.ppu.status_tmp & 0xe0) | (self.nes.ppu.status_tmp & 0x1f)

        if addr == 0x2007:
            tmp = self.nes.ppu.addr_tmp
            self.nes.ppu.addr_tmp = self.nes.ppu.addr
            if self.nes.ppu.incrememt_32() == 0:
                self.nes.ppu.addr += 1
            else:
                self.nes.ppu.addr += 0x20

            return self.nes.mem.ppu_mem[tmp]

        # APU data (sound)
        if addr == 0x4015:
            return self.cpu_mem[addr]

        # joypad1 data
        if addr == 0x4016:
            self.cpu_mem[addr] = self.nes.in_put.pads[self.nes.in_put.readcnt]
            self.nes.in_put.readcnt += 1
            return self.cpu_mem[addr]

        if addr == 0x4017:
            return self.cpu_mem[addr]

        return self.cpu_mem[addr]
