#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

if __name__ == '__main__':
    bit1 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
    bit2 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
    mem = np.arange(16)
    print('mem:')
    print(mem)
    for i in range(8)[::-1]:
        for j in range(8):
            bit1[7 - i][j] = bool((mem[j] >> i) & 0x01)
            bit2[7 - i][j] = bool((mem[8 + j] >> i) & 0x01)

    print('bit1:')
    print(bit1)
    print('bit2:')
    print(bit2)

    print('transpose: bit1:')
    print(np.transpose(bit1))
    print('transpose: bit2:')
    print(np.transpose(bit2))

    bit1 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
    bit2 = np.zeros(8 * 16, np.uint8).reshape(8, 16)
    print('bit1:')
    print(bit1)
    print('bit2:')
    print(bit2)
    tmp = (1 << np.arange(8))
    print('tmp:')
    print(tmp)
    ones = np.ones(64, dtype=np.uint8).reshape(8, 8)
    print('ones:')
    print(ones)
    print('tmp * ones:')
    print(tmp * ones)
    #mem[0:3] = 7
    print('mem[0:8]:')
    print(mem[0:8])
    print('(tmp * ones).T & mem[0:8]:')
    print((((tmp * ones).T & mem[0:8]) > 0) * 1)
    bit1[::-1,0:8] = (((tmp * ones).T & mem[0:8]) > 0) * 1
    print('bit1:')
    print(bit1)
    a = np.arange(8*16).reshape(8, 16)
    print('a:')
    print(a)
    print('a[:, 0:8]:')
    print(a[:, 0:8])
    print('a[:, 7:1:-1]:')
    print(a[:, 7:1:-1])
