import sys
import functools
import importlib
from logging import getLogger, basicConfig, INFO, DEBUG
import pprint
import yaml
from jinja2 import Environment
import pickle
import click
import difflib
from .parser import Parser
from .version import VERSION

log = getLogger(__name__)

out_formats = {
    'pickle': lambda d, f: pickle.dump(d, f),
    'yaml': lambda d, f: yaml.dump(d, stream=f),
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


@cli.command()
@cls_option
@click.option("--format", type=click.Choice(out_formats.keys()), default="yaml")
@click.option("--output", type=click.File('wb'), default=sys.stdout.buffer)
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
@click.option("--input", type=click.File('rb'), default=sys.stdin.buffer)
@click.option("--format", type=click.Choice(in_formats.keys()), default="yaml")
@click.option("--template", type=click.File('r'), required=True)
def gen(cls, input, format, template):
    data = in_formats.get(format)(input)
    env = Environment()
    tmpl = env.from_string(template.read())
    res = tmpl.render(**template_args(data, cls))
    print(res)


@cli.command()
@cls_option
@click.option("--input", type=click.File('rb'), default=sys.stdin.buffer)
@click.option("--format", type=click.Choice(in_formats.keys()), default="yaml")
@click.option("--template", type=click.File('r'), required=True)
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
@click.option("--input", type=click.File('rb'), default=sys.stdin.buffer)
@click.option("--format", type=click.Choice(in_formats.keys()), default="yaml")
def show(input, format):
    data = in_formats.get(format)(input)
    pprint.pprint(data)


if __name__ == "__main__":
    cli()
