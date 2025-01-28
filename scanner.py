# scanner.py - scanner class definition

class Scanner:
    def __init__(self, input_file):
        self.lineno = 1
        self.last_char = None
        self.token = ""
        self.state = 0
        self.file = open(input_file, "r")
        # self.tokens = open("tokens.txt", "a")
        # self.errors = open("lexical_errors.txt", "a")
        # self.symbol_table = open("symbol_table.txt", "a")
        # self.init_file()
        # self.init_write_symbol_table()
        self.error_count = 0
        self.symbol_num = 9
        self.tokens_nl = True
        self.errors_nl = True
        self.comment_nl = True
        self.comment_sl = 1
        self.comment_not_s = True
        self.symbol_set = set()

    # def init_file(self):
    #     self.tokens = open("tokens.txt", "w")
    #     self.errors = open("lexical_errors.txt", "w")
    #     self.symbol_table = open("symbol_table.txt", "w")
    #
    # def init_write_symbol_table(self):
    #     keyword_list = ["break", "else", "if", "endif", "int", "while", "return", "void"]
    #     for i in range(len(keyword_list)):
    #         self.symbol_table.write(f"{i+1}.\t{keyword_list[i]}\n")


    def get_next_char(self):
        if self.last_char:
            char = self.last_char
            self.last_char = None
            return char

        char = self.file.read(1)
        if char == '':  # EOF
            return None
        return char

    def write_token(self, token_type):
        if self.tokens_nl:
            # self.tokens.write(f"{self.lineno}.\t")
            self.tokens_nl = False
        # self.tokens.write(f"({token_type}, {self.token}) ")


    def new_line(self):
        self.lineno += 1
        if not self.tokens_nl:
            self.tokens_nl = True
            # self.tokens.write("\n")
        if not self.errors_nl:
            self.errors_nl = True
            # self.errors.write("\n")


    def write_error(self, error_type):
        self.error_count += 1
        if self.errors_nl:
            # self.errors.write(f"{self.lineno}.\t")
            self.errors_nl = False
        else:
            pass
            # self.errors.write(" ")
        # self.errors.write(f"({self.token}, {error_type})")
        self.token = ""
        self.state = 0

    def add_to_symbol_table(self):
        if self.token not in self.symbol_set:
            # self.symbol_table.write(f"{self.symbol_num}.\t{self.token}\n")
            self.symbol_num += 1
            self.symbol_set.add(self.token)

    def write_comment_error(self):
        self.error_count += 1
        if self.comment_nl:
            # self.errors.write(f"{self.comment_sl}.\t")
            if self.comment_sl == self.lineno:
                self.errors_nl = False
        else:
            pass
            # self.errors.write(" ")
        # self.errors.write(f"({self.token[:7]}..., Unclosed comment)")
        self.token = ""
        self.state = 0


    def get_next_token(self):
        self.token = ""
        self.state = 0

        while True:
            char = self.get_next_char()


            if self.state == 0:
                if char is None:
                    if self.error_count == 0:
                        pass
                        # self.errors.write("There is no lexical error.")
                    return 'EOF', '$'
                self.token += char
                if char.isdigit():
                    self.state = 1
                elif char.isalpha():
                    self.state = 2
                elif char == '=':
                    self.state = 3
                elif char == '*':
                    self.state = 4
                elif char == '/':
                    self.state = 5
                elif is_symbol(char):
                    self.write_token("SYMBOL")
                    return 'SYMBOL', self.token
                elif is_whitespace(char):
                    self.token = ""
                    if char == '\n':
                        self.new_line()
                else:
                    pass
                    self.write_error("Invalid input")


            elif self.state == 1:
                if is_special_character(char):
                    self.last_char = char
                    self.write_token("NUM")
                    return 'NUM', self.token
                elif char.isdigit():
                    self.token += char
                else:
                    self.token += char
                    self.write_error("Invalid number")


            elif self.state == 2:
                if is_special_character(char):
                    self.last_char = char
                    if is_keyword(self.token):
                        self.write_token("KEYWORD")
                        return 'KEYWORD', self.token
                    else:
                        self.add_to_symbol_table()
                        self.write_token("ID")
                        return 'ID', self.token
                elif char.isdigit() or char.isalpha():
                    self.token += char
                else:
                    self.token += char
                    self.write_error("Invalid input")


            elif self.state == 3:
                if char == '=':
                    self.token += char
                    self.write_token("SYMBOL")
                    return 'SYMBOL', self.token
                elif is_special_character(char) or char.isalpha() or char.isdigit():
                    self.last_char = char
                    self.write_token("SYMBOL")
                    return 'SYMBOL', self.token
                else:
                    self.token += char
                    self.write_error("Invalid input")


            elif self.state == 4:
                if char == '/':
                    self.token += char
                    self.write_error("Unmatched comment")
                elif is_special_character(char) or char.isalpha() or char.isdigit():
                    self.last_char = char
                    self.write_token("SYMBOL")
                    return 'SYMBOL', self.token
                else:
                    self.token += char
                    self.write_error("Invalid input")


            elif self.state == 5:
                if char == '/':
                    self.token += char
                    self.state = 6
                elif char == '*':
                    self.token += char
                    self.state = 7
                elif is_special_character(char) or char.isalpha() or char.isdigit():
                    self.last_char = char
                    self.write_token("SYMBOL")
                    return 'SYMBOL', self.token
                else:
                    self.token += char
                    self.write_error("Invalid input")


            elif self.state == 6:
                if char == '\n' or char is None:
                    self.last_char = char
                    self.token = ""
                    self.state = 0
                else:
                    self.state = 6
                    self.token += char


            elif self.state == 7:
                if self.comment_not_s:
                    self.comment_sl = self.lineno
                    self.comment_nl = self.errors_nl
                    self.comment_not_s = False
                if char == '*':
                    self.token += char
                    self.state = 8
                elif char is None:
                    self.last_char = char
                    self.write_comment_error()
                else:
                    self.token += char
                    if char == '\n':
                        self.new_line()


            elif self.state == 8:
                if char == '/':
                    self.token = ""
                    self.state = 0
                    self.comment_not_s = True
                elif char is None:
                    self.last_char = char
                    self.write_comment_error()
                elif char == '*':
                    self.token += char
                else:
                    self.token += char
                    self.state = 7
                    if char == '\n':
                        self.new_line()


def is_keyword(token):
    keywords = {"if", "else", "void", "int", "while", "break", "return", "endif"}
    return token in keywords

def is_whitespace(char):
    whitespaces = {' ', '\n', '\r', '\t', '\v', '\f', None}
    return char in whitespaces

def is_symbol(char):
    symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<'}
    return char in symbols

def is_special_character(char):
    special_characters = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/',
                          '=', '<', ' ', '\n', '\r', '\t', '\v', '\f', None}
    return char in special_characters