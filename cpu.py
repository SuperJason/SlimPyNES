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
        self.debug = self.DBG_OPCODE | self.DBG_NMI
        self.dbg_cnt = 0
        self.addr = 0

    def sign8(self, data):
        ret = data & 0xff
        if ret > 127:
            ret -= 256
        return ret

    # Stack Push
    def push(self, data):
        #print(" ### DBG ### PUSH data: 0x%x"%(data))
        self.mem.write(self.stack_pointer + 0x100, data)
        self.stack_pointer -= 1

    # Stack Pull
    def pull(self):
        self.stack_pointer += 1
        self.addr = self.mem.read(self.stack_pointer + 0x100)
        #print(" ### DBG ### PULL addr: 0x%x"%(self.addr))

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
        #print(" ### DBG ### GET SR flags: 0x%x"%(flags))
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
        reg_str = 'A:%x, P:%x, X:%x, Y:%x, S:0x%04x, addr:%x'%(self.accumulator, self.status_reg, self.x_reg, self.y_reg, self.stack_pointer + 0x100, self.addr)
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
        print(regs_str)
        print(flags_str)
        print(ops_str)
        #self.nes.log_cmp_debug(regs_str, flags_str, ops_str)


# ----- OpCode Functions -----
# ADC  -  Add to Accumulator with Carry
    def adc_im(self, pc, cycle_count): # 0x69
        name = 'ADC'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_zp(self, pc, cycle_count): # 0x65
        name = 'ADC'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[pc])
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_zpix(self, pc, cycle_count): # 0x75
        name = 'ADC'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[pc]) + self.x_reg
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_a(self, pc, cycle_count): # 0x6D
        name = 'ADC'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc])
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_aix(self, pc, cycle_count): # 0x7D
        name = 'ADC'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg)
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_aiy(self, pc, cycle_count): # 0x79
        name = 'ADC'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg)
        tmp = self.accumulator + self.addr + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp > 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_idi(self, pc, cycle_count): # 0x61
        name = 'ADC'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[pc] + self.y_reg)
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator + tmp2 + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80)
        self.carry_flag = tmp3 > 0xff
        self.accumulator = tmp3 & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def adc_ini(self, pc, cycle_count): # 0x71
        name = 'ADC'
        ext = 'INI'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator + tmp2 + int(self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80)
        self.carry_flag = tmp3 > 0xff
        self.accumulator = tmp3 & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# AND  -  AND Memory with Accumulator
    def and_im(self, pc, cycle_count): # 0x29
        name = 'AND'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator &= self.mem.cpu_mem[pc]
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_zp(self, pc, cycle_count): # 0x25
        name = 'AND'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_zpix(self, pc, cycle_count): # 0x35
        name = 'AND'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_a(self, pc, cycle_count): # 0x2D
        name = 'AND'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_aix(self, pc, cycle_count): # 0x3D
        name = 'AND'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.addr = tmp + self.x_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_aiy(self, pc, cycle_count): # 0x39
        name = 'AND'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.addr = tmp + self.y_reg
        self.accumulator &= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_idi(self, pc, cycle_count): # 0x21
        name = 'AND'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator &= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def and_ini(self, pc, cycle_count): # 0x31
        name = 'AND'
        ext = 'INI'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.accumulator &= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# ASL  -  Arithmatic Shift Left
    def arith_sl_acc(self, pc, cycle_count): # 0x0A
        name = 'ASL'
        ext = 'ACC'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = (self.accumulator >> 7) & 0x01
        self.accumulator = (self.accumulator << 1) & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_zp(self, pc, cycle_count): # 0x06
        name = 'ASL'
        ext = 'ZP'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.mem.cpu_mem[pc]
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = bool(self.addr & 0x80)
        self.zero_flag = not bool(self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_zpix(self, pc, cycle_count): # 0x16
        name = 'ASL'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.mem.cpu_mem[pc] + self.x_reg
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = bool(self.addr & 0x80)
        self.zero_flag = not bool(self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_a(self, pc, cycle_count): # 0x0E
        name = 'ASL'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = bool(self.addr & 0x80)
        self.zero_flag = not bool(self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_aix(self, pc, cycle_count): # 0x1E
        name = 'ASL'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.addr = self.mem.read(tmp)
        self.carry_flag = (self.addr >> 7) & 0x01
        self.addr = self.addr << 1
        self.mem.write(tmp, self.addr)
        self.sign_flag = bool(self.addr & 0x80)
        self.zero_flag = not bool(self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# BCC  -  Branch on Carry Clear
    def branch_cc(self, pc, cycle_count): # 0x90
        name = 'BCC'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if not self.carry_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BCS  -  Branch on Carry Set
    def branch_cs(self, pc, cycle_count): # 0xB0
        name = 'BCS'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if self.carry_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BEQ  -  Branch Zero Set
    def branch_zs(self, pc, cycle_count): # 0xF0
        name = 'BEQ'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if self.zero_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= 2
        return pc, cycle_count

# note: bit moet 5 instr zijn ipv 2?
# BIT  -  Test Bits in Memory with Accumulator
    def bit_test_zp(self, pc, cycle_count): # 0x24
        name = 'BIT'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        tmp2 = tmp & self.accumulator
        self.sign_flag = bool(tmp & 0x80)
        self.overflow_flag = bool(tmp & 0x40)
        self.zero_flag = not bool(tmp2)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def bit_test_a(self, pc, cycle_count): # 0x2C
        name = 'BIT'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        tmp2 = tmp & self.accumulator
        self.sign_flag = bool(tmp & 0x80)
        self.overflow_flag = bool(tmp & 0x40)
        self.zero_flag = not bool(tmp2)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# BMI  -  Branch on Result Minus
    def branch_rm(self, pc, cycle_count): # 0x30
        name = 'BMI'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if self.sign_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BNE  -  Branch on Z reset
    def branch_zr(self, pc, cycle_count): # 0xD0
        name = 'BNE'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if not self.zero_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BPL  -  Branch on Result Plus (or Positive)
    def branch_rp(self, pc, cycle_count): # 0x10
        name = 'BPL'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if not self.sign_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BRK  -  Force a Break
    def brk(self, pc, cycle_count): # 0x00
        name = 'BRK'
        ext = 'NODATA'
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        self.break_flag = True
        self.push((pc & 0xff00) >> 8)
        self.push(pc & 0xff)
        self.push(self.get_sr())
        self.interrupt_flag = True
        pc = (self.mem.cpu_mem[0xffff] << 8) | self.mem.cpu_mem[0xfffe];

        cycle_count -= cycle
        return pc, cycle_count

# BVC  -  Branch on Overflow Clear
    def branch_oc(self, pc, cycle_count): # 0x50
        name = 'BVC'
        ext = 'aa'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if not self.overflow_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# BVS  -  Branch on Overflow Set
    def branch_os(self, pc, cycle_count): # 0x70
        name = 'BVS'
        ext = 'aa'
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc += 1
        if self.overflow_flag:
            pc += self.sign8(self.mem.cpu_mem[pc - 1])

        cycle_count -= cycle
        return pc, cycle_count

# CLC  -  Clear Carry Flag
    def clear_cf(self, pc, cycle_count): # 0x18
        name = 'CLC'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = 0

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CLD  -  Clear Decimal Mode
    def clear_dm(self, pc, cycle_count): # 0xD8
        name = 'CLD'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.decimal_flag = 0

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CLI  -  Clear Interrupt Disable
    def clear_id(self, pc, cycle_count): # 0x58
        name = 'CLI'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.interrupt_flag = 0

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CLV  -  Clear Overflow Flag
    def clear_of(self, pc, cycle_count): # 0xB8
        name = 'CLV'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.overflow_flag = 0

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CMP  -  Compare Memory and Accumulator
    def comp_mem_im_a(self, pc, cycle_count): # 0xC9
        name = 'CMP'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.carry_flag = bool(self.accumulator >= self.addr)
        self.sign_flag = bool(self.sign8(self.accumulator) < self.sign8(self.addr))
        self.zero_flag = bool(self.accumulator == self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp_a(self, pc, cycle_count): # 0xC5
        name = 'CMP'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.accumulator >= tmp)
        self.sign_flag = bool(self.sign8(self.accumulator) < self.sign8(tmp))
        self.zero_flag = bool(self.accumulator == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zpix(self, pc, cycle_count): # 0xD5
        name = 'CMP'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.accumulator >= tmp)
        self.sign_flag = bool(self.sign8(self.accumulator) < self.sign8(tmp))
        self.zero_flag = bool(self.accumulator == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a_a(self, pc, cycle_count): # 0xCD
        name = 'CMP'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.accumulator >= tmp)
        self.sign_flag = bool(self.sign8(self.accumulator) < self.sign8(tmp))
        self.zero_flag = bool(self.accumulator == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_aix(self, pc, cycle_count): # 0xDD
        name = 'CMP'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        tmp = self.mem.read(self.addr)
        reg = self.accumulator
        self.carry_flag = bool(reg >= tmp)
        self.sign_flag = bool(self.sign8(reg) < self.sign8(tmp))
        self.zero_flag = bool(reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_aiy(self, pc, cycle_count): # 0xD9
        name = 'CMP'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg
        tmp = self.mem.read(self.addr)
        reg = self.accumulator
        self.carry_flag = bool(reg >= tmp)
        self.sign_flag = bool(self.sign8(reg) < self.sign8(tmp))
        self.zero_flag = bool(reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_idi(self, pc, cycle_count): # 0xC1
        name = 'CMP'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp2 = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp = self.mem.read(tmp2)
        reg = self.accumulator
        self.carry_flag = bool(reg >= tmp)
        self.sign_flag = bool(self.sign8(reg) < self.sign8(tmp))
        self.zero_flag = bool(reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_ini(self, pc, cycle_count): # 0xD1
        name = 'CMP'
        ext = 'INI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp2 = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp = self.mem.read(tmp2)
        reg = self.accumulator
        self.carry_flag = bool(reg >= tmp)
        self.sign_flag = bool(self.sign8(reg) < self.sign8(tmp))
        self.zero_flag = bool(reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CPX  -  Compare Memory and X register
    def comp_mem_im_x(self, pc, cycle_count): # 0xE0
        name = 'CPX'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.carry_flag = bool(self.x_reg >= self.addr)
        self.sign_flag = bool(self.sign8(self.x_reg) < self.sign8(self.addr))
        self.zero_flag = bool(self.x_reg == self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp_x(self, pc, cycle_count): # 0xE4
        name = 'CPX'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.x_reg >= tmp)
        self.sign_flag = bool(self.sign8(self.x_reg) < self.sign8(tmp))
        self.zero_flag = bool(self.x_reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a_x(self, pc, cycle_count): # 0xEC
        name = 'CPX'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.x_reg >= tmp)
        self.sign_flag = bool(self.sign8(self.x_reg) < self.sign8(tmp))
        self.zero_flag = bool(self.x_reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# CPY  -  Compare Memory and Y register
    def comp_mem_im_y(self, pc, cycle_count): # 0xC0
        name = 'CPY'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.carry_flag = bool(self.y_reg >= self.addr)
        self.sign_flag = bool(self.sign8(self.y_reg) < self.sign8(self.addr))
        self.zero_flag = bool(self.y_reg == self.addr)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp_y(self, pc, cycle_count): # 0xC4
        name = 'CPY'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.y_reg >= tmp)
        self.sign_flag = bool(self.sign8(self.y_reg) < self.sign8(tmp))
        self.zero_flag = bool(self.y_reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a_y(self, pc, cycle_count): # 0xCC
        name = 'CMP'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = bool(self.y_reg >= tmp)
        self.sign_flag = bool(self.sign8(self.y_reg) < self.sign8(tmp))
        self.zero_flag = bool(self.y_reg == tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# DEC  -  Decrement Memory by One
    def decr_mem_zp(self, pc, cycle_count): # 0xC6
        name = 'DEC'
        ext = 'ZP'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not bool(reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_zpix(self, pc, cycle_count): # 0xD6
        name = 'DEC'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not bool(reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_a(self, pc, cycle_count): # 0xCE
        name = 'DEC'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not bool(reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_aix(self, pc, cycle_count): # 0xDE
        name = 'DEC'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        tmp = self.mem.read(self.addr) - 1
        self.mem.write(self.addr, tmp)
        reg = self.mem.cpu_mem[self.addr]
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not bool(reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# DEX  -  Decrement X
    def decr_x(self, pc, cycle_count): # 0xCA
        name = 'DEX'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = (self.x_reg - 1) & 0xff
        self.sign_flag = bool(self.x_reg & 0x80)
        self.zero_flag= not bool(self.x_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# DEY  -  Decrement Y
    def decr_y(self, pc, cycle_count): # 0x88
        name = 'DEY'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = (self.y_reg - 1) & 0xff
        self.sign_flag = bool(self.y_reg & 0x80)
        self.zero_flag= not bool(self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# EOR  -  Exclusive-OR Memory with Accumulator
    def excl_or_mem_im(self, pc, cycle_count): # 0x49
        name = 'EOR'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator ^= self.mem.cpu_mem[pc]
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_zp(self, pc, cycle_count): # 0x45
        name = 'EOR'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_zpix(self, pc, cycle_count): # 0x55
        name = 'EOR'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_a(self, pc, cycle_count): # 0x4D
        name = 'EOR'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_aix(self, pc, cycle_count): # 0x5D
        name = 'EOR'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_aiy(self, pc, cycle_count): # 0x59
        name = 'EOR'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg
        self.accumulator ^= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_idi(self, pc, cycle_count): # 0x41
        name = 'EOR'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = (self.mem.cpu_mem[addr + 1] << 8) | self.mem.cpu_mem[addr]
        self.accumulator ^= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_ini(self, pc, cycle_count): # 0x51
        name = 'EOR'
        ext = 'INI'
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[addr + 1] << 8) | self.mem.cpu_mem[addr]) + self.y_reg
        self.accumulator ^= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# INC  -  Increment Memory by one
    def incr_mem_zp(self, pc, cycle_count): # 0xE6
        name = 'INC'
        ext = 'ZP'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(self.mem.cpu_mem[self.addr] & 0x80)
        self.zero_flag = not bool(self.mem.cpu_mem[self.addr])

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_zpix(self, pc, cycle_count): # 0xF6
        name = 'INC'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(self.mem.cpu_mem[self.addr] & 0x80)
        self.zero_flag = not bool(self.mem.cpu_mem[self.addr])

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_a(self, pc, cycle_count): # 0xEE
        name = 'INC'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(self.mem.cpu_mem[self.addr] & 0x80)
        self.zero_flag = not bool(self.mem.cpu_mem[self.addr])

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_aix(self, pc, cycle_count): # 0xFE
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = 'INC'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        tmp = self.mem.read(self.addr) + 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(self.mem.cpu_mem[self.addr] & 0x80)
        self.zero_flag = not bool(self.mem.cpu_mem[self.addr])

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# INX  -  Increment X by one
    def incr_x(self, pc, cycle_count): # 0xE8
        name = 'INX'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = (self.x_reg + 1) & 0xff
        self.sign_flag = bool(self.x_reg & 0x80)
        self.zero_flag = not bool(self.x_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# INY  -  Increment Y by one
    def incr_y(self, pc, cycle_count): # 0xC8
        name = 'INY'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = (self.y_reg + 1) & 0xff
        self.sign_flag = bool(self.y_reg & 0x80)
        self.zero_flag = not bool(self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# mis nog 1 JMP instructie
# JMP - Jump
    def jmp_a(self, pc, cycle_count): # 0x4C
        name = 'JMP'
        ext = 'A'
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        pc = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]

        cycle_count -= cycle
        return pc, cycle_count
    def jmp_ai(self, pc, cycle_count): # 0x6C
        name = 'JMP'
        ext = 'AI'
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp2 = self.mem.read(tmp)
        tmp = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + 1
        self.addr = self.mem.read(tmp)
        pc = (self.addr << 8) | tmp2

        cycle_count -= cycle
        return pc, cycle_count

# JSR - Jump to subroutine
    def jsr(self, pc, cycle_count): # 0x20
        name = 'JSR'
        ext = 'A'
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.push((pc + 1) >> 8)
        self.push(pc + 1)
        pc = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]

        cycle_count -= cycle
        return pc, cycle_count

# LDA - Load Accumulator with memory
    def load_im_a(self, pc, cycle_count): # 0xA9
        name = 'LDA'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[pc]
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_zp_a(self, pc, cycle_count): # 0xA5
        name = 'LDA'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        reg = self.mem.cpu_mem[self.addr]
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_zpix_a(self, pc, cycle_count): # 0xB5
        name = 'LDA'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        reg = self.mem.cpu_mem[self.addr]
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_a_a(self, pc, cycle_count): # 0xAD
        name = 'LDA'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_aix_a(self, pc, cycle_count): # 0xBD
        name = 'LDA'
        ext = 'AIX'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_aiy_a(self, pc, cycle_count): # 0xB9
        name = 'LDA'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg
        reg = self.mem.read(self.addr)
        self.accumulator = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def load_idi(self, pc, cycle_count): # 0xA1
        name = 'LDA'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator = self.mem.read(tmp) & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def load_ini(self, pc, cycle_count): # 0xB1
        name = 'LDA'
        ext = 'INI'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.accumulator = self.mem.read(tmp) & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# LDX - Load X with Memory
    def load_im_x(self, pc, cycle_count): # 0xA2
        name = 'LDX'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[pc]
        self.x_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def load_zp_x(self, pc, cycle_count): # 0xA6
        name = 'LDX'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        reg = self.mem.cpu_mem[self.addr]
        self.x_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def load_zpiy(self, pc, cycle_count): # 0xB6
        name = 'LDX'
        ext = 'ZPIY'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.y_reg
        reg = self.mem.cpu_mem[self.addr]
        self.x_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_a_x(self, pc, cycle_count): # 0xAE
        name = 'LDX'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        reg = self.mem.read(self.addr)
        self.x_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_aiy_x(self, pc, cycle_count): # 0xBE
        name = 'LDX'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg
        reg = self.mem.read(self.addr)
        self.x_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# LDY - Load Y with Memory
    def load_im_y(self, pc, cycle_count): # 0xA0
        name = 'LDY'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.mem.cpu_mem[pc]
        self.y_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_zp_y(self, pc, cycle_count): # 0xA4
        name = 'LDY'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_zpix_y(self, pc, cycle_count): # 0xB4
        name = 'LDY'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_a_y(self, pc, cycle_count): # 0xAC
        name = 'LDY'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        reg = self.mem.cpu_mem[self.addr]
        self.y_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def load_aix_y(self, pc, cycle_count): # 0xBC
        name = 'LDY'
        ext = 'AIX'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        reg = self.mem.read(self.addr)
        self.y_reg = reg & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# LSR  -  Logical Shift Right
    def logic_shift_r_acc(self, pc, cycle_count): # 0x4A
        name = 'LSR'
        ext = 'ACC'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = bool(self.accumulator & 0x01)
        self.accumulator = (self.accumulator >> 1) & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not self.accumulator

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_zp(self, pc, cycle_count): # 0x46
        name = 'LSR'
        ext = 'ZP'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(tmp & 0x80)
        self.zero_flag = not bool(tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_zpix(self, pc, cycle_count): # 0x56
        name = 'LSR'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(tmp & 0x80)
        self.zero_flag = not bool(tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_a(self, pc, cycle_count): # 0x4E
        name = 'LSR'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(tmp & 0x80)
        self.zero_flag = not bool(tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_aix(self, pc, cycle_count): # 0x5E
        name = 'LSR'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        tmp = self.mem.read(self.addr)
        self.carry_flag = tmp & 0x01
        tmp = tmp >> 1
        self.mem.write(self.addr, tmp)
        self.sign_flag = bool(tmp & 0x80)
        self.zero_flag = not bool(tmp)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# NOP - No Operation (79 instructies?)
    def nop(self, pc, cycle_count): # 0xEA
        name = 'NOP'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# ORA  -  OR Memory with Accumulator
    def or_mem_im(self, pc, cycle_count): # 0x09
        name = 'ORA'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator |= self.mem.cpu_mem[pc]
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_zp(self, pc, cycle_count): # 0x05
        name = 'ORA'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_zpix(self, pc, cycle_count): # 0x15
        name = 'ORA'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_a(self, pc, cycle_count): # 0x0D
        name = 'ORA'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_aix(self, pc, cycle_count): # 0x1D
        name = 'ORA'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_aiy(self, pc, cycle_count): # 0x19
        name = 'ORA'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.accumulator |= self.mem.read(self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_idi(self, pc, cycle_count): # 0x01
        name = 'ORA'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        self.accumulator |= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_ini(self, pc, cycle_count): # 0x11
        name = 'ORA'
        ext = 'INI'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]  + self.y_reg
        self.accumulator |= self.mem.read(tmp)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# PHA  -  Push Accumulator on Stack
    def push_a(self, pc, cycle_count): # 0x48
        name = 'PHA'
        ext = 'NODATA'
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.mem.write(self.stack_pointer + 0x100, self.accumulator)
        self.stack_pointer -= 1

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# PHP  -  Push Processor Status on Stack
    def push_ps(self, pc, cycle_count): # 0x08
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# PLA  -  Pull Accumulator from Stack
    def pull_a(self, pc, cycle_count): # 0x68
        name = 'PLA'
        ext = 'NODATA'
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.stack_pointer += 1
        self.accumulator = self.mem.read(self.stack_pointer + 0x100) & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# PLP  -  Pull Processor Status from Stack
    def pull_ps(self, pc, cycle_count): # 0x28
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# ROL  -  Rotate Left
    def rotate_left_acc(self, pc, cycle_count): # 0x2A
        name = 'ROL'
        ext = 'ACC'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        self.carry_flag = bool((self.accumulator >> 7) & 0x01)
        self.accumulator = (self.accumulator << 1) & 0xff
        self.accumulator |= tmp
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_zp(self, pc, cycle_count): # 0x26
        name = 'ROL'
        ext = 'ZP'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[pc]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = bool((self.addr >> 7) & 0x01)
        # TODO 
        # self.addr = (self.addr << 1) & 0xff
        self.addr = self.addr << 1
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_zpix(self, pc, cycle_count): # 0x36
        name = 'ROL'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[pc] + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = bool((self.addr >> 7) & 0x01)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_a(self, pc, cycle_count): # 0x2E
        name = 'ROL'
        ext = 'A'
        size = 3
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = bool((self.addr >> 7) & 0x01)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_aix(self, pc, cycle_count): # 0x3E
        name = 'ROL'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = bool((self.addr >> 7) & 0x01)
        self.addr = (self.addr << 1) & 0xff
        self.addr |= tmp
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# ROR  -  Rotate Right
    def rotate_right_acc(self, pc, cycle_count): # 0x6A
        name = 'ROR'
        ext = 'ACC'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        self.carry_flag = self.accumulator & 0x01
        self.accumulator = (self.accumulator >> 1) & 0xff
        if tmp:
            self.accumulator |= 0x80
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_zp(self, pc, cycle_count): # 0x66
        name = 'ROR'
        ext = 'ZP'
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[pc]
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_zpix(self, pc, cycle_count): # 0x76
        name = 'ROR'
        ext = 'ZPIX'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = self.mem.cpu_mem[pc] + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_a(self, pc, cycle_count): # 0x6E
        name = 'ROR'
        ext = 'A'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc])
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_aix(self, pc, cycle_count): # 0x7E
        name = 'ROR'
        ext = 'AIX'
        size = 3
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        tmp = self.carry_flag
        tmp2 = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        self.addr = self.mem.read(tmp2)
        self.carry_flag = self.addr & 0x01
        self.addr = self.addr >> 1
        if tmp:
            self.addr |= 0x80
        self.mem.write(tmp2, self.addr)
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# RTI  -  Return from Interrupt
    def ret_int(self, pc, cycle_count): # 0x40
        name = 'RTI'
        ext = 'NODATA'
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.pull()
        self.set_sr(self.addr)
        self.pull()
        pc = self.addr
        self.pull()
        pc += (self.addr << 8)

        cycle_count -= cycle
        return pc, cycle_count

# RTS  -  Return from Subroutine
    def ret_sub(self, pc, cycle_count): # 0x60
        name = 'RTS'
        ext = 'NODATA'
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.pull()
        pc = self.addr + 1 
        self.pull()
        pc += (self.addr << 8)

        cycle_count -= cycle
        return pc, cycle_count

# SBC  -  Subtract from Accumulator with Carry (IDI_ZP?)
    def sub_acc_im(self, pc, cycle_count): # 0xE9
        name = 'SBC'
        ext = 'IM'
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        # TODO if self.dbg_cnt > 228922:
        # tmp = self.accumulator - self.addr - int(not self.carry_flag
        tmp = (self.accumulator - self.addr - int(not self.carry_flag) & 0xffffffff)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_zp(self, pc, cycle_count): # 0xE5
        name = 'SBC'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[pc])
        tmp = self.accumulator - self.addr - int(not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_zpix(self, pc, cycle_count): # 0xF5
        name = 'SBC'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(self.mem.cpu_mem[pc] + self.x_reg)
        # TODO self.dbg_cnt: 385423
        #tmp = self.accumulator - self.addr - int(not self.carry_flag)
        tmp = (self.accumulator - self.addr - int(not self.carry_flag)) & 0xffffffff
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_a(self, pc, cycle_count): # 0xED
        name = 'SBC'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc])
        tmp = self.accumulator - self.addr - int(not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_aix(self, pc, cycle_count): # 0xFD
        name = 'SBC'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg)
        tmp = self.accumulator - self.addr - int(not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = tmp <= 0xff
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_aiy(self, pc, cycle_count): # 0xF9
        name = 'SBC'
        ext = 'AIY'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.read(((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg)
        tmp = self.accumulator - self.addr - (not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ self.addr)) & (self.accumulator ^ self.addr) & 0x80)
        self.carry_flag = bool(tmp <= 0xff)
        self.accumulator = tmp & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not self.accumulator

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_idi(self, pc, cycle_count): # 0xE1
        name = 'SBC'
        ext = 'IDI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc] + self.x_reg
        tmp = (self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator - tmp2 - int(not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80)
        self.carry_flag = bool(tmp3 <= 0xff)
        self.accumulator = tmp3 & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not self.accumulator

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_ini(self, pc, cycle_count): # 0xF1
        name = 'SBC'
        ext = 'INI'
        size = 2
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        tmp2 = self.mem.read(tmp)
        tmp3 = self.accumulator - tmp2 - int(not self.carry_flag)
        self.overflow_flag = bool((~(self.accumulator ^ tmp2)) & (self.accumulator ^ tmp2) & 0x80)
        self.carry_flag = bool(tmp3 <= 0xff)
        self.accumulator = tmp3 & 0xff
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not self.accumulator

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# SEC  -  Set Carry Flag
    def set_c_flag(self, pc, cycle_count): # 0x38
        name = 'SEC'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.carry_flag = True

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# SED  -  Set Decimal Mode
    def set_d_mode(self, pc, cycle_count): # 0xF8
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# SEI - Set Interrupt Disable
    def set_int_dis(self, pc, cycle_count): # 0x78
        name = 'SEI'
        ext = "NODATA"
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.interrupt_flag = 1

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# STA - Store Accumulator in Memory (IDI_ZP?)
    def store_zp_a(self, pc, cycle_count): # 0x85
        name = 'STA'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_zpix_a(self, pc, cycle_count): # 0x95
        name = 'STA'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.mem.write(self.addr, self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_a_a(self, pc, cycle_count): # 0x8D
        name = 'STA'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        reg = self.accumulator
        self.mem.write(self.addr, reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def store_aix(self, pc, cycle_count): # 0x9D
        name = 'STA'
        ext = 'AIX'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.x_reg
        reg = self.accumulator
        self.mem.write(self.addr, reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_aiy(self, pc, cycle_count): # 0x99
        name = 'STA'
        ext = 'AIY'
        size = 3
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = ((self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]) + self.y_reg
        self.mem.write(self.addr, self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_idi(self, pc, cycle_count): # 0x81
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_ini(self, pc, cycle_count): # 0x91
        name = 'STA'
        ext = 'INI'
        size = 2
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[pc]
        tmp = ((self.mem.cpu_mem[self.addr + 1] << 8) | self.mem.cpu_mem[self.addr]) + self.y_reg
        self.mem.write(tmp, self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# STX - Store X in Memory
    def store_zp_x(self, pc, cycle_count): # 0x86
        name = 'STX'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.x_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

    def store_zpiy(self, pc, cycle_count): # 0x96
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_a_x(self, pc, cycle_count): # 0x8E
        name = 'STX'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.mem.write(self.addr, self.x_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# STY - Store Y in Memory
    def store_zp_y(self, pc, cycle_count): # 0x84
        name = 'STY'
        ext = 'ZP'
        size = 2
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter]
        self.mem.write(self.addr, self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_zpix(self, pc, cycle_count): # 0x94
        name = 'STY'
        ext = 'ZPIX'
        size = 2
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = self.mem.cpu_mem[self.program_counter] + self.x_reg
        self.mem.write(self.addr, self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count
    def store_a_y(self, pc, cycle_count): # 0x8C
        name = 'STY'
        ext = 'A'
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.addr = (self.mem.cpu_mem[pc + 1] << 8) | self.mem.cpu_mem[pc]
        self.mem.write(self.addr, self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TAX  -  Transfer Accumulator to X
    def transfer_reg_x(self, pc, cycle_count): # 0xAA
        name = 'TAX'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.x_reg = self.accumulator
        self.sign_flag = bool(self.x_reg & 0x80)
        self.zero_flag = not bool(self.x_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TAY  -  Transfer Accumulator to Y
    def transfer_reg_y(self, pc, cycle_count): # 0xA8
        name = 'TAY'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.y_reg = self.accumulator
        self.sign_flag = bool(self.y_reg & 0x80)
        self.zero_flag = not bool(self.y_reg)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TSX  -  Transfer Stack to X
    def transfer_stack_from(self, pc, cycle_count): # 0xBA
        print(" ### OPCODE: 0x%x @ 0x%04x has not implemented yet!"%(self.mem.cpu_mem[self.program_counter - 1], self.program_counter - 1))
        exit()
        name = ''
        ext = ''
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)
        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TXA  -  Transfer X to Accumulator
    def transfer_reg_xa(self, pc, cycle_count): # 0x8A
        name = 'TXA'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator = self.x_reg
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TXS  -  Transfer X to Stack
    def transfer_stack_to(self, pc, cycle_count): # 0x9A
        name = 'TXS'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        reg = self.x_reg
        self.stack_pointer = (reg + 0x100) & 0xff
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

# TYA  -  Transfer Y to Accumulator
    def transfer_reg_ya(self, pc, cycle_count): # 0x98
        name = 'TYA'
        ext = 'NODATA'
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, name, ext)

        self.accumulator = self.y_reg
        self.sign_flag = bool(self.accumulator & 0x80)
        self.zero_flag = not bool(self.accumulator)

        pc += size - 1
        cycle_count -= cycle
        return pc, cycle_count

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
        #print(" -- CPU Execute -- Start cycles: %d"%(cycles))
        cycle_count = round(cycles)
        while(cycle_count > 0):
            self.dbg_cnt += 1
            self.update_status_reg()
            op = self.mem.cpu_mem[self.program_counter]
            self.program_counter += 1
            #print(' -- CPU Execute -- cnt: %d, pc: 0x%x, instruction: 0x%x'%(cycle_count, self.program_counter, op))
            #print(' -- CPU Execute -- [%d] loopyT: %x, loopyV: %x, loopyX: %x, ppu_status: %x'%(self.nes.cpu.dbg_cnt, self.nes.ppu.loopyT, self.nes.ppu.loopyV, self.nes.ppu.loopyX, self.nes.ppu.status))
            if (op in self.opcode):
                self.program_counter, cycle_count = self.opcode[op](self, self.program_counter, cycle_count)
            else:
                cycle_count -= 1
                print(' ### OpCode 0x%x @ 0x%xis not supported!!!'%(op, self.program_counter))
                exit()

        return cycles - cycle_count

