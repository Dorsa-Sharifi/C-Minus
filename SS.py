class SS:
    def __init__(self):
        self.stack = []

    def push(self, element):
        self.stack.append(element)
        print(self.stack)

    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            return None
    def is_Empty(self):
        return len(self.stack) == 0

    def pop_with_num(self, number):
        a = []
        if len(self.stack) >= number:
            for i in range(number):
                a.append(self.stack.pop())
            return a
        else:
            return None
    def access_members(self, index):
        return self.stack[index]