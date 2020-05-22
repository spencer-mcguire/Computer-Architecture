"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.pc = 0
        self.ram = [0] * 256
        self.running = True
        self.branchtable = {
            HLT: self.op_hlt,
            LDI: self.op_ldi,
            PRN: self.op_prn,
            ADD: self.op_add,
            MUL: self.op_mul,
            PUSH: self.op_push,
            POP: self.op_pop,
            CALL: self.op_call,
            RET: self.op_ret,
            CMP: self.op_cmp,
            JMP: self.op_jmp,
            JEQ: self.op_jeq,
            JNE: self.op_jne
        }
        self.reg[7] = 0xF4
        self.sp = self.reg[7]
        self.fl = 0b00000000

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        with open(filename) as file:
            for line in file:
                split = line.split('#')
                instruction = split[0]

                if instruction == '':
                    continue
                first_bit = instruction[0]
                if first_bit == '1' or first_bit == '0':
                    self.ram[address] = int(instruction[:8], 2)
                    address += 1

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def op_hlt(self, operand_a, operand_b):
        self.running = False
        sys.exit(1)

    def op_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def op_prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def op_add(self, operand_a, operand_b):
        #print('adding')
        self.alu('ADD', operand_a, operand_b)

    def op_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
    
    def op_push(self, operand_a, operand_b):
        #print(self.sp)
        self.sp -= 1

        #print(self.sp)

        # grab the value at op a
        val = self.reg[operand_a]

        self.ram_write(self.sp, val)

    def op_pop(self, operand_a, operand_b):
        # get value to pop
        val = self.ram_read(self.sp)

        self.reg[operand_a] = val

        self.sp += 1

    def op_call(self, operand_a, operand_b):
        return_address = self.pc + 2
        self.sp -= 1 
        
        self.ram_write(self.sp, return_address)

        sub_addr = self.reg[operand_a]
        # set pc to where you are jumping to
        self.pc = sub_addr

    def op_ret(self, operand_a, operand_b):
        return_to = self.ram_read(self.sp)

        self.sp += 1

        self.pc = return_to

    def op_cmp(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)

    def op_jmp(self, operand_a, operand_b):
        jump_to = self.reg[operand_a]

        self.pc = jump_to

    def op_jeq(self, operand_a, operand_b):
        if self.fl == 0b00000001:
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def op_jne(self, operand_a, operand_b):
        if self.fl != 0b00000001:
            self.op_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            #print('add')
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001

            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            op_size = IR >> 6
            # print('IR', IR)
            # print("op_size", op_size)

            ins_set = ((IR >> 4) & 0b1) == 1
            # print('shift', (IR >> 4) & 0b1)
            #print('ins_set', ins_set)

            if IR in self.branchtable:
                self.branchtable[IR](operand_a, operand_b)

            if not ins_set:
                # print('op_size', op_size)
                self.pc += op_size + 1

            

            

