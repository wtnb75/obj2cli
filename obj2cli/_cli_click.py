import os
import sys
import subprocess
import functools
import importlib
from logging import getLogger, basicConfig, INFO, DEBUG
import pprint
import yaml
from jinja2 import Environment
import pickle
import click
import difflib
import pkg_resources
import io
import pkgutil
from .parser import Parser
from .version import VERSION

log = getLogger(__name__)

out_formats = {
    'pickle': lambda d, f: pickle.dump(d, f),
    'yaml': lambda d, f: yaml.dump(d, stream=f),
    'pprint': lambda d, f: f.write(pprint.pformat(d).encode("utf-8")),
}

in_formats = {
    'pickle': lambda f: pickle.load(f),
    'yaml': lambda f: yaml.load(f, Loader=yaml.FullLoader),
}


@click.version_option(version=VERSION, prog_name="obj2cli")
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


def set_verbose(flag):
    fmt = '%(asctime)s %(levelname)s %(message)s'
    if flag:
        basicConfig(level=DEBUG, format=fmt)
    else:
        basicConfig(level=INFO, format=fmt)


_cli_option = [
    click.option("--verbose/--no-verbose"),
]

_cls_option = _cli_option + [
    click.option("--module", type=str),
    click.option("--package", type=str),
    click.option("--class", "klass", type=str),
]

out_option = [
    click.option("--output", type=click.File('wb'),
                 default=sys.stdout.buffer, show_default="STDOUT"),
    click.option("--format", type=click.Choice(out_formats.keys()),
                 default="yaml", show_default=True),
]

in_option = [
    click.option("--input", type=click.File('rb'),
                 default=sys.stdin.buffer, show_default="STDIN"),
    click.option("--format", type=click.Choice(in_formats.keys()),
                 default="yaml", show_default=True),
]


def multi_options(decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco


def cli_option(func):
    @functools.wraps(func)
    def wrap(verbose, *args, **kwargs):
        set_verbose(verbose)
        return func(*args, **kwargs)
    return multi_options(_cli_option)(wrap)


def cls_option(func):
    @functools.wraps(func)
    def wrap(verbose, klass, module, package, *args, **kwargs):
        set_verbose(verbose)
        log.debug("loading module %s, package=%s", module, package)
        mod = importlib.import_module(name=module, package=package)
        if klass is not None:
            cls = getattr(mod, klass)
            log.debug("class: %s", cls)
        else:
            cls = None
        return func(cls, *args, **kwargs)
    return multi_options(_cls_option)(wrap)


def resource_option(dest, dirname=None, ext=""):
    if dirname is None:
        dirname = dest

    def _resource_option(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            val = kwargs.pop(dest)
            exval = kwargs.pop("{}_example".format(dest))
            if val is not None:
                kwargs[dest] = open(val, 'rb')
            else:
                kwargs[dest] = io.BytesIO(pkgutil.get_data(
                    __package__, os.path.join(dirname, exval + ext)))
            return func(*args, **kwargs)

        try:
            names = pkg_resources.resource_listdir(__package__, dirname)
        except FileNotFoundError:
            names = []
        log.debug("resources in pkg=%s, dir=%s: %s",
                  __package__, dirname, names)
        names = [x[:-len(ext)]
                 for x in filter(lambda f: f.endswith(ext), names)]
        opts = [
            click.option("--{}".format(dest), type=click.Path()),
            click.option("--{}-example".format(dest),
                         type=click.Choice(names)),
        ]
        return multi_options(opts)(wrap)
    return _resource_option


@cli.command()
@cls_option
@multi_options(out_option)
def parse(cls, format, output):
    ps = Parser()
    log.debug("start parse: %s", cls.__name__)
    data = ps.parse_cls(cls)
    out_formats.get(format)(data, output)
    # pickle.dump(data, sys.stdout.buffer)


def template_args(data, cls=None):
    ps = Parser()
    funcs = {}
    for k, v in data.items():
        if k in ("__classmeta__", "__init__", "doc"):
            continue
        funcs[k] = ps.fn_args(v)
    if cls is None:
        cls = data.get("__classmeta__", {}).get("class", None)
    return {
        "klass": cls,
        "parsed": data,
        "constructor": ps.fn_args(data.get("__init__", {})),
        "funcs": funcs,
        "classmeta": data.get("__classmeta__", {}),
    }


@cli.command('generate')
@cls_option
@multi_options(in_option)
@resource_option(dest="template", dirname="template", ext="_cli.j2")
@click.option("--autopep8/--no-autopep8", default=False)
def gen(cls, input, format, template, autopep8):
    data = in_formats.get(format)(input)
    env = Environment()
    tmpl = env.from_string(template.read().decode("utf-8"))
    res = tmpl.render(**template_args(data, cls))
    if autopep8:
        p = subprocess.Popen(["autopep8", "-"], stdin=subprocess.PIPE)
        p.communicate(res.encode("utf8"))
    else:
        print(res)


@cli.command()
@cls_option
@multi_options(in_option)
@resource_option(dest="template", dirname="template", ext="_cli.j2")
@click.argument("other", type=click.File('r'), required=True)
def diff(cls, input, format, template, other):
    data = in_formats.get(format)(input)
    env = Environment()
    tmpl = env.from_string(template.read())
    res = tmpl.render(**template_args(data, cls))
    before = other.read().split("\n")
    current = res.split("\n")
    differ = difflib.unified_diff(
        before, current, fromfile="before.py", tofile="current.py", lineterm="")
    print("\n".join(differ))


@cli.command('print')
@cli_option
@multi_options(in_option)
def show(input, format):
    data = in_formats.get(format)(input)
    pprint.pprint(data)


@cli.command('print-tmpl-args')
@cls_option
@multi_options(in_option)
def show_tmplarg(cls, input, format):
    data = in_formats.get(format)(input)
    pprint.pprint(template_args(data, cls))


if __name__ == "__main__":
    cli()
