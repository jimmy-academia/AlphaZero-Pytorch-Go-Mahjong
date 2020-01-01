class something(object):
    """docstring for something"""
    def __init__(self):
        super(something, self).__init__()
        self.a = [1,2,3,4,5]
        self.b = {1:1,2:2,3:3}
    def print(self):
        print(self.a)
        print(self.b)

    # def copy(self):
    #     class copyofsomething(something):
    #         pass
    #     B = copyofsomething()
    #     return B


A = something()


A.a = [2,3,4,5,3,2,3,4]

import copy
B = copy.deepcopy(A)

# class newthing(A.__class__):
    # pass
# B = newthing()
# B = A.copy()

A.a = [2,3,4,5,6]
A.print()
B.print()

import code
code.interact(local=locals())
        