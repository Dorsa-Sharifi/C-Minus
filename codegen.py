from operator import index

from PB import PB
from SS import SS



#TODO Get back for printing possible errors
class Codegen:
    def __init__(self):
        self.index = 0
        self.current_scope = 0
        self.ss = SS()
        self.pb = PB()

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
        self.pb.Add_Code('JPF', {self.ss.access_members(-2)}, {self.index + 1}, '',
                         self.ss.access_members(-1))
        self.pb.Add_Code('JP', self.ss.access_members(-3), '','',self.index)
        self.index += 1
        self.ss.pop()
        self.ss.pop()
        self.ss.pop()

    def Push_Index(self):
        self.ss.push(f'#{self.index}')

    def Pop_Relation(self, relation):
        self.ss.push(relation)
        pass
    def Save_Operation(self):
        addr = self.get_temp()
        operand2, operator, operand1 = self.ss.pop_with_num(3)
        #TODO: a list of operands + add_code function
        self.ss.push(addr)
        pass

    def Multiply_Division(self):
        pass
    def Negative(self):
        pass

    def Func_Output(self):
        pass
    def Func_Call(self):
        pass

    #Related to Scoping, other stacks, etc
    def Create_Arr(self):
        #TODO:  Creates an array entry in the symbol table with the previously pushed number as its size.
        pass
    def Params_Declaration(self):
        pass
    def Func_Beginning(self):
        pass
    def Search_For_Return(self):
        pass
    def Found_Return(self):
        pass
    def Return_Main(self):
        pass
    def Func_Ending(self):
        pass
    def New_Break(self):
        pass
    def Return_Scope_with_Break(self):
        pass
    def Save_Return_Point(self):
        pass
    def Push_ID_Addr(self):
        pass
    def Add_Var_SS(self):
        #Scope Managing
        top = self.ss.pop()
        addr = self.get_temp()
        scope = self.current_scope
        #TODO Add the given popped value to the symbol table

    def Array_Args(self):
        pass
    def Next_Scope(self):
        pass
    def Prev_Scope(self):
        pass
    def End_of_Loop_Break(self):
        pass
    def Assignment(self):
        pass
    def Array_Indices(self):
        pass

    #Handy Functions
    def get_temp(self):
        #TODO
        return None