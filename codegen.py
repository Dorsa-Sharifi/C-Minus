from enum import Enum

class Opcode_Enums(Enum):
    ADD = 'ADD'
    LT = 'LT'
    ASSIGN = 'ASSIGN'
    MULT = 'MULT'
    SUB = 'SUB'
    DIV = 'DIV'
    EQ = 'EQ'
    JPF = 'JPF'
    JP = 'JP'
    PRINT = 'PRINT'


class CodeGenerator:
    def __init__(self):
        self.current_scope = 0
        self.Ret_Stack = list()
        self.index = 0
        self.temp_address = 500
        self.symbol_table = {'Keywords': ['if', 'else', 'void', 'int', 'while', 'break', 'return'],
                            'IDs': []}
        self.semantic_stack = list()
        self.program_block = dict()
        self.Break_stack = list()
        self.variable_size = 4
        self.semantic_errors = []
        self.operations_dict = {'+': Opcode_Enums.ADD.value,
                                '-': Opcode_Enums.SUB.value,
                                '*': Opcode_Enums.MULT.value,
                                '/': Opcode_Enums.DIV.value,
                                '<': Opcode_Enums.LT.value,
                                '==': Opcode_Enums.EQ.value}



    #Push Functions
    def Push_index(self, lookahead):
        self.semantic_stack.append(f'#{self.index}')

    def Push_Return_Point(self, lookahead):
        self.Ret_Stack.append((self.index, self.semantic_stack[-1]))
        self.semantic_stack.pop()
        self.index += 2

    def Push_ID(self, lookahead):
        self.semantic_stack.append(lookahead[2])

    def Push_ID_Addr(self, lookahead):
        self.semantic_stack.append(CodeGenerator.find_address(self, lookahead[2]))

    def Push_Number(self, lookahead):
        self.semantic_stack.append(f'#{lookahead[2]}')

    def Add_Var_SS(self):
        top = self.semantic_stack.pop()
        address = self.generate_temp_memory()
        self.symbol_table['IDs'].append(
            (top,
             'int',
             address,
             self.current_scope))



    def Create_Array(self):
        array_size = int(self.semantic_stack.pop()[1:])
        array_id = self.semantic_stack.pop()
        address = self.generate_temp_memory()
        array_space = self.generate_temp_memory(array_size)
        self.Add_TAD(Opcode_Enums.ASSIGN.value, f'#{array_space}', address)
        self.symbol_table['IDs'].append((array_id, 'int*', address, self.current_scope))



    #Function Handlers
    def Param_Def(self, lookahead):
        top = self.semantic_stack.pop()
        self.semantic_stack.append(self.index)
        self.index += 1
        self.semantic_stack.append(top)
        self.symbol_table['IDs'].append('>>')

    def Func_Beginning(self, lookahead):
        func_id = self.semantic_stack[-1]
        return_address = self.generate_temp_memory()
        current_index = self.index
        return_value = self.generate_temp_memory()
        self.semantic_stack.append(return_value)
        self.semantic_stack.append(return_address)
        args_start_index = self.symbol_table['IDs'].index('>>')
        func_args = self.symbol_table['IDs'][args_start_index + 1:]
        self.symbol_table['IDs'].pop(args_start_index)
        self.symbol_table['IDs'] \
            .append((func_id, 'function', [return_value, func_args, return_address, current_index], self.current_scope))

    def Mark_Return(self, lookahead):
        self.Ret_Stack.append('>>>')

    def close_return(self, lookahead):
        latest_func = len(self.Ret_Stack) - 1
        latest_func = latest_func - self.Ret_Stack[::-1].index('>>>')
        return_value = self.semantic_stack[-2]
        return_address = self.semantic_stack[-1]
        for rs in self.Ret_Stack[latest_func + 1:]:
            index = rs[0]
            self.program_block[index] = f'(ASSIGN, {rs[1]}, {return_value}, )'
            self.program_block[index + 1] = f'(JP, @{return_address}, , )'
        self.Ret_Stack = self.Ret_Stack[:latest_func]

    def Back_to_Main(self, lookahead):
        if self.semantic_stack[-3] != 'main':
            return_address = self.semantic_stack[-1]
            self.Add_TAD(Opcode_Enums.JP.value, f'@{return_address}')

    def Func_Ending(self, lookahead):
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        self.semantic_stack.pop()
        for st in self.symbol_table['IDs'][::-1]:
            if st[1] == 'function':
                if st[0] == 'main':
                    top = self.semantic_stack.pop()
                    self.program_block[top] = f'(ASSIGN, #0, {self.generate_temp_memory()}, )'
                    return
                break
            else:
                continue
        top = self.semantic_stack.pop()
        self.program_block[top] = f'(JP, {self.index}, , )'

    def call_function(self, lookahead):
        if self.semantic_stack[-1] != 'output':
            elements = []
            collections = []
            for top in self.semantic_stack[::-1]:
                if isinstance(top, list):
                    collections = top
                    break
                elements = [top] + elements
            # assign each element
            for variable, element in zip(collections[1], elements):
                self.Add_TAD(Opcode_Enums.ASSIGN.value, element, variable[2])
                self.semantic_stack.pop()  # pop each element
            for i in range(len(elements) - len(collections[1])):
                self.semantic_stack.pop()
            self.semantic_stack.pop()
            self.Add_TAD(Opcode_Enums.ASSIGN.value, f'#{self.index + 2}', collections[2])
            # jump
            self.Add_TAD(Opcode_Enums.JP.value, collections[-1])
            # save result to temp
            result = self.generate_temp_memory()
            self.Add_TAD(Opcode_Enums.ASSIGN.value, collections[0], result)
            self.semantic_stack.append(result)


    def Push_Relation(self, lookahead):
        self.semantic_stack.append(lookahead[2])

    #Calculations
    def Save_Operation(self):
        operand_2 = self.semantic_stack.pop()
        operator = self.semantic_stack.pop()
        operand_1 = self.semantic_stack.pop()
        address = self.generate_temp_memory()
        opr = self.operations_dict[operator]
        self.Add_TAD(opr, operand_1, operand_2, address)
        self.semantic_stack.append(address)

    def Negative(self, lookahead):
        result = self.generate_temp_memory()
        factor_value = self.semantic_stack.pop()
        self.Add_TAD(Opcode_Enums.SUB.value, '#0', factor_value, result)
        self.semantic_stack.append(result)

    def Assignment_Op(self):
        opr1 = self.semantic_stack[-1]
        opr2 = self.semantic_stack[-2]
        self.Add_TAD(Opcode_Enums.ASSIGN.value, opr1, opr2)
        self.semantic_stack.pop()

    def Mult_Div_Operation(self, lookahead):
        operand_2 = self.semantic_stack.pop()
        operator = self.semantic_stack.pop()
        operand_1 = self.semantic_stack.pop()
        address = self.generate_temp_memory()
        opr = self.operations_dict[operator]
        self.Add_TAD(opr, operand_2, operand_1, address)
        self.semantic_stack.append(address)

    #Scoping Handlers
    def Next_Scope(self, lookahead):
        self.current_scope += 1

    def Prev_Scope(self, lookahead):
        for record in self.symbol_table['IDs'][::-1]:
            if record[3] == self.current_scope:
                del self.symbol_table['IDs'][-1]
        self.current_scope -= 1



    #Array Handlers
    def Arr_Args_Def(self, lookahead):
        top = self.symbol_table['IDs'][-1]
        del self.symbol_table['IDs'][-1]
        self.symbol_table['IDs'].append((top[0], 'int*', top[2], top[3]))

    def Array_Indices(self, lookahead):
        idx = self.semantic_stack.pop()
        array_address = self.semantic_stack.pop()
        temp = self.generate_temp_memory()
        result = self.generate_temp_memory()
        self.Add_TAD(Opcode_Enums.MULT.value, '#4', idx, temp)
        self.Add_TAD(Opcode_Enums.ASSIGN.value, f'{array_address}', result)
        self.Add_TAD(Opcode_Enums.ADD.value, result, temp, result)
        self.semantic_stack.append(f'@{result}')


    def output_function(self, lookahead):
        if self.semantic_stack[-2] == 'output':
            self.Add_TAD(Opcode_Enums.PRINT.value, self.semantic_stack.pop())

    def save(self, lookahead):
        self.semantic_stack.append(self.index)
        self.index += 1

    def label(self, lookahead):
        self.semantic_stack.append(self.index)

    def Save_JPF(self):
        dest = self.semantic_stack.pop()
        src = self.semantic_stack.pop()
        self.program_block[dest] = f'(JPF, {src}, {self.index + 1}, )'
        self.semantic_stack.append(self.index)
        self.index += 1

    def While_Jumps(self, lookahead):
        self.program_block[int(self.semantic_stack[-1])] = f'(JPF, {self.semantic_stack[-2]}, {self.index + 1}, )'
        self.program_block[self.index] = f'(JP, {self.semantic_stack[-3]}, , )'
        self.index += 1
        self.semantic_stack.pop(), self.semantic_stack.pop(), self.semantic_stack.pop()

    def jump(self, lookahead):
        dest = int(self.semantic_stack.pop())
        self.program_block[dest] = f'(JP, {self.index}, , )'



    def Remove_Extra_Data(self, lookahead):
        self.semantic_stack.pop()

    def end_of_loop_with_break(self, lookahead):
        self.Break_stack.append(self.index)
        self.index += 1

    def new_break(self, lookahead):
        self.Break_stack.append('>>>')

    def back_to_scope_with_end_break(self, lookahead):
        latest_block = len(self.Break_stack) - self.Break_stack[::-1].index('>>>') - 1
        for item in self.Break_stack[latest_block + 1:]:
            self.program_block[item] = f'(JP, {self.index}, , )'
        self.Break_stack = self.Break_stack[:latest_block]


    # Handy Functions
    def find_address(self, token_string):
        if token_string == 'output':
            return 'output'
        for record in self.symbol_table['IDs'][::-1]:
            line_number = record[0]
            type_token = record[1]
            lexeme = record[2]
            if token_string == line_number:
                return lexeme

    def Add_TAD(self, relop, opr1, opr2='', dist=''):
        i = self.index
        self.program_block[i] = f'({relop}, {opr1}, {opr2}, {dist})'
        self.index += 1

    def generate_temp_memory(self, count=1):
        address = str(self.temp_address)
        for i in range(count):
            self.Add_TAD(Opcode_Enums.ASSIGN.value, '#0', str(self.temp_address))
            self.temp_address += self.variable_size
        return address