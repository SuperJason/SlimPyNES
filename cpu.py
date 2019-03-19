#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class CPU():
    DBG_OPCODE = 0x01
    DBG_NMI = 0x02
    def __init__(self, nes):
        self.nes = nes
        self.mem = nes.mem
        #self.debug = self.DBG_OPCODE | self.DBG_NMI
        self.debug = self.DBG_OPCODE
        self.dbg_cnt = 0
        self.addr = 0

    def sign8(self, data):
        ret = data & 0xff
        if ret > 127:
            ret -= 256
        return ret

    # Stack Push
    def push(self, data):
        self.mem.write(self.stack_pointer + 0x100, data)
        self.stack_pointer -= 1

    # Stack Pull
    def pull(self):
        self.stack_pointer += 1
        self.addr = self.mem.read(self.stack_pointer + 0x100)

    # Get the cpu flags
    def get_sr(self):
        if self.sign_flag:
            flags = 0x80
        if self.overflow_flag:
            flags |= 0x40
        if self.break_flag:
            flags |= 0x10
        if self.decimal_flag:
            flags |= 0x08
        if self.interrupt_flag:
            flags |= 0x04
        if self.zero_flag:
            flags |= 0x02
        if self.carry_flag:
            flags |= 0x01
        return flags

    # Set the cpu flags
    def set_sr(self, flags):
        self.sign_flag = bool(flags & 0x80)
        self.overflow_flag = bool(flags & 0x40)
        self.break_flag = bool((flags & 0x10) | 0x20)
        self.decimal_flag = bool(flags & 0x08)
        self.interrupt_flag = bool(flags & 0x04)
        self.zero_flag = bool(flags & 0x02)
        self.carry_flag = bool(flags & 0x01)

    def update_status_reg(self):
        self.status_reg = 0x20
        if self.sign_flag:
            self.status_reg |= 0x80
        if self.overflow_flag:
            self.status_reg |= 0x40
        if self.break_flag:
            self.status_reg |= 0x10
        if self.decimal_flag:
            self.status_reg |= 0x08
        if self.interrupt_flag:
            self.status_reg |= 0x04
        if self.zero_flag:
            self.status_reg |= 0x02
        if self.carry_flag:
            self.status_reg |= 0x01

    def reset(self):
        self.status_reg = 0x20
        self.zero_flag = bool(1)
        self.sign_flag = bool(0)
        self.overflow_flag = bool(0)
        self.break_flag = bool(0)
        self.decimal_flag = bool(0)
        self.interrupt_flag = bool(0)
        self.carry_flag = bool(0)

        self.stack_pointer = 0xff
        self.program_counter = (self.mem.cpu_mem[0xfffd] << 8) | self.mem.cpu_mem[0xfffc]

        self.accumulator=0x0
        self.x_reg=0x0
        self.y_reg=0x0
        print(' -- CPU Reset --')

    def opcode_dbg_prt(self, size, cycle, name, ext):
        op = self.mem.cpu_mem[self.program_counter - 1]
        flag_str = 'Z:%d, N:%d, O:%d, B:%d, D:%d, I:%d, C:%d'%(self.zero_flag, self.sign_flag, self.overflow_flag, self.break_flag, self.decimal_flag, self.interrupt_flag, self.carry_flag)
        reg_str = 'A:%x, P:%x, X:%x, Y:%x, S:0x%04x, addr:%x, ps: %x'%(self.accumulator, self.status_reg, self.x_reg, self.y_reg, self.stack_pointer + 0x100, self.addr, self.nes.ppu.status)
        if ext == 'NODATA':
            ass_str = ''
        elif ext == 'ACC':
            ass_str = '\tA'
        elif ext == 'aa':
            offset = self.sign8(self.mem.cpu_mem[self.program_counter])
            ass_str = '\t%x (%x + %d)'%((self.program_counter + offset) + 1, self.program_counter + 1, offset)
        elif ext == 'IM':
            addr = self.mem.cpu_mem[self.program_counter]
            ass_str = '\t#%x'%(addr)
        elif ext == 'ZP':
            addr = self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr]
            ass_str = '\t%x [mem value: %x]'%(addr, value)
        elif ext == 'ZPIX':
            addr = self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr + self.x_reg]
            ass_str = '\t%x, X [mem value: %x]'%(addr, value)
        elif ext == 'ZPIY':
            addr = self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr + self.y_reg]
            ass_str = '\t%x, Y [mem value: %x]'%(addr, value)
        elif ext == 'A':
            addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr]
            ass_str = '\t%x [mem value: %x]'%(addr, value)
        elif ext == 'AI':
            addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
            ass_str = '\t(%x)'%(addr)
        elif ext == 'AIX':
            addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr + self.x_reg]
            ass_str = '\t%0x, X [mem value: %x]'%(addr, value)
        elif ext == 'AIY':
            addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
            value = self.mem.cpu_mem[addr + self.y_reg]
            ass_str = '\t%0x, Y [mem value: %x]'%(addr, value)
        elif ext == 'IDI':
            addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
            value = (self.mem.cpu_mem[addr + 1] << 8) | self.mem.cpu_mem[addr]
            ass_str = '\t(%x, X) [mem location: %x]'%(addr, value)
        elif ext == 'INI':
            addr = self.mem.cpu_mem[self.program_counter]
            value = ((self.mem.cpu_mem[addr + 1] << 8) | self.mem.cpu_mem[addr]) + self.y_reg
            ass_str = '\t(%x), Y [mem location: %x]'%(addr, value)
        else:
            ass_str = '\twhich is unknown'
        #print('[%d] %s'%(self.dbg_cnt - 1, reg_str))
        #print('[%d] %s'%(self.dbg_cnt - 1, flag_str))
        #print('[%d] executing instruction at offset 0x%x: [0x%x - %s]'%(self.dbg_cnt - 1, self.program_counter - 1, op, name) + ass_str)
        regs_str = '[%d] %s'%(self.dbg_cnt - 1, reg_str)
        flags_str = '[%d] %s'%(self.dbg_cnt - 1, flag_str)
        ops_str = '[%d] executing instruction at offset 0x%x: [0x%x - %s]'%(self.dbg_cnt - 1, self.program_counter - 1, op, name) + ass_str
        #print(regs_str)
        #print(flags_str)
        #print(ops_str)
        self.nes.log_cmp_debug(regs_str, flags_str, ops_str)


