

from codegen import CodeGenerator
from scanner import Scanner
from anytree import Node, RenderTree

def get_from_file(file_path):
    result_dict = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
    headers = lines[0].split()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        key = parts[0]
        values = parts[1:]
        result_dict[key] = [headers[i] for i, v in enumerate(values) if v == '+']
    return result_dict

def get_rules(rules_path):
    rules_from_file = []
    with open(rules_path, "r") as file:
        for line in file:
            lhs, rhs = line.strip().split(" -> ")
            rules_from_file.append((lhs, rhs))
    return rules_from_file

def print_tree(root, file):
    for pre, fill, node in RenderTree(root):
        file.write(f"{pre}{node.name}\n")

class Parser:
    def __init__(self, first, follow, rules, input_file):
        self.first = get_from_file(first)
        self.follow = get_from_file(follow)
        self.rules = get_rules(rules)
        self.parse_table = {}
        self.init_parse_table()
        self.scanner = Scanner(input_file)
        self.codegen = CodeGenerator()
        self.isActionSymbol = True
        self.stack = ['$', self.rules[0][0]]
        self.error_count = 0
        self.parse_tree = open("parse_tree.txt", "a")
        self.errors = open("syntax_errors.txt", "a")
        self.output_file_phase3 = open("output.txt", "a")
        self.semantic_error_file = open("semantic_errors.txt", "a")
        self.init_file()
        self.nodes = []
        self.nodes.append(Node(self.rules[0][0]))
        self.stack_nodes = ['$', 0]
        self.next_token_flag = False


    def get_first(self, x):
        if is_terminal(x) or x == 'epsilon':
            return [x]
        else:
            return self.first[x]

    def get_first_rhs(self, rhs):
        elements = list(rhs.split(" "))
        firsts = []
        for i in range(len(elements)):
            if elements[i].startswith('#'):
                continue
            for t in self.get_first(elements[i]):
                firsts.append(t)
            if 'epsilon' not in self.get_first(elements[i]):
                break
            elif i < len(elements) - 1:
                firsts.remove('epsilon')
        return firsts

    def init_parse_table(self):
        for i in range(len(self.rules)):
            if self.rules[i][0] not in self.parse_table:
                self.parse_table[self.rules[i][0]] = {}
            for t in self.get_first_rhs(self.rules[i][1]):
                if t != 'epsilon':
                    self.parse_table[self.rules[i][0]][t] = self.rules[i][1]
            if 'epsilon' in self.get_first_rhs(self.rules[i][1]):
                for t in self.follow[self.rules[i][0]]:
                    self.parse_table[self.rules[i][0]][t] = self.rules[i][1]

    def init_file(self):
        self.parse_tree = open("parse_tree.txt", "w", encoding="utf-8")
        self.errors = open("syntax_errors.txt", "w")
        self.output_file_phase3 = open("output.txt", "w")
        self.semantic_error_file = open("semantic_errors.txt", "w")


    def write_error(self, error):
        self.error_count += 1
        lineno = self.scanner.lineno
        self.errors.write(f"#{lineno} : syntax error, {error}\n")
        # self.test.write(f"#{lineno} : syntax error, {error}\n")

    def codegen_caller(self, action, tup):
        if action == '#Add_Var_SS':
            self.codegen.Add_Var_SS()
        elif action == '#Create_Array':
            self.codegen.Create_Array()
        elif action == '#Push_ID':
            self.codegen.Push_ID(tup)
        elif action == '#Push_ID_Addr':
            self.codegen.Push_ID_Addr(tup)
        elif action == '#Push_Number':
            self.codegen.Push_Number(tup)
        elif action == '#Push_Relation':
            self.codegen.Push_Relation(tup)
        elif action == '#Save_Operation':
            self.codegen.Save_Operation()
        elif action == '#Assignment_Op':
            self.codegen.Assignment_Op()
        elif action == '#Mult_Div_Operation':
            self.codegen.Mult_Div_Operation(tup)
        elif action == '#Arr_Args_Def':
            self.codegen.Arr_Args_Def(tup)
        elif action == '#Array_Indices':
            self.codegen.Array_Indices(tup)
        elif action == '#output_function':
            self.codegen.output_function(tup)
        elif action == '#save':
            self.codegen.save(tup)
        elif action == '#label':
            self.codegen.label(tup)
        elif action == '#Save_JPF':
            self.codegen.Save_JPF()
        elif action == '#jump':
            self.codegen.jump(tup)
        elif action == '#While_Jumps':
            self.codegen.While_Jumps(tup)
        elif action == '#Negative':
            self.codegen.Negative(tup)
        elif action == '#Remove_Extra_Data':
            self.codegen.Remove_Extra_Data(tup)
        elif action == '#end_of_loop_with_break':
            self.codegen.end_of_loop_with_break(tup)
        elif action == '#new_break':
            self.codegen.new_break(tup)
        elif action == '#back_to_scope_with_end_break':
            self.codegen.back_to_scope_with_end_break(tup)
        elif action == '#Func_Ending':
            self.codegen.Func_Ending(tup)
        elif action == '#call_function':
            self.codegen.call_function(tup)
        elif action == '#Param_Def':
            self.codegen.Param_Def(tup)
        elif action == '#Push_index':
            self.codegen.Push_index(tup)
        elif action == '#Func_Beginning':
            self.codegen.Func_Beginning(tup)
        elif action == '#Mark_Return':
            self.codegen.Mark_Return(tup)
        elif action == '#Push_Return_Point':
            self.codegen.Push_Return_Point(tup)
        elif action == '#Back_to_Main':
            self.codegen.Back_to_Main(tup)
        elif action == '#close_return':
            self.codegen.close_return(tup)
        elif action == '#Next_Scope':
            self.codegen.Next_Scope(tup)
        elif action == '#Prev_Scope':
            self.codegen.Prev_Scope(tup)
        else:
            self.isActionSymbol = False


    def run(self):
        token = self.scanner.get_next_token()
        while token[0] != 'EOF':
            if token[0] == 'ID' or token[0] == 'NUM':
                exe_token = token[0]
            else:
                exe_token = token[1]
            top_stack = self.stack.pop()
            top_node = self.stack_nodes.pop()
            print('TOKEN: ',token, 'top_stack ',top_stack)
            # print(self.stack)
            # while top_stack.startswith('#'):
            #     print('?????????, ', exe_token)
            #     self.codegen_caller(top_stack, token[1])
            #     top_stack = self.stack.pop()
            #     top_node = self.stack_nodes.pop()
            while top_stack == 'epsilon' or top_stack.startswith('#'):
                if top_stack.startswith('#'):
                    mio = self.scanner.lineno, token[0], token[1]
                    self.codegen_caller(top_stack, mio)
                    top_stack = self.stack.pop()
                    top_node = self.stack_nodes.pop()
                else:
                    top_stack = self.stack.pop()
                    top_node = self.stack_nodes.pop()
            print('new_top_stack', top_stack)

            if is_terminal(top_stack):
                if top_stack == exe_token:
                    self.nodes[top_node].name = f"({token[0]}, {token[1]})"
                    token = self.scanner.get_next_token()
                else:
                    if top_stack == '$':
                        eof = Node('$', parent=self.nodes[0])
                        print_tree(self.nodes[0], self.parse_tree)
                        if len(self.codegen.semantic_errors) > 0:
                            self.save_semantic_errors()
                        else:
                            self.output_phase3()
                        exit()
                    else:
                        self.write_error(f"missing {top_stack}")
                        self.nodes[top_node].parent = None
            else:
                if exe_token in self.parse_table[top_stack]:
                    RHS = self.parse_table[top_stack][exe_token].split()
                    # print('!!!!!',RHS)
                    for x in RHS:
                        self.nodes.append(Node(x, parent=self.nodes[top_node]))
                    RHS = RHS[::-1]
                    size = 1
                    for x in RHS:
                        self.stack.append(x)
                        self.stack_nodes.append(len(self.nodes) - size)
                        size += 1
                    # print(self.stack)
                elif exe_token in self.follow[top_stack]:
                    self.write_error(f"missing {top_stack}")
                    self.nodes[top_node].parent = None
                else:
                    self.write_error(f"illegal {exe_token}")
                    self.stack.append(top_stack)
                    self.stack_nodes.append(top_node)
                    token = self.scanner.get_next_token()

        wrote = False
        top_stack = self.stack.pop()
        top_node = self.stack_nodes.pop()
        while not is_terminal(top_stack) or top_stack == 'epsilon':
            if top_stack == 'epsilon' or top_stack.startswith('#'):
                if top_stack.startswith('#'):
                    mio = self.scanner.lineno, token[0], token[1]
                    self.codegen_caller(top_stack, mio)
                    top_stack = self.stack.pop()
                    top_node = self.stack_nodes.pop()
                else:
                    top_stack = self.stack.pop()
                    top_node = self.stack_nodes.pop()
            elif '$' in self.parse_table[top_stack]:
                RHS = self.parse_table[top_stack]['$'].split()
                for x in RHS:
                    self.nodes.append(Node(x, parent=self.nodes[top_node]))
                RHS = RHS[::-1]
                size = 1
                for x in RHS:
                    self.stack.append(x)
                    self.stack_nodes.append(len(self.nodes) - size)
                    size += 1
                top_stack = self.stack.pop()
                top_node = self.stack_nodes.pop()
            else:
                wrote = True
                self.write_error("Unexpected EOF")
                break

        if top_stack != '$' and not wrote:
            wrote = True
            self.write_error("Unexpected EOF")
        if wrote:
            self.nodes[top_node].parent = None
            while len(self.stack_nodes) > 1:
                top_node = self.stack_nodes.pop()
                self.nodes[top_node].parent = None
        else:
            eof = Node('$', parent=self.nodes[0])

        if self.error_count == 0:
            self.errors.write("There is no syntax error.\n")
        print_tree(self.nodes[0], self.parse_tree)
        print('From here we reach to output')
        if len(self.codegen.semantic_errors) > 0:
            self.save_semantic_errors()
        else:
            self.output_phase3()

    def output_phase3(self):
        self.semantic_error_file.write('The input program is semantically correct.')
        for idx in sorted(self.codegen.program_block.keys()):
            self.output_file_phase3.write(f'{idx}\t{self.codegen.program_block[idx]}\n')

    def save_semantic_errors(self):
        for idx in self.codegen.semantic_errors:
            self.semantic_error_file.write(f'{idx}\n')
        self.output_file_phase3.write('The code has not been generated.')
        pass


def is_terminal(word):
    terminals = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '=', '==', '*', '/', "if", "else", "void", "int", "while",
                 "break", "return", "endif", 'ID', 'NUM', '$', 'epsilon'}
    return word in terminals
