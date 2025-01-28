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
        self.stack = ['$', self.rules[0][0]]
        self.error_count = 0
        self.parse_tree = open("parse_tree.txt", "a")
        self.errors = open("syntax_errors.txt", "a")
        self.init_file()
        self.nodes = []
        self.nodes.append(Node(self.rules[0][0]))
        self.stack_nodes = ['$', 0]


    def get_first(self, x):
        if is_terminal(x) or x == 'epsilon':
            return [x]
        else:
            return self.first[x]

    def get_first_rhs(self, rhs):
        elements = list(rhs.split(" "))
        firsts = []
        for i in range(len(elements)):
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

    def write_error(self, error):
        self.error_count += 1
        lineno = self.scanner.lineno
        self.errors.write(f"#{lineno} : syntax error, {error}\n")
        # self.test.write(f"#{lineno} : syntax error, {error}\n")

    def run(self):
        token = self.scanner.get_next_token()
        while token[0] != 'EOF':
            if token[0] == 'ID' or token[0] == 'NUM':
                exe_token = token[0]
            else:
                exe_token = token[1]

            top_stack = self.stack.pop()
            top_node = self.stack_nodes.pop()
            while top_stack == 'epsilon':
                top_stack = self.stack.pop()
                top_node = self.stack_nodes.pop()
            if is_terminal(top_stack):
                if top_stack == exe_token:
                    self.nodes[top_node].name = f"({token[0]}, {token[1]})"
                    token = self.scanner.get_next_token()
                else:
                    if top_stack == '$':
                        eof = Node('$', parent=self.nodes[0])
                        print_tree(self.nodes[0], self.parse_tree)
                        exit()
                    else:
                        self.write_error(f"missing {top_stack}")
                        self.nodes[top_node].parent = None
            else:

                if exe_token in self.parse_table[top_stack]:
                    RHS = self.parse_table[top_stack][exe_token].split()
                    for x in RHS:
                        self.nodes.append(Node(x, parent=self.nodes[top_node]))
                    RHS = RHS[::-1]
                    size = 1
                    for x in RHS:
                        self.stack.append(x)
                        self.stack_nodes.append(len(self.nodes) - size)
                        size += 1
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
            if top_stack == 'epsilon':
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

def is_terminal(word):
    terminals = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<', '=', '==', '*', '/', "if", "else", "void", "int", "while",
                 "break", "return", "endif", 'ID', 'NUM', '$', 'epsilon'}
    return word in terminals
