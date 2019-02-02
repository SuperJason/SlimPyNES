# ADC  -  Add to Accumulator with Carry 
    def dc_im(self, pc, cycle_count): # 0x69
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def adc_zp(self, pc, cycle_count): # 0x65
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def adc_zpix(self, pc, cycle_count): # 0x75
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def adc_a(self, pc, cycle_count): # 0x6D
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def adc_aix(self, pc, cycle_count): # 0x7D
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def adc_aiy(self, pc, cycle_count): # 0x79
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def adc_idi(self, pc, cycle_count): # 0x61
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def adc_ini(self, pc, cycle_count): # 0x71
        exit()
        cycle_count -= 5
        return pc, cycle_count

# AND  -  AND Memory with Accumulator 
    def and_im(self, pc, cycle_count): # 0x29
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def and_zp(self, pc, cycle_count): # 0x25
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def and_zpix(self, pc, cycle_count): # 0x35
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def and_a(self, pc, cycle_count): # 0x2D
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def and_aix(self, pc, cycle_count): # 0x3D
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def and_aiy(self, pc, cycle_count): # 0x39
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def and_idi(self, pc, cycle_count): # 0x21
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def and_ini(self, pc, cycle_count): # 0x31
        exit()
        cycle_count -= 5
        return pc, cycle_count

# ASL  -  Arithmatic Shift Left 
    def arith_sl_acc(self, pc, cycle_count): # 0x0A
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def arith_sl_zp(self, pc, cycle_count): # 0x06
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def arith_sl_zpix(self, pc, cycle_count): # 0x16
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def arith_sl_a(self, pc, cycle_count): # 0x0E
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def arith_sl_aix(self, pc, cycle_count): # 0x1E
        exit()
        cycle_count -= 7
        return pc, cycle_count

# BCC  -  Branch on Carry Clear 
    def branch_cc(self, pc, cycle_count): # 0x90
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BCS  -  Branch on Carry Set 
    def branch_cs(self, pc, cycle_count): # 0xB0
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BEQ  -  Branch Zero Set 
    def branch_zs(self, pc, cycle_count): # 0xF0
        exit()
        cycle_count -= 2
        return pc, cycle_count

# note: bit moet 5 instr zijn ipv 2? 
# BIT  -  Test Bits in Memory with Accumulator 
    def bit_test_zp(self, pc, cycle_count): # 0x24
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def bit_test_a(self, pc, cycle_count): # 0x2C
        exit()
        cycle_count -= 4
        return pc, cycle_count

# BMI  -  Branch on Result Minus 
    def branch_rm(self, pc, cycle_count): # 0x30
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BNE  -  Branch on Z reset 
    def branch_zr(self, pc, cycle_count): # 0xD0
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BPL  -  Branch on Result Plus (or Positive) 
    def branch_rp(self, pc, cycle_count): # 0x10
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BRK  -  Force a Break 
    def brk(self, pc, cycle_count): # 0x00
        exit()
        cycle_count -= 7
        return pc, cycle_count

# BVC  -  Branch on Overflow Clear 
    def branch_oc(self, pc, cycle_count): # 0x50
        exit()
        cycle_count -= 2
        return pc, cycle_count

# BVS  -  Branch on Overflow Set 
    def branch_os(self, pc, cycle_count): # 0x70
        exit()
        cycle_count -= 4
        return pc, cycle_count

# CLC  -  Clear Carry Flag 
    def clear_cf(self, pc, cycle_count): # 0x18
        exit()
        cycle_count -= 2
        return pc, cycle_count

# CLD  -  Clear Decimal Mode 
    def clear_dm(self, pc, cycle_count): # 0xD8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# CLI  -  Clear Interrupt Disable 
    def clear_id(self, pc, cycle_count): # 0x58
        exit()
        cycle_count -= 2
        return pc, cycle_count

