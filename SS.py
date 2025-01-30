class SS:
    def __init__(self):
        self.stack = []

    def push(self, element):
        self.stack.append(element)

    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            return None
    def is_Empty(self):
        return len(self.stack) == 0

    def pop_with_num(self, number):
        if len(self.stack) >= number:
            a, b, c = self.stack.pop(), self.stack.pop(), self.stack.pop()
            return a, b, c
        else:
            return None
    def access_members(self, index):
        return self.stack[index]