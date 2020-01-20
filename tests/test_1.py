import unittest
import pprint
import enum
from abc import abstractmethod
from obj2cli import Parser, Argparse


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


class Cls1:
    def __init__(self, arg1: str, arg2: int = 0):
        self.arg1 = arg1
        self.arg2 = arg2

    def fn(self, argf1: bool) -> dict:
        print("fn", argf1)
        self.argf1 = argf1
        return self.__dict__

    def fnenum(self, arge1: Color) -> dict:
        self.arge1 = arge1
        return self.__dict__

    @classmethod
    def clsfn(cls, argc1: bool) -> int:
        print("clsfn", argc1)
        return 0

    @staticmethod
    def stfn(args1: bool) -> int:
        print("stfn", args1)
        return 0

    @abstractmethod
    def absfn(self, arga1: bool) -> int:
        pass

    def gen1(self, n: int):
        print("gen1", n)
        for i in range(n):
            yield i

    @property
    def propfn(self) -> int:
        print("propfn")
        return 123

    def fn2(self, n: int, *args, **kwargs) -> int:
        print("fn2", n, args, kwargs)
        return 1234 + len(args) + len(kwargs)

    def fn3(self, n: int, *, v1: str) -> int:
        return 12345

    def fn4(self, n: int, v1: str, / ) -> int:
        return 12345


class Cls2:
    def fn(self):
        return "hello"


class TestParser(unittest.TestCase):
    def test1(self):
        ps = Parser()
        pcls1 = ps.parse_cls(Cls1)
        print("call by class")
        pprint.pprint(pcls1)
        pcls2 = ps.parse_cls(Cls1("hello"))
        print("call by object")
        pprint.pprint(pcls2)
        ap = Argparse()
        p = ap.convert_cls(pcls1)
        print("p", p)
        print("usage", p.format_usage())
        print("help", p.format_help())
