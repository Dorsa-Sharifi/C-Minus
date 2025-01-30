class PB:
    def __init__(self):
        self.line_Number = 0
        self.PB = []
    def Add_Code(self, opcode, operator1 = '', operator2 = '', target = '', addr = 0):
        self.PB[addr] =  f"({opcode}, {operator1}, {operator2}, {target})"
    def increase_line_Number(self):
        self.line_Number += 1