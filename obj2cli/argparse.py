from inspect import Parameter
from logging import getLogger
import datetime
import enum
import argparse
import argparse_utils
from .parser import Parser

log = getLogger(__name__)


class Argparse:
    parser = Parser()

    def __init__(self, positional: bool = False):
        self.positional = positional

    def onearg(self, arg, p):
        optname = arg.get("name")
        if len(optname) == 1:
            optname = "-" + optname
        else:
            optname = "--" + optname
        kwargs = {
            'type': arg.get("type", str),
            'default': arg.get("default"),
            'help': arg.get("doc"),
            'metavar': arg.get('type', str).__name__,
        }
        # custom action
        if kwargs.get('type') == datetime.datetime:
            kwargs['action'] = argparse_utils.datetime_action()
            kwargs.pop('type')
        elif kwargs.get('type') == datetime.date:
            kwargs['action'] = argparse_utils.date_action()
            kwargs.pop('type')
        elif kwargs.get('type') == datetime.time:
            kwargs['action'] = argparse_utils.time_action()
            kwargs.pop('type')
        elif kwargs.get('type') == datetime.timedelta:
            kwargs['action'] = argparse_utils.timedelta_action()
            kwargs.pop('type')
        elif issubclass(kwargs.get('type'), enum.Enum):
            kwargs['action'] = argparse_utils.enum_action(kwargs.get('type'))
            kwargs['help'] = "/".join(kwargs.get('type').__members__.keys())
            kwargs.pop('type')
        elif kwargs.get('type') == dict:
            kwargs['action'] = argparse_utils.json_action()
            kwargs.pop('type')
        elif kwargs.get('type') == bool:
            kwargs.pop('type')
            kwargs.pop('metavar')
            if kwargs.get('default', False):
                kwargs['action'] = "store_false"
            else:
                kwargs['action'] = "store_true"
        log.debug("kwargs %s", kwargs)

        # by kind(positional/keyword)
        if arg.get("kind") == Parameter.POSITIONAL_ONLY:
            p.add_argument(arg.get("name"), **kwargs)
        elif arg.get("kind") == Parameter.VAR_POSITIONAL:
            p.add_argument(arg.get("name"), nargs='*', **kwargs)
        elif arg.get("kind") == Parameter.VAR_KEYWORD:
            pass
            # p.add_argument(optname, **kwargs)
        elif arg.get("kind") == Parameter.POSITIONAL_OR_KEYWORD:
            if self.positional:
                p.add_argument(arg.get("name"), nargs=1, **kwargs)
            else:
                p.add_argument(optname, **kwargs)
        elif arg.get("kind") == Parameter.KEYWORD_ONLY:
            p.add_argument(optname, **kwargs)

    def convert_fn(self, name, data, p=None):
        log.debug("convert_fn name=%s, data=%s", name, data)
        if p is None:
            p = argparse.ArgumentParser(prog=name, description=data.get("doc"))
        else:
            p.description = data.get("doc")
        p.set_defaults(__FUNCNAME__=name, __FUNC__=data.get("fn"))
        log.debug("fn %s, args=%s", name, [
                  x.get("name") for x in data.get("args", [])])
        args = self.parser.fn_args(data)
        log.debug("args=%s", [x.get("name") for x in args])
        for i in args:
            self.onearg(i, p)
        return p

    def convert_cls(self, data, p=None):
        if p is None:
            name = data.get("__classmeta__", {}).get("name")
            p = argparse.ArgumentParser(prog=name, description=data.get("doc"))
        else:
            p.description = data.get("doc")
        p.set_defaults(__CLASSMETA__=data.get("__classmeta__"))
        self.convert_fn("new", data.get("__init__"), p)
        subs = p.add_subparsers()
        for k, v in data.items():
            log.debug("do1 k=%s v=%s", k, v)
            if k == "__classmeta__":
                log.debug("classmeta %s", v)
                continue
            if k == "__init__":
                log.debug("new %s", v)
                continue
            if k == "doc":
                log.debug("doc %s", v)
                continue
            s = subs.add_parser(k, help=v.get("doc"))
            self.convert_fn(k, v, s)
        return p

    def fn_arg(self, fdata, parsed):
        kw = {}
        pos = []
        for ag in fdata.get("args", []):
            name = ag.get("name")
            if name is None:
                log.debug("name is none")
                continue
            if not hasattr(parsed, name):
                log.debug("has no %s", name)
                continue
            if ag.get("kind") in (Parameter.POSITIONAL_ONLY, Parameter.VAR_POSITIONAL):
                pos.extend(getattr(parsed, name))
            elif ag.get("kind") == Parameter.POSITIONAL_OR_KEYWORD and self.positional:
                pos.extend(getattr(parsed, name))
            else:
                kw[name] = getattr(parsed, name)
        return kw, pos

    def split_arg(self, data, parsed):
        carg_kw, carg_pos = self.fn_arg(data.get("__init__", {}), parsed)
        farg_kw, farg_pos = self.fn_arg(
            data.get(parsed.__FUNCNAME__, {}), parsed)
        return ((carg_pos, carg_kw), (farg_pos, farg_kw))
