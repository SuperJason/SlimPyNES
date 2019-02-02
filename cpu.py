#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class CPU():
    DBG_OPCODE = 0x01
    def __init__(self, mem):
        self.mem = mem
        self.debug = self.DBG_OPCODE 

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

    def opcode_dbg_prt(self, size, cycle, pc, str):
        op = self.mem.cpu_mem[pc]
        print(' >-> S: %d - C: %d - OP: %X @ PC: %X - '%(size, cycle, op, pc) + str)

# ----- OpCode Functions -----
# ADC  -  Add to Accumulator with Carry 
    def adc_im(self, pc, cycle_count): # 0x69
        addr = self.mem.cpu_mem[pc + 1]
        tmp = addr + self.accumulator + self.carry_flag
        self.overflow_flag = bool((~(self.accumulator ^ addr)) & (self.accumulator ^ addr) & 0x80)
        if tmp > 0xff: 
            self.carry_flag = bool(1)
        else:
            self.carry_flag = bool(0)
        reg = self.accumulator
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg

        dbg_str = "ADC IM "
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        exit()
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_zp(self, pc, cycle_count): # 0x65
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_zpix(self, pc, cycle_count): # 0x75
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_a(self, pc, cycle_count): # 0x6D
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_aix(self, pc, cycle_count): # 0x7D
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_aiy(self, pc, cycle_count): # 0x79
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_idi(self, pc, cycle_count): # 0x61
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def adc_ini(self, pc, cycle_count): # 0x71
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# AND  -  AND Memory with Accumulator 
    def and_im(self, pc, cycle_count): # 0x29
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_zp(self, pc, cycle_count): # 0x25
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_zpix(self, pc, cycle_count): # 0x35
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_a(self, pc, cycle_count): # 0x2D
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_aix(self, pc, cycle_count): # 0x3D
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_aiy(self, pc, cycle_count): # 0x39
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_idi(self, pc, cycle_count): # 0x21
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def and_ini(self, pc, cycle_count): # 0x31
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# ASL  -  Arithmatic Shift Left 
    def arith_sl_acc(self, pc, cycle_count): # 0x0A
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_zp(self, pc, cycle_count): # 0x06
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_zpix(self, pc, cycle_count): # 0x16
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_a(self, pc, cycle_count): # 0x0E
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def arith_sl_aix(self, pc, cycle_count): # 0x1E
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BCC  -  Branch on Carry Clear 
    def branch_cc(self, pc, cycle_count): # 0x90
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BCS  -  Branch on Carry Set 
    def branch_cs(self, pc, cycle_count): # 0xB0
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BEQ  -  Branch Zero Set 
    def branch_zs(self, pc, cycle_count): # 0xF0
        op = self.mem.cpu_mem[pc]
        print('pc: 0x%x, instruction: 0x%x'%(pc, op))
        if self.zero_flag:
            pc += self.mem.cpu_mem[pc + 1] + 1
        else:
            exit()
        cycle_count -= 2
        return pc, cycle_count

# note: bit moet 5 instr zijn ipv 2? 
# BIT  -  Test Bits in Memory with Accumulator 
    def bit_test_zp(self, pc, cycle_count): # 0x24
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def bit_test_a(self, pc, cycle_count): # 0x2C
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BMI  -  Branch on Result Minus 
    def branch_rm(self, pc, cycle_count): # 0x30
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BNE  -  Branch on Z reset 
    def branch_zr(self, pc, cycle_count): # 0xD0
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BPL  -  Branch on Result Plus (or Positive) 
    def branch_rp(self, pc, cycle_count): # 0x10
        if not self.sign_flag:
            pc += self.mem.cpu_mem[pc + 1] + 1
        cycle_count -= 2
        return pc, cycle_count