# CLV  -  Clear Overflow Flag 
    def clear_of(self, pc, cycle_count): # 0xB8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# CMP  -  Compare Memory and Accumulator 
    def comp_mem_im(self, pc, cycle_count): # 0xC9
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xC5
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def comp_mem_zpix(self, pc, cycle_count): # 0xD5
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xCD
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def comp_mem_aix(self, pc, cycle_count): # 0xDD
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def comp_mem_aiy(self, pc, cycle_count): # 0xD9
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def comp_mem_idi(self, pc, cycle_count): # 0xC1
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def comp_mem_ini(self, pc, cycle_count): # 0xD1
        exit()
        cycle_count -= 6
        return pc, cycle_count

# CPX  -  Compare Memory and X register 
    def comp_mem_im(self, pc, cycle_count): # 0xE0
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xE4
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xEC
        exit()
        cycle_count -= 4
        return pc, cycle_count

# CPY  -  Compare Memory and Y register 
    def comp_mem_im(self, pc, cycle_count): # 0xC0
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def comp_mem_zp(self, pc, cycle_count): # 0xC4
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def comp_mem_a(self, pc, cycle_count): # 0xCC
        exit()
        cycle_count -= 4
        return pc, cycle_count

# DEC  -  Decrement Memory by One 
    def decr_mem_zp(self, pc, cycle_count): # 0xC6
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def decr_mem_zpix(self, pc, cycle_count): # 0xD6
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def decr_mem_a(self, pc, cycle_count): # 0xCE
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def decr_mem_aix(self, pc, cycle_count): # 0xDE
        exit()
        cycle_count -= 7
        return pc, cycle_count

# DEX  -  Decrement X 
    def decr(self, pc, cycle_count): # 0xCA
        exit()
        cycle_count -= 2
        return pc, cycle_count

# DEY  -  Decrement Y 
    def decr(self, pc, cycle_count): # 0x88
        exit()
        cycle_count -= 2
        return pc, cycle_count

# EOR  -  Exclusive-OR Memory with Accumulator 
    def excl_or_mem_im(self, pc, cycle_count): # 0x49
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def excl_or_mem_zp(self, pc, cycle_count): # 0x45
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def excl_or_mem_zpix(self, pc, cycle_count): # 0x55
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def excl_or_mem_a(self, pc, cycle_count): # 0x4D
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def excl_or_mem_aix(self, pc, cycle_count): # 0x5D
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def excl_or_mem_aiy(self, pc, cycle_count): # 0x59
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def excl_or_mem_idi(self, pc, cycle_count): # 0x41
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def excl_or_mem_ini(self, pc, cycle_count): # 0x51
        exit()
        cycle_count -= 5
        return pc, cycle_count

# INC  -  Increment Memory by one 
    def incr_mem_zp(self, pc, cycle_count): # 0xE6
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def incr_mem_zpix(self, pc, cycle_count): # 0xF6
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def incr_mem_a(self, pc, cycle_count): # 0xEE
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def incr_mem_aix(self, pc, cycle_count): # 0xFE
        exit()
        cycle_count -= 7
        return pc, cycle_count

# INX  -  Increment X by one 
    def incr(self, pc, cycle_count): # 0xE8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# INY  -  Increment Y by one 
    def incr(self, pc, cycle_count): # 0xC8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# mis nog 1 JMP instructie 
# JMP - Jump 
    def jmp_a(self, pc, cycle_count): # 0x4c
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def jmp_ai(self, pc, cycle_count): # 0x6c
        exit()
        cycle_count -= 5
        return pc, cycle_count

# JSR - Jump to subroutine 
    def jsr(self, pc, cycle_count): # 0x20
        exit()
        cycle_count -= 6
        return pc, cycle_count

# LDA - Load Accumulator with memory 
    def load_im(self, pc, cycle_count): # 0xA9
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def load_zp(self, pc, cycle_count): # 0xA5
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def load_zpix(self, pc, cycle_count): # 0xB5
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_a(self, pc, cycle_count): # 0xAD
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_aix(self, pc, cycle_count): # 0xBD
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_aiy(self, pc, cycle_count): # 0xB9
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_idi(self, pc, cycle_count): # 0xA1
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def load_ini(self, pc, cycle_count): # 0xB1
        exit()
        cycle_count -= 5
        return pc, cycle_count

