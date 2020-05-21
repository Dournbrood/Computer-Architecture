"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.instructions = {"HLT": 0b00000001,
                             "LDI": 0b10000010, "PRN": 0b01000111, "MLT": 0b10100010, "PSH": 0b01000101, "POP": 0b01000110, "CLL": 0b01010000, "RET": 0b00010001, "ADD": 0b10100000}
        self.halted = False
        self.sp = 7

        self.reg[self.sp] = 0xF4

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        with open(sys.argv[1]) as f:

            for line in f:

                string_val = line.split("#")[0].strip()

                if string_val == '':
                    continue

                v = int(string_val, 2)

                self.ram[address] = v

                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MLT":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def push(self):

        # Decrement the stack pointer by 1
        self.reg[self.sp] -= 1

        # The registry at `self.sp` points to the address in our `self.ram` that is the top of the stack. It defaults to 0xf4.
        stack_top_addr = self.reg[self.sp]

        # Change the value in the address that is the top of our stack to whatever value we grabbed from the registry earlier.
        self.ram[stack_top_addr] = self.pc

    def pop(self):

        # The registry at `self.sp` points to the address in our `self.ram` that is the top of the stack. It defaults to 0xf4.
        stack_top_addr = self.reg[self.sp]

        # Change the value at the specified registry to the value at the top of the stack.
        return self.ram[stack_top_addr]

    def run(self):
        while not self.halted:

            # self.trace()

            # print(f"self.pc: {self.pc}")

            # print(self.reg)
            # print(self.ram)
            # print(self.ram[self.pc])

            if self.ram[self.pc] == self.instructions["HLT"]:
                # print("HLT")
                self.halted = True
                break

            elif self.ram[self.pc] == self.instructions["LDI"]:
                # print("LDI")
                self.pc += 1
                self.reg[self.ram[self.pc]] = self.ram[self.pc + 1]
                self.pc += 2

            elif self.ram[self.pc] == self.instructions["PRN"]:
                # print("PRN")
                self.pc += 1
                print(f"{self.reg[self.ram[self.pc]]}")
                self.pc += 1

            elif self.ram[self.pc] == self.instructions["MLT"]:
                # print("MLT")
                self.pc += 1
                self.alu("MLT", self.ram[self.pc],
                         self.ram[self.pc + 1])
                self.pc += 2

            elif self.ram[self.pc] == self.instructions["PSH"]:
                # print("PSH")
                # Decrement the stack pointer by 1
                self.reg[self.sp] -= 1

                # Get register number
                reg_num = self.ram[self.pc + 1]

                # Get value at that registry
                val = self.reg[reg_num]

                # The registry at `self.sp` points to the address in our `self.ram` that is the top of the stack. It defaults to 0xf4.
                stack_top_addr = self.reg[self.sp]

                # Change the value in the address that is the top of our stack to whatever value we grabbed from the registry earlier.
                self.ram[stack_top_addr] = val

                self.pc += 2

            elif self.ram[self.pc] == self.instructions["POP"]:
                # print("POP")
                # When popping to registry 0, set the registry[0] value to the value at the top of the stack, and then remove it from the stack.

                # Get register number
                reg_num = self.ram[self.pc + 1]

                # The registry at `self.sp` points to the address in our `self.ram` that is the top of the stack. It defaults to 0xf4.
                stack_top_addr = self.reg[self.sp]

                # Change the value at the specified registry to the value at the top of the stack.
                self.reg[reg_num] = self.ram[stack_top_addr]

                # Change the value in the address that is the top of our stack to 0.
                self.ram[stack_top_addr] = 0

                # Increment the stack pointer by 1
                self.reg[self.sp] += 1

                self.pc += 2

            elif self.ram[self.pc] == self.instructions["ADD"]:
                # print("ADD")
                self.pc += 1
                self.alu("ADD", self.ram[self.pc], self.ram[self.pc + 1])

                self.pc += 2

            elif self.ram[self.pc] == self.instructions["CLL"]:
                # print("CLL")
                # Put our current `pc` or address in memory in the stack.
                self.push()

                # self.trace()

                # Change `pc` to whatever address the `CALL` wants us to.
                self.pc = self.reg[self.ram[self.pc + 1]]
                # print(f"self.pc: {self.pc}")

                # print(f"value at self.ram[self.pc]: {self.ram[self.pc]}")

            elif self.ram[self.pc] == self.instructions["RET"]:
                # print("RET")
                self.pc = self.pop()

                self.pc += 2

                # Change the value in the address that is the top of our stack to 0.
                stack_top_addr = self.reg[self.sp]

                self.ram[stack_top_addr] = 0

                # Increment the stack pointer by 1
                self.reg[self.sp] += 1
