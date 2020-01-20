import sys
import obj2cli


class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def call1(self, c, d):
        print("hello {}: {}, c={}, d={}".format(self.__class__.__name__, self.__dict__, c, d))


class B(A):
    pass


if __name__ == "__main__":
    obj2cli.main_cls({A: A, B: B}, sys.argv[1:])