# LDX - Load X with Memory 
    def load_im(self, pc, cycle_count): # 0xA2
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def load_zp(self, pc, cycle_count): # 0xA6
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def load_zpiy(self, pc, cycle_count): # 0xB6
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_a(self, pc, cycle_count): # 0xAE
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_aiy(self, pc, cycle_count): # 0xBE
        exit()
        cycle_count -= 4
        return pc, cycle_count

# LDY - Load Y with Memory 
    def load_im(self, pc, cycle_count): # 0xA0
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def load_zp(self, pc, cycle_count): # 0xA4
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def load_zpix(self, pc, cycle_count): # 0xB4
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_a(self, pc, cycle_count): # 0xAC
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def load_aix(self, pc, cycle_count): # 0xBC
        exit()
        cycle_count -= 4
        return pc, cycle_count

# LSR  -  Logical Shift Right 
    def logic_shift_r_acc(self, pc, cycle_count): # 0x4A
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def logic_shift_r_zp(self, pc, cycle_count): # 0x46
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def logic_shift_r_zpix(self, pc, cycle_count): # 0x56
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def logic_shift_r_a(self, pc, cycle_count): # 0x4E
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def logic_shift_r_aix(self, pc, cycle_count): # 0x5E
        exit()
        cycle_count -= 7
        return pc, cycle_count

# NOP - No Operation (79 instructies?) 
    def nop(self, pc, cycle_count): # 0xEA
        exit()
        cycle_count -= 2
        return pc, cycle_count

# ORA  -  OR Memory with Accumulator 
    def or_mem_im(self, pc, cycle_count): # 0x09
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def or_mem_zp(self, pc, cycle_count): # 0x05
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def or_mem_zpix(self, pc, cycle_count): # 0x15
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def or_mem_a(self, pc, cycle_count): # 0x0D
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def or_mem_aix(self, pc, cycle_count): # 0x1D
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def or_mem_aiy(self, pc, cycle_count): # 0x19
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def or_mem_idi(self, pc, cycle_count): # 0x01
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def or_mem_ini(self, pc, cycle_count): # 0x11
        exit()
        cycle_count -= 5
        return pc, cycle_count

# PHA  -  Push Accumulator on Stack 
    def push_a(self, pc, cycle_count): # 0x48
        exit()
        cycle_count -= 3
        return pc, cycle_count

# PHP  -  Push Processor Status on Stack 
    def push_ps(self, pc, cycle_count): # 0x08
        exit()
        cycle_count -= 3
        return pc, cycle_count

# PLA  -  Pull Accumulator from Stack 
    def pull_a(self, pc, cycle_count): # 0x68
        exit()
        cycle_count -= 4
        return pc, cycle_count

# PLP  -  Pull Processor Status from Stack 
    def pull_ps(self, pc, cycle_count): # 0x28
        exit()
        cycle_count -= 4
        return pc, cycle_count

# ROL  -  Rotate Left 
    def rotate_left_acc(self, pc, cycle_count): # 0x2A
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def rotate_left_zp(self, pc, cycle_count): # 0x26
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def rotate_left_zpix(self, pc, cycle_count): # 0x36
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def rotate_left_a(self, pc, cycle_count): # 0x2E
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def rotate_left_aix(self, pc, cycle_count): # 0x3E
        exit()
        cycle_count -= 7
        return pc, cycle_count

# ROR  -  Rotate Right 
    def rotate_right_acc(self, pc, cycle_count): # 0x6A
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def rotate_right_zp(self, pc, cycle_count): # 0x66
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def rotate_right_zpix(self, pc, cycle_count): # 0x76
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def rotate_right_a(self, pc, cycle_count): # 0x6E
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def rotate_right_aix(self, pc, cycle_count): # 0x7E
        exit()
        cycle_count -= 7
        return pc, cycle_count

# RTI  -  Return from Interrupt 
    def ret_int(self, pc, cycle_count): # 0x40
        exit()
        cycle_count -= 4
        return pc, cycle_count