# ----- OpCode Functions -----
# ADC  -  Add to Accumulator with Carry
    def adc_im(self): # 0x69
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_zp(self): # 0x65
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[self.program_counter])
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_zpix(self): # 0x75
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[self.program_counter] + self.x_reg)
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_a(self): # 0x6D
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter])
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_aix(self): # 0x7D
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg)
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_aiy(self): # 0x79
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg)
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_idi(self): # 0x61
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[self.program_counter] + self.y_reg)
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator + tmp2 + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80) != 0)
        self.carry_flag = tmp3 > 0xff
        self.accumulator = tmp3 & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def adc_ini(self): # 0x71
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ADC'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator + tmp2 + int(self.carry_flag)
        self.overflow_flag = (((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80) != 0)
        self.carry_flag = tmp3 > 0xff
        self.accumulator = tmp3 & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# AND  -  AND Memory with Accumulator
    def and_im(self): # 0x29
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator &= self.mem.cpu_mem[self.program_counter]
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_zp(self): # 0x25
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_zpix(self): # 0x35
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_a(self): # 0x2D
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_aix(self): # 0x3D
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.addr = tmp + self.x_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_aiy(self): # 0x39
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.addr = tmp + self.y_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_idi(self): # 0x21
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator &= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def and_ini(self): # 0x31
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'AND'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.accumulator &= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# ASL  -  Arithmatic Shift Left
    def arith_sl_acc(self): # 0x0A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'ASL'
            ext = 'ACC'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = (self.accumulator >> 7) & 0x01
        self.accumulator = (self.accumulator << 1) & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def arith_sl_zp(self): # 0x06
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ASL'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.mem.cpu_mem[self.program_counter]
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = ((self.addr & 0x80) != 0)
        self.zero_flag = ((self.addr) == 0)

        self.program_counter += size - 1
        return cycle
    def arith_sl_zpix(self): # 0x16
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ASL'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = ((self.addr & 0x80) != 0)
        self.zero_flag = ((self.addr) == 0)

        self.program_counter += size - 1
        return cycle
    def arith_sl_a(self): # 0x0E
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ASL'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = ((self.addr & 0x80) != 0)
        self.zero_flag = ((self.addr) == 0)

        self.program_counter += size - 1
        return cycle
    def arith_sl_aix(self): # 0x1E
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'ASL'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = ((self.addr & 0x80) != 0)
        self.zero_flag = ((self.addr) == 0)

        self.program_counter += size - 1
        return cycle

# BCC  -  Branch on Carry Clear
    def branch_cc(self): # 0x90
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BCC'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if not self.carry_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BCS  -  Branch on Carry Set
    def branch_cs(self): # 0xB0
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BCS'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if self.carry_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BEQ  -  Branch Zero Set
    def branch_zs(self): # 0xF0
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BEQ'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if self.zero_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# note: bit moet 5 instr zijn ipv 2?
# BIT  -  Test Bits in Memory with Accumulator
    def bit_test_zp(self): # 0x24
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'BIT'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        tmp2 = tmp & self.accumulator
        self.sign_flag = ((tmp & 0x80) != 0)
        self.overflow_flag = ((tmp & 0x40) != 0)
        self.zero_flag = ((tmp2) == 0)

        self.program_counter += size - 1
        return cycle
    def bit_test_a(self): # 0x2C
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'BIT'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        tmp2 = tmp & self.accumulator
        self.sign_flag = ((tmp & 0x80) != 0)
        self.overflow_flag = ((tmp & 0x40) != 0)
        self.zero_flag = ((tmp2) == 0)

        self.program_counter += size - 1
        return cycle

# BMI  -  Branch on Result Minus
    def branch_rm(self): # 0x30
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BMI'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if self.sign_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BNE  -  Branch on Z reset
    def branch_zr(self): # 0xD0
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BNE'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if not self.zero_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BPL  -  Branch on Result Plus (or Positive)
    def branch_rp(self): # 0x10
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BPL'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if not self.sign_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BRK  -  Force a Break
    def brk(self): # 0x00
        size = 1
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'BRK'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        self.break_flag = True
        self.push((self.program_counter & 0xff00) >> 8)
        self.push(self.program_counter & 0xff)
        self.push(self.get_sr())
        self.interrupt_flag = True
        self.program_counter = (self.mem.cpu_mem[0xffff] << 8) | self.mem.cpu_mem[0xfffe];

        return cycle

# BVC  -  Branch on Overflow Clear
    def branch_oc(self): # 0x50
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'BVC'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if not self.overflow_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# BVS  -  Branch on Overflow Set
    def branch_os(self): # 0x70
        size = 1
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'BVS'
            ext = 'aa'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter += 1
        if self.overflow_flag:
            self.program_counter += self.sign8(self.mem.cpu_mem[self.program_counter - 1])

        return cycle

# CLC  -  Clear Carry Flag
    def clear_cf(self): # 0x18
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CLC'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = 0

        self.program_counter += size - 1
        return cycle

# CLD  -  Clear Decimal Mode
    def clear_dm(self): # 0xD8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CLD'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.decimal_flag = 0

        self.program_counter += size - 1
        return cycle

# CLI  -  Clear Interrupt Disable
    def clear_id(self): # 0x58
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CLI'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.interrupt_flag = 0

        self.program_counter += size - 1
        return cycle

# CLV  -  Clear Overflow Flag
    def clear_of(self): # 0xB8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CLV'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.overflow_flag = 0

        self.program_counter += size - 1
        return cycle

# CMP  -  Compare Memory and Accumulator
    def comp_mem_im_a(self): # 0xC9
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.carry_flag = ((self.accumulator >= self.addr) != 0)
        self.sign_flag = ((self.sign8(self.accumulator) < self.sign8(self.addr)) != 0)
        self.zero_flag = ((self.accumulator == self.addr) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_zp_a(self): # 0xC5
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.accumulator >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.accumulator) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.accumulator == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_zpix(self): # 0xD5
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.accumulator >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.accumulator) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.accumulator == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_a_a(self): # 0xCD
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.accumulator >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.accumulator) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.accumulator == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_aix(self): # 0xDD
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        tmp = self.mem.read(self.addr)
        reg = self.accumulator
        self.carry_flag = ((reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_aiy(self): # 0xD9
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg
        tmp = self.mem.read(self.addr)
        reg = self.accumulator
        self.carry_flag = ((reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_idi(self): # 0xC1
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp2 = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp = self.mem.read(tmp2)
        reg = self.accumulator
        self.carry_flag = ((reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_ini(self): # 0xD1
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp2 = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp = self.mem.read(tmp2)
        reg = self.accumulator
        self.carry_flag = ((reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle

# CPX  -  Compare Memory and X register
    def comp_mem_im_x(self): # 0xE0
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CPX'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.carry_flag = ((self.x_reg >= self.addr) != 0)
        self.sign_flag = ((self.sign8(self.x_reg) < self.sign8(self.addr)) != 0)
        self.zero_flag = ((self.x_reg == self.addr) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_zp_x(self): # 0xE4
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'CPX'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.x_reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.x_reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.x_reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_a_x(self): # 0xEC
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'CPX'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.x_reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.x_reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.x_reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle

# CPY  -  Compare Memory and Y register
    def comp_mem_im_y(self): # 0xC0
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'CPY'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.carry_flag = ((self.y_reg >= self.addr) != 0)
        self.sign_flag = ((self.sign8(self.y_reg) < self.sign8(self.addr)) != 0)
        self.zero_flag = ((self.y_reg == self.addr) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_zp_y(self): # 0xC4
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'CPY'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.y_reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.y_reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.y_reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle
    def comp_mem_a_y(self): # 0xCC
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'CMP'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = ((self.y_reg >= tmp) != 0)
        self.sign_flag = ((self.sign8(self.y_reg) < self.sign8(tmp)) != 0)
        self.zero_flag = ((self.y_reg == tmp) != 0)

        self.program_counter += size - 1
        return cycle

# DEC  -  Decrement Memory by One
    def decr_mem_zp(self): # 0xC6
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'DEC'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = ((reg) == 0)

        self.program_counter += size - 1
        return cycle
    def decr_mem_zpix(self): # 0xD6
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'DEC'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = ((reg) == 0)

        self.program_counter += size - 1
        return cycle
    def decr_mem_a(self): # 0xCE
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'DEC'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = ((reg) == 0)

        self.program_counter += size - 1
        return cycle
    def decr_mem_aix(self): # 0xDE
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'DEC'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = ((reg) == 0)

        self.program_counter += size - 1
        return cycle

# DEX  -  Decrement X
    def decr_x(self): # 0xCA
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'DEX'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = (self.x_reg - 1) & 0xff
        self.sign_flag = ((self.x_reg & 0x80) != 0)
        self.zero_flag= ((self.x_reg) == 0)

        self.program_counter += size - 1
        return cycle

# DEY  -  Decrement Y
    def decr_y(self): # 0x88
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'DEY'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = (self.y_reg - 1) & 0xff
        self.sign_flag = ((self.y_reg & 0x80) != 0)
        self.zero_flag= ((self.y_reg) == 0)

        self.program_counter += size - 1
        return cycle

# EOR  -  Exclusive-OR Memory with Accumulator
    def excl_or_mem_im(self): # 0x49
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator ^= self.mem.cpu_mem[self.program_counter]
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_zp(self): # 0x45
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_zpix(self): # 0x55
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_a(self): # 0x4D
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_aix(self): # 0x5D
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_aiy(self): # 0x59
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_idi(self): # 0x41
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator ^= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def excl_or_mem_ini(self): # 0x51
        size = 1
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'EOR'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.accumulator ^= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# INC  -  Increment Memory by one
    def incr_mem_zp(self): # 0xE6
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'INC'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((self.mem.cpu_mem[self.addr] & 0x80) != 0)
        self.zero_flag = ((self.mem.cpu_mem[self.addr]) == 0)

        self.program_counter += size - 1
        return cycle
    def incr_mem_zpix(self): # 0xF6
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'INC'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((self.mem.cpu_mem[self.addr] & 0x80) != 0)
        self.zero_flag = ((self.mem.cpu_mem[self.addr]) == 0)

        self.program_counter += size - 1
        return cycle
    def incr_mem_a(self): # 0xEE
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'INC'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((self.mem.cpu_mem[self.addr] & 0x80) != 0)
        self.zero_flag = ((self.mem.cpu_mem[self.addr]) == 0)

        self.program_counter += size - 1
        return cycle
    def incr_mem_aix(self): # 0xFE
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'INC'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((self.mem.cpu_mem[self.addr] & 0x80) != 0)
        self.zero_flag = ((self.mem.cpu_mem[self.addr]) == 0)

        self.program_counter += size - 1
        return cycle

# INX  -  Increment X by one
    def incr_x(self): # 0xE8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'INX'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = (self.x_reg + 1) & 0xff
        self.sign_flag = ((self.x_reg & 0x80) != 0)
        self.zero_flag = ((self.x_reg) == 0)

        self.program_counter += size - 1
        return cycle

# INY  -  Increment Y by one
    def incr_y(self): # 0xC8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'INY'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = (self.y_reg + 1) & 0xff
        self.sign_flag = ((self.y_reg & 0x80) != 0)
        self.zero_flag = ((self.y_reg) == 0)

        self.program_counter += size - 1
        return cycle

# mis nog 1 JMP instructie
# JMP - Jump
    def jmp_a(self): # 0x4C
        size = 1
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'JMP'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.program_counter = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]

        return cycle
    def jmp_ai(self): # 0x6C
        size = 1
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'JMP'
            ext = 'AI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp2 = self.mem.read(tmp)
        tmp = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + 1
        self.addr = self.mem.read(tmp)
        self.program_counter = (self.addr << 8) | tmp2

        return cycle

# JSR - Jump to subroutine
    def jsr(self): # 0x20
        size = 1
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'JSR'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.push((self.program_counter + 1) >> 8)
        self.push(self.program_counter + 1)
        self.program_counter = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]

        return cycle

# LDA - Load Accumulator with memory
    def load_im_a(self): # 0xA9
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[self.program_counter]
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_zp_a(self): # 0xA5
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        reg = self.mem.cpu_mem[self.addr]
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_zpix_a(self): # 0xB5
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        reg = self.mem.cpu_mem[self.addr]
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_a_a(self): # 0xAD
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_aix_a(self): # 0xBD
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_aiy_a(self): # 0xB9
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle
    def load_idi(self): # 0xA1
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator = self.mem.read(tmp) & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def load_ini(self): # 0xB1
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'LDA'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.accumulator = self.mem.read(tmp) & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# LDX - Load X with Memory
    def load_im_x(self): # 0xA2
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'LDX'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[self.program_counter]
        self.x_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle
    def load_zp_x(self): # 0xA6
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'LDX'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        reg = self.mem.cpu_mem[self.addr]
        self.x_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle
    def load_zpiy(self): # 0xB6
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDX'
            ext = 'ZPIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.y_reg
        reg = self.mem.cpu_mem[self.addr]
        self.x_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_a_x(self): # 0xAE
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDX'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        reg = self.mem.read(self.addr)
        self.x_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_aiy_x(self): # 0xBE
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDX'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg
        reg = self.mem.read(self.addr)
        self.x_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

# LDY - Load Y with Memory
    def load_im_y(self): # 0xA0
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'LDY'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[self.program_counter]
        self.y_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_zp_y(self): # 0xA4
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'LDY'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_zpix_y(self): # 0xB4
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDY'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_a_y(self): # 0xAC
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDY'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

    def load_aix_y(self): # 0xBC
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'LDY'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        reg = self.mem.read(self.addr)
        self.y_reg = reg & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

# LSR  -  Logical Shift Right
    def logic_shift_r_acc(self): # 0x4A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'LSR'
            ext = 'ACC'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = ((self.accumulator & 0x01) != 0)
        self.accumulator = (self.accumulator >> 1) & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = not self.accumulator

        self.program_counter += size - 1
        return cycle
    def logic_shift_r_zp(self): # 0x46
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'LSR'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((tmp & 0x80) != 0)
        self.zero_flag = ((tmp) == 0)

        self.program_counter += size - 1
        return cycle
    def logic_shift_r_zpix(self): # 0x56
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'LSR'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((tmp & 0x80) != 0)
        self.zero_flag = ((tmp) == 0)

        self.program_counter += size - 1
        return cycle
    def logic_shift_r_a(self): # 0x4E
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'LSR'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((tmp & 0x80) != 0)
        self.zero_flag = ((tmp) == 0)

        self.program_counter += size - 1
        return cycle
    def logic_shift_r_aix(self): # 0x5E
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'LSR'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = ((tmp & 0x80) != 0)
        self.zero_flag = ((tmp) == 0)

        self.program_counter += size - 1
        return cycle

# NOP - No Operation (79 instructies?)
    def nop(self): # 0xEA
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'NOP'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)
        self.program_counter += size - 1
        return cycle

# ORA  -  OR Memory with Accumulator
    def or_mem_im(self): # 0x09
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator |= self.mem.cpu_mem[self.program_counter]
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_zp(self): # 0x05
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_zpix(self): # 0x15
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_a(self): # 0x0D
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_aix(self): # 0x1D
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_aiy(self): # 0x19
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_idi(self): # 0x01
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator |= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def or_mem_ini(self): # 0x11
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ORA'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]  + self.y_reg
        self.accumulator |= self.mem.read(tmp)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# PHA  -  Push Accumulator on Stack
    def push_a(self): # 0x48
        size = 1
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'PHA'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.mem.write(self.stack_pointer + 0x100, self.accumulator)
        self.stack_pointer -= 1

        self.program_counter += size - 1
        return cycle

# PHP  -  Push Processor Status on Stack
    def push_ps(self): # 0x08
        size = 1
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'PHP'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.push(self.get_sr())

        self.program_counter += size - 1
        return cycle

# PLA  -  Pull Accumulator from Stack
    def pull_a(self): # 0x68
        size = 1
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'PLA'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.stack_pointer += 1
        self.accumulator = self.mem.read(self.stack_pointer + 0x100) & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# PLP  -  Pull Processor Status from Stack
    def pull_ps(self): # 0x28
        size = 1
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'PLP'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.pull()
        self.addr = self.mem.read(self.stack_pointer + 0x100)
        self.set_sr(self.addr)

        self.program_counter += size - 1
        return cycle

# ROL  -  Rotate Left
    def rotate_left_acc(self): # 0x2A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'ROL'
            ext = 'ACC'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        self.carry_flag = (((self.accumulator >> 7) & 0x01) != 0)
        self.accumulator = (self.accumulator << 1) & 0xff
        self.accumulator |= tmp
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_left_zp(self): # 0x26
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ROL'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[self.program_counter]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = (((self.addr >> 7) & 0x01) != 0)
        # TODO 
        # self.addr = (self.addr << 1) & 0xff
        self.addr = self.addr << 1
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_left_zpix(self): # 0x36
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ROL'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = (((self.addr >> 7) & 0x01) != 0)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_left_a(self): # 0x2E
        size = 3
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ROL'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = (((self.addr >> 7) & 0x01) != 0)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_left_aix(self): # 0x3E
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'ROL'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = (((self.addr >> 7) & 0x01) != 0)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# ROR  -  Rotate Right
    def rotate_right_acc(self): # 0x6A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'ROR'
            ext = 'ACC'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        self.carry_flag = self.accumulator & 0x01
        self.accumulator = (self.accumulator >> 1) & 0xff
        if tmp:
            self.accumulator |= 0x80
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_right_zp(self): # 0x66
        size = 1
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'ROR'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[self.program_counter]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_right_zpix(self): # 0x76
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ROR'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_right_a(self): # 0x6E
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'ROR'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter])
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def rotate_right_aix(self): # 0x7E
        size = 3
        cycle = 7
        if self.debug & self.DBG_OPCODE:
            name = 'ROR'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# RTI  -  Return from Interrupt
    def ret_int(self): # 0x40
        size = 1
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'RTI'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.pull()
        self.set_sr(self.addr)
        self.pull()
        self.program_counter = self.addr
        self.pull()
        self.program_counter += (self.addr << 8)

        return cycle

# RTS  -  Return from Subroutine
    def ret_sub(self): # 0x60
        size = 1
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'RTS'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.pull()
        self.program_counter = self.addr + 1 
        self.pull()
        self.program_counter += (self.addr << 8)

        return cycle

# SBC  -  Subtract from Accumulator with Carry (IDI_ZP?)
    def sub_acc_im(self): # 0xE9
        size = 2
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'IM'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        # TODO if self.dbg_cnt > 228922:
        # tmp = self.accumulator - self.addr - int(not self.carry_flag
        tmp = (self.accumulator - self.addr - int(not self.carry_flag) & 0xffffffff)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def sub_acc_zp(self): # 0xE5
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[self.program_counter])
        # TODO if self.dbg_cnt > 4107136
        #tmp = self.accumulator - self.addr - int(not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag) & 0xffffffff)
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def sub_acc_zpix(self): # 0xF5
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[self.program_counter] + self.x_reg)
        # TODO self.dbg_cnt: 385423
        #tmp = self.accumulator - self.addr - int(not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def sub_acc_a(self): # 0xED
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter])
        #tmp = self.accumulator - self.addr - int(not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def sub_acc_aix(self): # 0xFD
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg)
        #tmp = self.accumulator - self.addr - int(not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle
    def sub_acc_aiy(self): # 0xF9
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg)
        #tmp = self.accumulator - self.addr - (not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80) != 0)
        self.carry_flag = ((tmp <= 0xff) != 0)
        self.accumulator = tmp & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = not self.accumulator

        self.program_counter += size - 1
        return cycle
    def sub_acc_idi(self): # 0xE1
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp2 = self.mem.read(tmp)
        #tmp3 = self.accumulator - tmp2 - int(not self.carry_flag)
        tmp3 = (self.accumulator - tmp2 - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80) != 0)
        self.carry_flag = ((tmp3 <= 0xff) != 0)
        self.accumulator = tmp3 & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = not self.accumulator

        self.program_counter += size - 1
        return cycle
    def sub_acc_ini(self): # 0xF1
        size = 2
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'SBC'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp2 = self.mem.read(tmp)
        #tmp3 = self.accumulator - tmp2 - int(not self.carry_flag)
        tmp3 = (self.accumulator - tmp2 - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = (((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80) != 0)
        self.carry_flag = ((tmp3 <= 0xff) != 0)
        self.accumulator = tmp3 & 0xff
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = not self.accumulator

        self.program_counter += size - 1
        return cycle

# SEC  -  Set Carry Flag
    def set_c_flag(self): # 0x38
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'SEC'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = True

        self.program_counter += size - 1
        return cycle

# SED  -  Set Decimal Mode
    def set_d_mode(self): # 0xF8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'SED'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.decimal_flag = True

        self.program_counter += size - 1
        return cycle

# SEI - Set Interrupt Disable
    def set_int_dis(self): # 0x78
        name = 'SEI'
        ext = "NODATA"
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.interrupt_flag = 1

        self.program_counter += size - 1
        return cycle

# STA - Store Accumulator in Memory (IDI_ZP?)
    def store_zp_a(self): # 0x85
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.accumulator)

        self.program_counter += size - 1
        return cycle
    def store_zpix_a(self): # 0x95
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.mem.write(self.addr, self.accumulator)

        self.program_counter += size - 1
        return cycle
    def store_a_a(self): # 0x8D
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        reg = self.accumulator
        self.mem.write(self.addr, reg)

        self.program_counter += size - 1
        return cycle

    def store_aix(self): # 0x9D
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'AIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.x_reg
        reg = self.accumulator
        self.mem.write(self.addr, reg)

        self.program_counter += size - 1
        return cycle
    def store_aiy(self): # 0x99
        size = 3
        cycle = 5
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'AIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]) + self.y_reg
        self.mem.write(self.addr, self.accumulator)

        self.program_counter += size - 1
        return cycle
    def store_idi(self): # 0x81
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'IDI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.mem.write(tmp, self.accumulator)

        self.program_counter += size - 1
        return cycle
    def store_ini(self): # 0x91
        size = 2
        cycle = 6
        if self.debug & self.DBG_OPCODE:
            name = 'STA'
            ext = 'INI'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.mem.write(tmp, self.accumulator)

        self.program_counter += size - 1
        return cycle

# STX - Store X in Memory
    def store_zp_x(self): # 0x86
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'STX'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.x_reg)

        self.program_counter += size - 1
        return cycle

    def store_zpiy(self): # 0x96
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STX'
            ext = 'ZPIY'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.y_reg
        self.mem.write(self.addr, self.x_reg)

        self.program_counter += size - 1
        return cycle
    def store_a_x(self): # 0x8E
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STX'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.x_reg)

        self.program_counter += size - 1
        return cycle

