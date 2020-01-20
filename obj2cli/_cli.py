import sys
from logging import getLogger, DEBUG, INFO, WARNING, basicConfig
import importlib
import datetime
import argparse
import json
import yaml
import toml
import pickle
import marshal
import pprint
from .main import main_single, main_func
from .version import VERSION

log = getLogger(__name__)


def output_bytype(s):
    if s is None:
        return
    elif isinstance(s, (str, int, float, bool)):
        print(s)
    else:
        json.dump(s, sys.stdout, ensure_ascii=False)


formats = {
    "json": lambda f: json.dump(f, sys.stdout, ensure_ascii=False),
    "yaml": lambda f: yaml.dump(f, stream=sys.stdout),
    "pprint": lambda f: pprint.pprint(f),
    "print": lambda f: print(f),
    "log": lambda f: log.info("%s", f),
    "toml": lambda f: toml.dump(f, f=sys.stdout),
    "pickle": lambda f: pickle.dump(f, sys.stdout.buffer),
    "marshal": lambda f: marshal.dump(f, sys.stdout.buffer),
    "bytype": output_bytype,
}

typemap = {
    'int': int,
    'str': str,
    'dict': dict,
    'datetime': datetime.datetime,
    'time': datetime.time,
    'date': datetime.date,
    'float': float,
}


def main():
    parser = argparse.ArgumentParser(prog="obj2cli")
    parser.add_argument("--version", action="version", version='%(prog)s ' + VERSION)
    parser.add_argument("--default-type", type=str,
                        default='str', dest='deftype', choices=typemap.keys())
    parser.add_argument("--module", type=str, required=True)
    parser.add_argument("--package", type=str, default=None)
    parser.add_argument("--interface", dest="ifklass", type=str)
    parser.add_argument("--class", dest="klass", type=str)
    parser.add_argument("--function", type=str)
    parser.add_argument("--positional", action="store_true", default=False)
    parser.add_argument("--noskip", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--format", choices=formats.keys(), default="bytype")
    parser.add_argument("args", nargs='*')
    parsed = parser.parse_args()
    # fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    fmt = '%(asctime)s %(levelname)s %(message)s'
    if parsed.verbose:
        basicConfig(level=DEBUG, format=fmt)
    elif parsed.quiet:
        basicConfig(level=WARNING, format=fmt)
    else:
        basicConfig(level=INFO, format=fmt)
    log.debug("parsed: %s", parsed)

    deftype = typemap.get(parsed.deftype, str)

    log.debug("loading module %s, package=%s", parsed.module, parsed.package)
    mod = importlib.import_module(name=parsed.module, package=parsed.package)
    if parsed.ifklass is None:
        ifclsname = parsed.klass
    else:
        ifclsname = parsed.ifklass
    if ifclsname is not None:
        ifcls = getattr(mod, ifclsname)
        cls = getattr(mod, parsed.klass)
        log.debug("class: %s, if=%s", cls, ifcls)
        res = main_single(ifcls, cls, parsed.args,
                          deftype=deftype, positional=parsed.positional)
        log.debug("result: %s", res)
        formats.get(parsed.format, lambda f: print(f))(res)
    elif parsed.function is not None:
        fn = getattr(mod, parsed.function)
        log.debug("func: %s", fn)
        res = main_func(fn, parsed.args, noskip=parsed.noskip,
                        deftype=deftype, positional=parsed.positional)
        log.debug("result: %s", res)
        formats.get(parsed.format, lambda f: print(f))(res)


if __name__ == "__main__":
    main()
