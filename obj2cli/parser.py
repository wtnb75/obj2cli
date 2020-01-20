import inspect
from logging import getLogger

log = getLogger(__name__)


class Parser:
    def __init__(self, deftype=str):
        self.deftype = deftype

    def onearg(self, name, param, p):
        log.debug("onearg param: %s", param)
        if param.default != inspect._empty and param.default is not None:
            dflt = param.default
        else:
            dflt = None
        thint = param.annotation
        if thint == inspect._empty:
            if dflt is not None:
                typ = type(dflt)
            else:
                log.debug("default type %s", self.deftype)
                typ = self.deftype
        else:
            typ = thint
        return {
            "name": name,
            "default": dflt,
            "type": typ,
            "kind": param.kind,
        }

    def inspect_flags(self, v):
        res = []
        for f in filter(lambda f: f.startswith("is") and callable(getattr(inspect, f)), dir(inspect)):
            if getattr(inspect, f)(v):
                res.append(f[2:])
        return res

    def parse_fn(self, fn):
        sig = inspect.signature(fn)
        log.debug("signature %s", sig)
        res = {"flags": self.inspect_flags(fn), "args": [], "fn": fn, }
        fndoc = inspect.getdoc(fn)
        if fndoc is not None:
            res['doc'] = fndoc
        for name, param in sig.parameters.items():
            res["args"].append(self.onearg(name, param, res))
        if sig.return_annotation != inspect._empty:
            res["return"] = sig.return_annotation
        return res

    def fn_args(self, data):
        if "staticmethod" in data.get("flags", []):
            args = data.get("args", [])
        elif "classmethod" in data.get("flags", []):
            args = data.get("args", [])
        else:
            args = data.get("args", [])[1:]
        return args

    def parse_new(self, cls):
        return self.parse_fn(cls.__init__)

    def parse_cls(self, cls):
        if not inspect.isclass(cls):
            cls = cls.__class__
        res = {'__init__': self.parse_new(cls),
               '__classmeta__': {
               "class": cls,
               "name": cls.__name__,
               "qualname": cls.__qualname__,
               "flags": self.inspect_flags(cls),
        }}
        clsdoc = inspect.getdoc(cls)
        if clsdoc is not None:
            res['doc'] = clsdoc
        for m, fn in inspect.getmembers(cls, lambda f: callable(f)):
            if m.startswith("_"):
                continue
            try:
                res[m] = self.parse_fn(fn)
            except ValueError as e:
                log.error("cannot inspect %s: %s", m, e)
        if "class" in res.get("__classmeta__"):
            # class
            kls = cls
        else:
            # object
            kls = cls.__class__
        for k, v in kls.__dict__.items():
            if k not in res:
                continue
            if isinstance(v, staticmethod):
                res[k]["flags"].append('staticmethod')
            elif isinstance(v, classmethod):
                res[k]["flags"].append('classmethod')
            elif isinstance(v, property):
                res[k]["flags"].append("property")
        return res