# STY - Store Y in Memory
    def store_zp_y(self): # 0x84
        size = 2
        cycle = 3
        if self.debug & self.DBG_OPCODE:
            name = 'STY'
            ext = 'ZP'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.y_reg)

        self.program_counter += size - 1
        return cycle
    def store_zpix(self): # 0x94
        size = 2
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STY'
            ext = 'ZPIX'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.mem.write(self.addr, self.y_reg)

        self.program_counter += size - 1
        return cycle
    def store_a_y(self): # 0x8C
        size = 3
        cycle = 4
        if self.debug & self.DBG_OPCODE:
            name = 'STY'
            ext = 'A'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[self.program_counter + 1] << 8) | self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.y_reg)

        self.program_counter += size - 1
        return cycle

# TAX  -  Transfer Accumulator to X
    def transfer_reg_x(self): # 0xAA
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TAX'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = self.accumulator
        self.sign_flag = ((self.x_reg & 0x80) != 0)
        self.zero_flag = ((self.x_reg) == 0)

        self.program_counter += size - 1
        return cycle

# TAY  -  Transfer Accumulator to Y
    def transfer_reg_y(self): # 0xA8
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TAY'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = self.accumulator
        self.sign_flag = ((self.y_reg & 0x80) != 0)
        self.zero_flag = ((self.y_reg) == 0)

        self.program_counter += size - 1
        return cycle

