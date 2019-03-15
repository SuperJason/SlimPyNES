#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

cpu_mem = np.zeros(64*1024, dtype=np.uint8)

def mem_write(addr, data):
    cpu_mem[addr] = data

def mem_read(addr):
    return cpu_mem[addr]