# BRK  -  Force a Break 
    def brk(self, pc, cycle_count): # 0x00
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BVC  -  Branch on Overflow Clear 
    def branch_oc(self, pc, cycle_count): # 0x50
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# BVS  -  Branch on Overflow Set 
    def branch_os(self, pc, cycle_count): # 0x70
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CLC  -  Clear Carry Flag 
    def clear_cf(self, pc, cycle_count): # 0x18
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CLD  -  Clear Decimal Mode 
    def clear_dm(self, pc, cycle_count): # 0xD8
        self.decimal_flag = 0
        dbg_str = "CLD"
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CLI  -  Clear Interrupt Disable 
    def clear_id(self, pc, cycle_count): # 0x58
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CLV  -  Clear Overflow Flag 
    def clear_of(self, pc, cycle_count): # 0xB8
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CMP  -  Compare Memory and Accumulator 
    def comp_mem_im(self, pc, cycle_count): # 0xC9
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xC5
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zpix(self, pc, cycle_count): # 0xD5
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xCD
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_aix(self, pc, cycle_count): # 0xDD
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_aiy(self, pc, cycle_count): # 0xD9
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_idi(self, pc, cycle_count): # 0xC1
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_ini(self, pc, cycle_count): # 0xD1
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CPX  -  Compare Memory and X register 
    def comp_mem_im(self, pc, cycle_count): # 0xE0
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xE4
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xEC
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# CPY  -  Compare Memory and Y register 
    def comp_mem_im(self, pc, cycle_count): # 0xC0
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xC4
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xCC
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# DEC  -  Decrement Memory by One 
    def decr_mem_zp(self, pc, cycle_count): # 0xC6
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_zpix(self, pc, cycle_count): # 0xD6
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_a(self, pc, cycle_count): # 0xCE
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def decr_mem_aix(self, pc, cycle_count): # 0xDE
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# DEX  -  Decrement X 
    def decr(self, pc, cycle_count): # 0xCA
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# DEY  -  Decrement Y 
    def decr(self, pc, cycle_count): # 0x88
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# EOR  -  Exclusive-OR Memory with Accumulator 
    def excl_or_mem_im(self, pc, cycle_count): # 0x49
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_zp(self, pc, cycle_count): # 0x45
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_zpix(self, pc, cycle_count): # 0x55
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_a(self, pc, cycle_count): # 0x4D
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_aix(self, pc, cycle_count): # 0x5D
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_aiy(self, pc, cycle_count): # 0x59
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_idi(self, pc, cycle_count): # 0x41
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def excl_or_mem_ini(self, pc, cycle_count): # 0x51
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# INC  -  Increment Memory by one 
    def incr_mem_zp(self, pc, cycle_count): # 0xE6
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_zpix(self, pc, cycle_count): # 0xF6
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_a(self, pc, cycle_count): # 0xEE
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def incr_mem_aix(self, pc, cycle_count): # 0xFE
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# INX  -  Increment X by one 
    def incr(self, pc, cycle_count): # 0xE8
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# INY  -  Increment Y by one 
    def incr(self, pc, cycle_count): # 0xC8
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# mis nog 1 JMP instructie 
# JMP - Jump 
    def jmp_a(self, pc, cycle_count): # 0x4c
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def jmp_ai(self, pc, cycle_count): # 0x6c
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# JSR - Jump to subroutine 
    def jsr(self, pc, cycle_count): # 0x20
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# LDA - Load Accumulator with memory 
    def load_im(self, pc, cycle_count): # 0xA9, 0xA2, 0xA0
        reg = self.mem.cpu_mem[pc + 1]
        if self.mem.cpu_mem[pc] == 0xa9:
            self.accumulator = reg
            dbg_str = "LDA #%X"%(reg)
        elif self.mem.cpu_mem[pc] == 0xa2:
            self.x_reg = reg
            dbg_str = "LDX #%X"%(reg)
        elif self.mem.cpu_mem[pc] == 0xa0:
            self.y_reg = reg
            dbg_str = "LDY #%X"%(reg)
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg
        size = 2
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_zp(self, pc, cycle_count): # 0xA5
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_zpix(self, pc, cycle_count): # 0xB5
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_a(self, pc, cycle_count): # 0xAD, 0xAE, 0xAC
        addr = (self.mem.cpu_mem[pc + 2] << 8) | self.mem.cpu_mem[pc + 1]
        if self.mem.cpu_mem[pc] == 0xad:
            reg = self.accumulator
        elif self.mem.cpu_mem[pc] == 0xae:
            reg = self.x_reg
        elif self.mem.cpu_mem[pc] == 0xac:
            reg = self.y_reg
        self.mem.cpu_mem[addr] = reg
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_aix(self, pc, cycle_count): # 0xBD, 0xBC
        addr = (self.mem.cpu_mem[pc + 2] << 8) | self.mem.cpu_mem[pc + 1]
        reg = self.mem.cpu_mem[addr]
        if self.mem.cpu_mem[pc] == 0xbd:
            self.accumulator = reg
        elif self.mem.cpu_mem[pc] == 0xbc:
            self.y_reg = reg
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_aiy(self, pc, cycle_count): # 0xB9
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def load_idi(self, pc, cycle_count): # 0xA1
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def load_ini(self, pc, cycle_count): # 0xB1
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# LDX - Load X with Memory 
    def load_zp(self, pc, cycle_count): # 0xA6
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def load_zpiy(self, pc, cycle_count): # 0xB6
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

