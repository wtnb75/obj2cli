import sys
import obj2cli


class A:
    def __init__(self, arg1, arg2):
        self.a = arg1
        self.b = arg2

    def call1(self, c, d=None):
        print("hello {} c={}, d={}".format(self.__dict__, c, d))


if __name__ == "__main__":
    obj2cli.main_single(A, A, sys.argv[1:])
