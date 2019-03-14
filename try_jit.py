#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numba as nb
import numpy as np

node_type = nb.deferred_type()
spec = [
        ('accumulator', nb.int32),
        ('programcounter', nb.int32),
        ('zeroflag', nb.boolean),
        #('mem', nb.optional(node_type)),
        ('ppu_mem', nb.int8[:]),
        ]

@nb.jitclass(spec)
class JIT_CPU():
    def __init__(self, mem):
        #self.mem = mem
        self.accumulator = 0
        self.programcounter = 0
        self.zeroflag = bool(0)
        self.ppu_mem = mem

    def excute(self):
        self.programcounter += 1
        self.ppu_mem[10] += 1

spec = [
        ('cpu_mem', nb.int8[:]),
        ('addr', nb.int16),
        ('data', nb.int8),
        ]

@nb.jitclass(spec)
class JIT_MEM():
    def __init__(self):
        # 64k main memory
        self.cpu_mem = np.zeros(64*1024, dtype=np.uint8)
        self.addr = 0
        self.data = 0

    def write(self, a, d):
        self.addr = a 
        self.data = d

node_type.define(JIT_MEM.class_type.instance_type)

spec = [
        ('looyV', nb.int32),
        ('looyX', nb.int32),
        ]

@nb.jitclass(spec)
class JIT_PPU():
    def __init__(self):
        self.looyV = 0
        self.looyX = 0

    def render_bg(self):
        self.looyV += 1


if __name__ == '__main__':
    mem = JIT_MEM()
    cpu = JIT_CPU(mem.cpu_mem)
    ppu = JIT_PPU()
    mem.cpu_mem[0] = 1
    cpu.excute()
    ppu.render_bg()
    mem.write(1, 1)