#    def load_a(self, pc, cycle_count): # 0xAE

    def load_aiy(self, pc, cycle_count): # 0xBE
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# LDY - Load Y with Memory 
    def load_zp(self, pc, cycle_count): # 0xA4
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

    def load_zpix(self, pc, cycle_count): # 0xB4
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

#    def load_a(self, pc, cycle_count): # 0xAC

#    def load_aix(self, pc, cycle_count): # 0xBC

# LSR  -  Logical Shift Right 
    def logic_shift_r_acc(self, pc, cycle_count): # 0x4A
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_zp(self, pc, cycle_count): # 0x46
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_zpix(self, pc, cycle_count): # 0x56
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_a(self, pc, cycle_count): # 0x4E
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def logic_shift_r_aix(self, pc, cycle_count): # 0x5E
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# NOP - No Operation (79 instructies?) 
    def nop(self, pc, cycle_count): # 0xEA
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# ORA  -  OR Memory with Accumulator 
    def or_mem_im(self, pc, cycle_count): # 0x09
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_zp(self, pc, cycle_count): # 0x05
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_zpix(self, pc, cycle_count): # 0x15
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_a(self, pc, cycle_count): # 0x0D
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_aix(self, pc, cycle_count): # 0x1D
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_aiy(self, pc, cycle_count): # 0x19
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_idi(self, pc, cycle_count): # 0x01
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def or_mem_ini(self, pc, cycle_count): # 0x11
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# PHA  -  Push Accumulator on Stack 
    def push_a(self, pc, cycle_count): # 0x48
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# PHP  -  Push Processor Status on Stack 
    def push_ps(self, pc, cycle_count): # 0x08
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# PLA  -  Pull Accumulator from Stack 
    def pull_a(self, pc, cycle_count): # 0x68
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# PLP  -  Pull Processor Status from Stack 
    def pull_ps(self, pc, cycle_count): # 0x28
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# ROL  -  Rotate Left 
    def rotate_left_acc(self, pc, cycle_count): # 0x2A
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_zp(self, pc, cycle_count): # 0x26
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_zpix(self, pc, cycle_count): # 0x36
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_a(self, pc, cycle_count): # 0x2E
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_left_aix(self, pc, cycle_count): # 0x3E
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# ROR  -  Rotate Right 
    def rotate_right_acc(self, pc, cycle_count): # 0x6A
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_zp(self, pc, cycle_count): # 0x66
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_zpix(self, pc, cycle_count): # 0x76
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_a(self, pc, cycle_count): # 0x6E
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def rotate_right_aix(self, pc, cycle_count): # 0x7E
        exit()
        size = 1
        cycle = 7
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# RTI  -  Return from Interrupt 
    def ret_int(self, pc, cycle_count): # 0x40
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# RTS  -  Return from Subroutine 
    def ret_sub(self, pc, cycle_count): # 0x60
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# SBC  -  Subtract from Accumulator with Carry (IDI_ZP?) 
    def sub_acc_im(self, pc, cycle_count): # 0xE9
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_zp(self, pc, cycle_count): # 0xE5
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_zpix(self, pc, cycle_count): # 0xF5
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_a(self, pc, cycle_count): # 0xED
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_aix(self, pc, cycle_count): # 0xFD
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_aiy(self, pc, cycle_count): # 0xF9
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_idi(self, pc, cycle_count): # 0xE1
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def sub_acc_ini(self, pc, cycle_count): # 0xF1
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# SEC  -  Set Carry Flag 
    def set_c_flag(self, pc, cycle_count): # 0x38
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# SED  -  Set Decimal Mode 
    def set_d_mode(self, pc, cycle_count): # 0xF8
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# SEI - Set Interrupt Disable 
    def set_int_dis(self, pc, cycle_count): # 0x78
        self.interrupt_flag = 1
        dbg_str = "SEI"
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# STA - Store Accumulator in Memory (IDI_ZP?) 
    def store_zp(self, pc, cycle_count): # 0x85
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_zpix(self, pc, cycle_count): # 0x95
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_a(self, pc, cycle_count): # 0x8D, 0x8E, 0x8C
        addr = (self.mem.cpu_mem[pc + 2] << 8) | self.mem.cpu_mem[pc + 1]
        if self.mem.cpu_mem[pc] == 0x8d:
            reg = self.accumulator
            dbg_str = "LDA #%X"%(reg)
        elif self.mem.cpu_mem[pc] == 0x8e:
            reg = self.x_reg
        elif self.mem.cpu_mem[pc] == 0x8c:
            self.mem.cpu_mem[addr] = self.y_reg
        self.mem.cpu_mem[addr] = reg
        size = 3
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_aix(self, pc, cycle_count): # 0x9D
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_aiy(self, pc, cycle_count): # 0x99
        exit()
        size = 1
        cycle = 5
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_idi(self, pc, cycle_count): # 0x81
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_ini(self, pc, cycle_count): # 0x91
        exit()
        size = 1
        cycle = 6
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# STX - Store X in Memory 
    def store_zp(self, pc, cycle_count): # 0x86
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_zpiy(self, pc, cycle_count): # 0x96
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
#    def store_a(self, pc, cycle_count): # 0x8E

