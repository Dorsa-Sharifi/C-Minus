
from PB import PB
from SS import SS

#TODO Get back for printing possible errors
class Codegen:
    def __init__(self):
        self.base_address = 500
        self.memory_size = 4
        self.index = 0
        self.current_scope = 0
        self.ss = SS()
        self.pb = PB()
        self.RS = []
        self.symbol_table = dict()
        self.OperationDict = {'+': 'ADD',
                              '-': 'SUB',
                              '*': 'MUL',
                              '/': 'DIV',
                              '<': 'LT',
                              '==': 'ASSIGN'}

    def run(self, action):
        pass

    def Push_ID(self, ID):
        self.ss.push(ID)

    def Push_Num(self, num):
        self.ss.push(num)

    def Remove_Data_From_SS(self):
        self.ss.pop()

    def Save(self):
        self.ss.push(self.index)
        self.index += 1

    def Jpf_Save(self):
        destination, operator1 = self.ss.pop_with_num(2)
        target = self.index + 1
        self.pb.Add_Code('JPF', operator1, target,'' ,destination)
        self.index += 1

    def Jump(self):
        destination = int(self.ss.pop())
        self.pb.Add_Code('JP', {self.index},'','',destination)

    def Label(self):
        self.ss.push(self.index)

    def While_Jumps(self):
        self.pb.Add_Code('JPF', {self.ss.access_members(-2)}, {self.index + 1}, '',self.ss.access_members(-1))
        self.pb.Add_Code('JP', self.ss.access_members(-3), '','',self.index)
        self.index += 1
        self.ss.pop()
        self.ss.pop()
        self.ss.pop()

    def Push_Index(self):
        self.ss.push(f'#{self.index}')

    def Pop_Relation(self, relation):
        self.ss.push(relation)

    def Negative(self):
        temp = self.generateTemp()
        to_be_negated = self.ss.pop()
        self.pb.Add_Code('SUB', 0, to_be_negated, temp, self.index)
        self.ss.push(temp)

    def Func_Output(self):
        if self.ss.access_members(-2) == 'output':
            self.pb.Add_Code('PRINT', self.ss.pop())


    #Related to Scoping, other stacks, etc
    def Create_Arr(self):
        #Got help from a repo in GitHub
        array_size = int(self.ss.pop()[1:])
        array_id = self.ss.pop()
        address = self.generateTemp()
        array_space = self.generateTemp(array_size)
        self.pb.Add_Code('ASSIGN', f'#{array_space}', address)
        self.symbol_table['IDs'].append((array_id, 'int*', address, self.current_scope))

    def Params_Declaration(self):
        top = self.ss.pop()
        self.ss.push(self.index)
        self.index += 1
        self.ss.push(top)
        self.symbol_table['IDs'].append('>>')

    def Func_Beginning(self):
        pass

    def Search_For_Return(self):
        self.RS.append('>>>')

    def Return_Main(self):
        if self.ss.access_members(-3) != 'main':
            return_address = self.ss.access_members(-1)
            self.pb.Add_Code('JP', f'@{return_address}')

    def Push_ID_Addr(self, addr):
        self.ss.push(self.find_address(addr))

    def Add_Var_SS(self):
        #Scope Managing
        top = self.ss.pop()
        addr = self.generateTemp()
        scope = self.current_scope
        #TODO Add the given popped value to the symbol table

    def Save_Operation(self):
        addr = self.generateTemp()
        operand2, operator, operand1 = self.ss.pop_with_num(3)
        opcode = self.OperationDict[operator]
        self.pb.Add_Code(opcode, operand1, operand2, addr,self.index)
        self.ss.push(addr)


    def Array_Args(self):
        top = self.symbol_table['IDs'][-1]
        del self.symbol_table['IDs'][-1]
        self.symbol_table['IDs'].append((top[0], 'int*', top[2], top[3]))

    def Next_Scope(self):
        self.current_scope += 1

    def Prev_Scope(self):
        #Until reaching another scope del vars and functions
        for i in self.symbol_table['IDs'][::-1]:
            if i[3] == self.current_scope:
                del self.symbol_table['IDs'][-1]
        self.current_scope -= 1

    def End_of_Loop_Break(self):
        pass
    def Assignment(self):
        pass
    def Array_Indices(self):
        pass
    def Multiply_Division(self):
        pass
    def Func_Call(self):
        pass
    def Func_Ending(self):
        pass
    def New_Break(self):
        pass
    def Return_Scope_with_Break(self):
        pass
    def Save_Return_Point(self):
        pass
    def Found_Return(self):
        pass


    #Handy Functions
    def generateTemp(self, i = 1):
        address = self.base_address
        for j in range(i):
            self.pb.Add_Code('ASSIGN', '#0', str(self.base_address))
            self.base_address += self.memory_size
        return address

    def find_address(self, address):

        pass