# TSX  -  Transfer Stack to X
    def transfer_stack_from(self): # 0xBA
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TSX'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = self.stack_pointer
        self.sign_flag = ((self.x_reg & 0x80) != 0)
        self.zero_flag = ((self.x_reg) == 0)

        self.program_counter += size - 1
        return cycle

# TXA  -  Transfer X to Accumulator
    def transfer_reg_xa(self): # 0x8A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TXA'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator = self.x_reg
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# TXS  -  Transfer X to Stack
    def transfer_stack_to(self): # 0x9A
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TXS'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.x_reg
        self.stack_pointer = (reg + 0x100) & 0xff
        self.sign_flag = ((reg & 0x80) != 0)
        self.zero_flag = not reg

        self.program_counter += size - 1
        return cycle

# TYA  -  Transfer Y to Accumulator
    def transfer_reg_ya(self): # 0x98
        size = 1
        cycle = 2
        if self.debug & self.DBG_OPCODE:
            name = 'TYA'
            ext = 'NODATA'
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator = self.y_reg
        self.sign_flag = ((self.accumulator & 0x80) != 0)
        self.zero_flag = ((self.accumulator) == 0)

        self.program_counter += size - 1
        return cycle

# ----- OpCode Dict -----
    opcode = {
            0x00: brk,
            0x01: or_mem_idi,
            0x05: or_mem_zp,
            0x06: arith_sl_zp,
            0x08: push_ps,
            0x09: or_mem_im,
            0x0a: arith_sl_acc,
            0x0d: or_mem_a,
            0x0e: arith_sl_a,
            0x10: branch_rp,
            0x11: or_mem_ini,
            0x15: or_mem_zpix,
            0x16: arith_sl_zpix,
            0x18: clear_cf,
            0x19: or_mem_aiy,
            0x1d: or_mem_aix,
            0x1e: arith_sl_aix,
            0x20: jsr,
            0x21: and_idi,
            0x24: bit_test_zp,
            0x25: and_zp,
            0x26: rotate_left_zp,
            0x28: pull_ps,
            0x29: and_im,
            0x2a: rotate_left_acc,
            0x2c: bit_test_a,
            0x2d: and_a,
            0x2e: rotate_left_a,
            0x30: branch_rm,
            0x31: and_ini,
            0x35: and_zpix,
            0x36: rotate_left_zpix,
            0x38: set_c_flag,
            0x39: and_aiy,
            0x3d: and_aix,
            0x3e: rotate_left_aix,
            0x40: ret_int,
            0x41: excl_or_mem_idi,
            0x45: excl_or_mem_zp,
            0x46: logic_shift_r_zp,
            0x48: push_a,
            0x49: excl_or_mem_im,
            0x4a: logic_shift_r_acc,
            0x4d: excl_or_mem_a,
            0x4e: logic_shift_r_a,
            0x4c: jmp_a,
            0x50: branch_oc,
            0x51: excl_or_mem_ini,
            0x55: excl_or_mem_zpix,
            0x56: logic_shift_r_zpix,
            0x58: clear_id,
            0x59: excl_or_mem_aiy,
            0x5d: excl_or_mem_aix,
            0x5e: logic_shift_r_aix,
            0x60: ret_sub,
            0x61: adc_idi,
            0x65: adc_zp,
            0x66: rotate_right_zp,
            0x68: pull_a,
            0x69: adc_im,
            0x6a: rotate_right_acc,
            0x6d: adc_a,
            0x6e: rotate_right_a,
            0x6c: jmp_ai,
            0x70: branch_os,
            0x71: adc_ini,
            0x75: adc_zpix,
            0x76: rotate_right_zpix,
            0x78: set_int_dis,
            0x79: adc_aiy,
            0x7d: adc_aix,
            0x7e: rotate_right_aix,
            0x81: store_idi,
            0x84: store_zp_y,
            0x85: store_zp_a,
            0x86: store_zp_x,
            0x88: decr_y,
            0x8a: transfer_reg_xa,
            0x8c: store_a_y,
            0x8d: store_a_a,
            0x8e: store_a_x,
            0x90: branch_cc,
            0x91: store_ini,
            0x94: store_zpix,
            0x95: store_zpix_a,
            0x96: store_zpiy,
            0x98: transfer_reg_ya,
            0x99: store_aiy,
            0x9a: transfer_stack_to,
            0x9d: store_aix,
            0xa0: load_im_y,
            0xa1: load_idi,
            0xa2: load_im_x,
            0xa4: load_zp_y,
            0xa5: load_zp_a,
            0xa6: load_zp_x,
            0xa8: transfer_reg_y,
            0xa9: load_im_a,
            0xaa: transfer_reg_x,
            0xac: load_a_y,
            0xad: load_a_a,
            0xae: load_a_x,
            0xb0: branch_cs,
            0xb1: load_ini,
            0xb4: load_zpix_y,
            0xb5: load_zpix_a,
            0xb6: load_zpiy,
            0xb8: clear_of,
            0xb9: load_aiy_a,
            0xba: transfer_stack_from,
            0xbc: load_aix_y,
            0xbd: load_aix_a,
            0xbe: load_aiy_x,
            0xc0: comp_mem_im_y,
            0xc1: comp_mem_idi,
            0xc4: comp_mem_zp_y,
            0xc5: comp_mem_zp_a,
            0xc6: decr_mem_zp,
            0xc8: incr_y,
            0xc9: comp_mem_im_a,
            0xca: decr_x,
            0xcc: comp_mem_a_y,
            0xcd: comp_mem_a_a,
            0xce: decr_mem_a,
            0xd0: branch_zr,
            0xd1: comp_mem_ini,
            0xd5: comp_mem_zpix,
            0xd6: decr_mem_zpix,
            0xd8: clear_dm,
            0xd9: comp_mem_aiy,
            0xdd: comp_mem_aix,
            0xde: decr_mem_aix,
            0xe0: comp_mem_im_x,
            0xe1: sub_acc_idi,
            0xe4: comp_mem_zp_x,
            0xe5: sub_acc_zp,
            0xe6: incr_mem_zp,
            0xe8: incr_x,
            0xe9: sub_acc_im,
            0xea: nop,
            0xec: comp_mem_a_x,
            0xed: sub_acc_a,
            0xee: incr_mem_a,
            0xf0: branch_zs,
            0xf1: sub_acc_ini,
            0xf5: sub_acc_zpix,
            0xf6: incr_mem_zpix,
            0xf8: set_d_mode,
            0xf9: sub_acc_aiy,
            0xfd: sub_acc_aix,
            0xfe: incr_mem_aix,
            }

    def nmi(self, cycles = 7):
        if bool(self.debug & self.DBG_NMI):
            print('[%d] executing NMI routine'%(self.dbg_cnt - 1))

        self.push((self.program_counter & 0xff00) >> 8)
        self.push(self.program_counter & 0xff)
        self.push(self.get_sr())
        self.break_flag = False
        self.interrupt_flag = True
        self.program_counter = (self.mem.cpu_mem[0xfffb] << 8) | self.mem.cpu_mem[0xfffa]

        return cycles - 7

    def execute(self, cycles = 1):
        cycle_count = round(cycles)
        while(cycle_count > 0):
            self.dbg_cnt += 1
            self.update_status_reg()
            op = self.mem.cpu_mem[self.program_counter]
            self.program_counter += 1
            if (op in self.opcode):
                cycle_count -= self.opcode[op](self)
            else:
                cycle_count -= 1
                print(' ### OpCode 0x%x @ 0x%xis not supported!!!'%(op, self.program_counter))
                exit()

        return cycles - cycle_count