# RTS  -  Return from Subroutine 
    def ret_sub(self, pc, cycle_count): # 0x60
        exit()
        cycle_count -= 4
        return pc, cycle_count

# SBC  -  Subtract from Accumulator with Carry (IDI_ZP?) 
    def sub_acc_im(self, pc, cycle_count): # 0xE9
        exit()
        cycle_count -= 2
        return pc, cycle_count
    def sub_acc_zp(self, pc, cycle_count): # 0xE5
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def sub_acc_zpix(self, pc, cycle_count): # 0xF5
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def sub_acc_a(self, pc, cycle_count): # 0xED
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def sub_acc_aix(self, pc, cycle_count): # 0xFD
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def sub_acc_aiy(self, pc, cycle_count): # 0xF9
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def sub_acc_idi(self, pc, cycle_count): # 0xE1
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def sub_acc_ini(self, pc, cycle_count): # 0xF1
        exit()
        cycle_count -= 5
        return pc, cycle_count

# SEC  -  Set Carry Flag 
    def set_c_flag(self, pc, cycle_count): # 0x38
        exit()
        cycle_count -= 2
        return pc, cycle_count

# SED  -  Set Decimal Mode 
    def set_d_mode(self, pc, cycle_count): # 0xF8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# SEI - Set Interrupt Disable 
    def set_int_dis(self, pc, cycle_count): # 0x78
        exit()
        cycle_count -= 2
        return pc, cycle_count

# STA - Store Accumulator in Memory (IDI_ZP?) 
    def store_zp(self, pc, cycle_count): # 0x85
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def store_zpix(self, pc, cycle_count): # 0x95
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def store_a(self, pc, cycle_count): # 0x8D
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def store_aix(self, pc, cycle_count): # 0x9D
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def store_aiy(self, pc, cycle_count): # 0x99
        exit()
        cycle_count -= 5
        return pc, cycle_count
    def store_idi(self, pc, cycle_count): # 0x81
        exit()
        cycle_count -= 6
        return pc, cycle_count
    def store_ini(self, pc, cycle_count): # 0x91
        exit()
        cycle_count -= 6
        return pc, cycle_count

# STX - Store X in Memory 
    def store_zp(self, pc, cycle_count): # 0x86
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def store_zpiy(self, pc, cycle_count): # 0x96
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def store_a(self, pc, cycle_count): # 0x8E
        exit()
        cycle_count -= 4
        return pc, cycle_count

# STY - Store Y in Memory 
    def store_zp(self, pc, cycle_count): # 0x84
        exit()
        cycle_count -= 3
        return pc, cycle_count
    def store_zpix(self, pc, cycle_count): # 0x94
        exit()
        cycle_count -= 4
        return pc, cycle_count
    def store_a(self, pc, cycle_count): # 0x8C
        exit()
        cycle_count -= 4
        return pc, cycle_count

# TAX  -  Transfer Accumulator to X 
    def transfer_reg(self, pc, cycle_count): # 0xAA
        exit()
        cycle_count -= 2
        return pc, cycle_count

# TAY  -  Transfer Accumulator to Y 
    def transfer_reg(self, pc, cycle_count): # 0xA8
        exit()
        cycle_count -= 2
        return pc, cycle_count

# TSX  -  Transfer Stack to X 
    def transfer_stack_from(self, pc, cycle_count): # 0xBA
        exit()
        cycle_count -= 2
        return pc, cycle_count

# TXA  -  Transfer X to Accumulator 
    def transfer_reg(self, pc, cycle_count): # 0x8A
        exit()
        cycle_count -= 2
        return pc, cycle_count

# TXS  -  Transfer X to Stack 
    def transfer_stack_to(self, pc, cycle_count): # 0x9A
        exit()
        cycle_count -= 2
        return pc, cycle_count

# TYA  -  Transfer Y to Accumulator 
    def transfer_reg(self, pc, cycle_count): # 0x98
        exit()
        cycle_count -= 2
        return pc, cycle_count
