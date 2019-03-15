#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mem import cpu_mem, mem_write, mem_read
import numba as na
from collections import OrderedDict

spec = OrderedDict()
spec['status_reg'] = na.uint8
spec['zero_flag'] = na.boolean
spec['sign_flag'] = na.boolean
spec['overflow_flag'] = na.boolean
spec['break_flag'] = na.boolean
spec['decimal_flag'] = na.boolean
spec['interrupt_flag'] = na.boolean
spec['carry_flag'] = na.boolean
spec['stack_pointer'] = na.uint8
spec['program_counter'] = na.uint16
spec['accumulator'] = na.uint8
spec['x_reg'] = na.uint8
spec['y_reg'] = na.uint8
spec['addr'] = na.uint8
spec['dbg_cnt'] = na.uint32
spec['DBG_OPCODE'] = na.uint32
spec['debug'] = na.uint32

@na.jitclass(spec)
class CPU():
    def __init__(self):
        self.status_reg = 0x20
        self.zero_flag = bool(1)
        self.sign_flag = bool(0)
        self.overflow_flag = bool(0)
        self.break_flag = bool(0)
        self.decimal_flag = bool(0)
        self.interrupt_flag = bool(0)
        self.carry_flag = bool(0)

        self.stack_pointer = 0xff
        self.program_counter = (cpu_mem[0xfffd] << 8) | cpu_mem[0xfffc]
        self.accumulator = 0x0

        self.x_reg = 0x0
        self.y_reg = 0x0
        self.addr = 0

        self.dbg_cnt = 0

        self.DBG_OPCODE = 0x0001
        self.debug = 0

# Stack Push
def cpu_push(cpu, data):
    mem_write(cpu.stack_pointer + 0x100, data)
    cpu.stack_pointer -= 1

# Stack Pull
def cpu_pull(cpu):
    cpu.stack_pointer += 1
    cpu.addr = mem_read(cpu.stack_pointer + 0x100)

# Get the cpu flags
def cpu_get_sr(cpu):
    flags = 0
    if cpu.sign_flag:
        flags |= 0x80
    if cpu.overflow_flag:
        flags |= 0x40
    if cpu.break_flag:
        flags |= 0x10
    if cpu.decimal_flag:
        flags |= 0x08
    if cpu.interrupt_flag:
        flags |= 0x04
    if cpu.zero_flag:
        flags |= 0x02
    if cpu.carry_flag:
        flags |= 0x01
    return flags

# Set the cpu flags
def cpu_set_sr(cpu, flags):
    cpu.sign_flag = bool(flags & 0x80)
    cpu.overflow_flag = bool(flags & 0x40)
    cpu.break_flag = bool((flags & 0x10) | 0x20)
    cpu.decimal_flag = bool(flags & 0x08)
    cpu.interrupt_flag = bool(flags & 0x04)
    cpu.zero_flag = bool(flags & 0x02)
    cpu.carry_flag = bool(flags & 0x01)

@na.njit
def cpu_update_status_reg(cpu):
    cpu.status_reg = 0x20
    if cpu.sign_flag:
        cpu.status_reg |= 0x80
    if cpu.overflow_flag:
        cpu.status_reg |= 0x40
    if cpu.break_flag:
        cpu.status_reg |= 0x10
    if cpu.decimal_flag:
        cpu.status_reg |= 0x08
    if cpu.interrupt_flag:
        cpu.status_reg |= 0x04
    if cpu.zero_flag:
        cpu.status_reg |= 0x02
    if cpu.carry_flag:
        cpu.status_reg |= 0x01

def cpu_reset(cpu):
    status_reg = 0x20
    zero_flag = bool(1)
    sign_flag = bool(0)
    overflow_flag = bool(0)
    break_flag = bool(0)
    decimal_flag = bool(0)
    interrupt_flag = bool(0)
    carry_flag = bool(0)

    stack_pointer = 0xff
    program_counter = (cpu_mem[0xfffd] << 8) | cpu_mem[0xfffc]

    accumulator=0x0
    x_reg=0x0
    y_reg=0x0
    print(' -- CPU Reset --')
    return 1

def brk(cpu): # 0x00
    size = 1
    cycle = 7
    if cpu.debug & cpu.DBG_OPCODE:
        name = 'BRK'
        ext = 'NODATA'
        cpu_opcode_dbg_prt(size, cycle, name, ext)

    cpu.program_counter += 1
    cpu.break_flag = True
    cpu_push(cpu, (cpu.program_counter & 0xff00) >> 8)
    cpu_push(cpu, cpu.program_counter & 0xff)
    cpu_push(cpu, cpu_get_sr(cpu))
    cpu.interrupt_flag = True
    cpu.program_counter = (cpu_mem[0xffff] << 8) | cpu_mem[0xfffe];

    return cycle

def or_mem_idi(cpu): # 0x01
    size = 2
    cycle = 6
    if cpu.debug & cpu.DBG_OPCODE:
        name = 'BRK'
        ext = 'NODATA'
        cpu_opcode_dbg_prt(size, cycle, name, ext)

    cpu.addr = cpu_mem[cpu.program_counter] + x_reg
    tmp = (cpu_mem[cpu.addr + 1] << 8) | cpu_mem[cpu.addr]
    cpu.accumulator |= mem_read(tmp)
    cpu.sign_flag = ((cpu.accumulator & 0x80) != 0)
    cpu.zero_flag = ((cpu.accumulator) == 0)

    cpu.program_counter += size - 1
    return cycle

opcode = {
        0x00: brk,
        0x01: or_mem_idi,
        }

@na.njit
def cpu_execute(cpu, cycles = 1):
    op = cpu_mem[cpu.program_counter]
    b = op_code[1]

@na.njit
def _cpu_execute(cpu, cycles = 1):
    cycle_count = round(cycles)
    while(cycle_count > 0):
        cpu.dbg_cnt += 1
        cpu_update_status_reg(cpu)
        op = cpu_mem[cpu.program_counter]
        cpu.program_counter += 1
        if (op in opcode):
            cycle_count -= opcode[op](cpu)
        else:
            cycle_count -= 1
            print(' ### OpCode 0x%x @ 0x%xis not supported!!!'%(op, cpu.program_counter))
            exit()

    return cycles - cycle_count

