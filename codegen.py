
from SS import SS
#TODO Double check all the PB.Add_Codes
#TODO Get back for printing possible errors
class Codegen:
    def __init__(self):
        self.base_address = 500
        self.memory_size = 4
        self.index = 0
        self.current_scope = 0
        self.ss = SS()
        self.pb = []
        self.RS = []
        self.BS = []
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
        self.BS.append(self.index)
        self.index += 1

    def Assignment(self):
        operand1, operand2 = self.ss.pop_with_num(2)
        self.pb.Add_Code('ASSIGN', operand1, operand2,'',int(self.index))
        self.ss.pop()

    def Array_Indices(self):
        index, arr_addr = self.ss.pop_with_num(2)
        # temp = self.generateTemp()
        # result = self.generateTemp()
        # self.pb.Add_Code(RelativeOperation.MULT.value, '#4', idx, temp)
        # self.insert_code(RelativeOperation.ASSIGN.value, f'{array_address}', result)
        # self.insert_code(RelativeOperation.ADD.value, result, temp, result)
        # self.SS.append(f'@{result}')

    def Multiply_Division(self):
        pass
    def Func_Call(self):
        if self.ss.access_members(-1) != 'output':
            elements = []
            collections = []
            for top in self.ss.stack[::-1]:
                if isinstance(top, list):
                    collections = top
                    break
                elements = [top] + elements
            # assign each element
            for variable, element in zip(collections[1], elements):
                self.pb.Add_Code(self.index,'ASSIGN', element, variable[2])
                self.ss.pop()  # pop each element
            for i in range(len(elements) - len(collections[1])):
                self.ss.pop()
            self.ss.pop()
            # self.insert_code(RelativeOperation.ASSIGN.value, f'#{self.index + 2}', collections[2])
            # jump
            # self.insert_code(RelativeOperation.JP.value, collections[-1])
            # save result to temp
            result = self.generateTemp()
            # self.insert_code(RelativeOperation.ASSIGN.value, collections[0], result)
            self.ss.push(result)
        pass

    def Func_Ending(self):
        for _ in range(3):
            self.ss.pop()

        # Check the symbol table for a function, prioritizing 'main'
        for st in reversed(self.symbol_table['IDs']):
            if st[1] == 'function':
                if st[0] == 'main':
                    top = self.ss.pop()
                    self.pb[top] = f'(ASSIGN, #0, {self.generateTemp()}, )'
                    return
                break  # Stop checking after the first function is found

        # Default jump if no 'main' function was found
        top = self.ss.pop()
        self.pb[top] = f'(JP, {self.index}, , )'

    def New_Break(self):
        self.BS.append('>>>')
    def Return_Scope_with_Break(self):
        latest_block = len(self.BS) - self.BS[::-1].index('>>>') - 1
        for item in self.BS[latest_block + 1:]:
            self.pb[item] = f'(JP, {self.index}, , )'
        self.BS = self.BS[:latest_block]
    def Save_Return_Point(self):
        self.RS.append((self.index, self.ss.access_members(-1)))
        self.ss.pop()
        self.index += 2
    def Found_Return(self):
        self.RS.append('>>>')


    #Handy Functions
    def generateTemp(self, i = 1):
        address = self.base_address
        for j in range(i):
            self.pb.Add_Code(self.index,'ASSIGN', '#0', str(self.base_address))
            self.base_address += self.memory_size
        return address

    def find_address(self, address):

        pass
    def Add_Code(self, opcode, operation1, operation2='', dist=''):
        i = self.index
        self.pb[i] = f'({opcode}, {operation1}, {operation2}, {dist})'
        self.index += 1
