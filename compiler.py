# Erfan Mohammadi - 40017052
# Dorsa Sharifi - 401170604

from parser import Parser

if __name__ == "__main__":

    input_file = "input.txt"
    first = "inputs/first.txt"
    follow = "inputs/follow.txt"
    rules = "inputs/grammar_rules.txt"


    # scanner = Scanner(input_file)
    parser = Parser(first, follow, rules, input_file)

    parser.run()

    # while True:
    #     token = scanner.get_next_token()
    #     print(token)
    #     if token == ('$', 'EOF'):
    #         break
