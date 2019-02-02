#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np

class MEMORY():
    def __init__(self):
        # 64k main memory
        self.cpu_mem = np.ones(64*1024, dtype=np.uint8)
        # 16k video memory
        self.ppu_mem = np.ones(16*1024, dtype=np.uint8)
        # 256b sprite memory 
        self.sprite_mem = np.ones(256, dtype=np.uint8)
        self.tital = ''

