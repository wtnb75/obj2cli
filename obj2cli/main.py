import argparse
from logging import getLogger
from .parser import Parser
from .argparse import Argparse

log = getLogger(__name__)


def main_cls(clsmap, args, deftype=str, positional=False):
    ps = Parser(deftype)
    ap = Argparse(positional)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    for ifcls, cls in clsmap.items():
        data = ps.parse_cls(ifcls)
        log.debug("if=%s, cls=%s, data: %s", ifcls, cls, data)
        s = sub.add_parser(cls.__name__)
        s.set_defaults(__IFCLASS__=ifcls, __CLASS__=cls)
        ap.convert_cls(data, s)
    parsed = parser.parse_args(args)
    log.debug("parsed: %s dict=%s", parsed, parsed.__dict__)
    carg, farg = ap.split_arg(data, parsed)
    log.debug("carg: %s", carg)
    log.debug("farg: %s", farg)
    obj = parsed.__CLASS__(*carg[0], **carg[1])
    return getattr(obj, parsed.__FUNCNAME__)(*farg[0], **farg[1])


def main_single(ifcls, cls, args, deftype=str, positional=False):
    parser = Parser(deftype)
    ap = Argparse(positional)
    data = parser.parse_cls(ifcls)
    log.debug("if=%s, cls=%s, data: %s", ifcls, cls, data)
    parser = ap.convert_cls(data)
    parsed = parser.parse_args(args)
    log.debug("parsed: %s dict=%s", parsed, parsed.__dict__)
    carg, farg = ap.split_arg(data, parsed)
    obj = cls(*carg[0], **carg[1])
    return getattr(obj, parsed.__FUNCNAME__)(*farg[0], **farg[1])


def main_func(fn, args, noskip=False, deftype=str, positional=False):
    parser = Parser(deftype)
    ap = Argparse(positional)
    log.debug("fn: %s", fn)
    data = parser.parse_fn(fn)
    log.debug("data: %s", data)
    if not noskip:
        data["flags"].append("staticmethod")
    p2 = ap.convert_fn(fn.__name__, data)
    parsed2 = p2.parse_args(args)
    log.debug("parsed2: %s dict=%s", parsed2, parsed2.__dict__)
    kwarg, posarg = ap.fn_arg(data, parsed2)
    log.debug("kwarg=%s, posarg=%s", kwarg, posarg)
    return fn(*posarg, **kwarg)