# STY - Store Y in Memory 
    def store_zp(self, pc, cycle_count): # 0x84
        exit()
        size = 1
        cycle = 3
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
    def store_zpix(self, pc, cycle_count): # 0x94
        exit()
        size = 1
        cycle = 4
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count
#    def store_a(self, pc, cycle_count): # 0x8C

# TAX  -  Transfer Accumulator to X 
    def transfer_reg(self, pc, cycle_count): # 0xAA
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# TAY  -  Transfer Accumulator to Y 
    def transfer_reg(self, pc, cycle_count): # 0xA8
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# TSX  -  Transfer Stack to X 
    def transfer_stack_from(self, pc, cycle_count): # 0xBA
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# TXA  -  Transfer X to Accumulator 
    def transfer_reg(self, pc, cycle_count): # 0x8A
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# TXS  -  Transfer X to Stack 
    def transfer_stack_to(self, pc, cycle_count): # 0x9A
        reg = self.x_reg
        self.stack_pointer = reg + 100
        self.sign_flag = bool(reg & 0x80)
        self.zero_flag = not reg
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
        cycle_count -= cycle
        return pc, cycle_count

# TYA  -  Transfer Y to Accumulator 
    def transfer_reg(self, pc, cycle_count): # 0x98
        exit()
        size = 1
        cycle = 2
        if bool(self.debug & self.DBG_OPCODE):
            self.opcode_dbg_prt(size, cycle, pc, dbg_str)
        pc += size
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
            0x84: store_zp,
            0x85: store_zp,
            0x86: store_zp,
            0x88: decr,
            0x8a: transfer_reg,
            0x8c: store_a,
            0x8d: store_a,
            0x8e: store_a,
            0x90: branch_cc,
            0x91: store_ini,
            0x94: store_zpix,
            0x95: store_zpix,
            0x96: store_zpiy,
            0x98: transfer_reg,
            0x99: store_aiy,
            0x9a: transfer_stack_to,
            0x9d: store_aix,
            0xa0: load_im,
            0xa1: load_idi,
            0xa2: load_im,
            0xa4: load_zp,
            0xa5: load_zp,
            0xa6: load_zp,
            0xa8: transfer_reg,
            0xa9: load_im,
            0xaa: transfer_reg,
            0xac: load_a,
            0xad: load_a,
            0xae: load_a,
            0xb0: branch_cs,
            0xb1: load_ini,
            0xb4: load_zpix,
            0xb5: load_zpix,
            0xb6: load_zpiy,
            0xb8: clear_of,
            0xb9: load_aiy,
            0xba: transfer_stack_from,
            0xbc: load_aix,
            0xbd: load_aix,
            0xbe: load_aiy,
            0xc0: comp_mem_im,
            0xc1: comp_mem_idi,
            0xc4: comp_mem_zp,
            0xc5: comp_mem_zp,
            0xc6: decr_mem_zp,
            0xc8: incr,
            0xc9: comp_mem_im,
            0xca: decr,
            0xcc: comp_mem_a,
            0xcd: comp_mem_a,
            0xce: decr_mem_a,
            0xd0: branch_zr,
            0xd1: comp_mem_ini,
            0xd5: comp_mem_zpix,
            0xd6: decr_mem_zpix,
            0xd8: clear_dm,
            0xd9: comp_mem_aiy,
            0xdd: comp_mem_aix,
            0xde: decr_mem_aix,
            0xe0: comp_mem_im,
            0xe1: sub_acc_idi,
            0xe4: comp_mem_zp,
            0xe5: sub_acc_zp,
            0xe6: incr_mem_zp,
            0xe8: incr,
            0xe9: sub_acc_im,
            0xea: nop,
            0xec: comp_mem_a,
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

    def execute(self, cycle_count = 1):
        pc = self.program_counter
        while(cycle_count > 0):
            op = self.mem.cpu_mem[pc]
            print(' -- CPU Execute -- cnt: %d, pc: 0x%x, instruction: 0x%x'%(cycle_count, pc, op))
            if (op in self.opcode):
                pc, cycle_count = self.opcode[op](self, pc, cycle_count)
            else:
                pc += 1
                cycle_count -= 1
                print(' ### OpCode 0x%x is not supported'%(op))
        self.program_counter = pc

