import functools
from logging import getLogger, basicConfig, INFO, DEBUG
import click
from tests.test_1 import Cls1

log = getLogger(__name__)


def set_verbose(flag):
    fmt = '%(asctime)s %(levelname)s %(message)s'
    if flag:
        basicConfig(level=DEBUG, format=fmt)
    else:
        basicConfig(level=INFO, format=fmt)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


_common_option = [
    click.option("--verbose/--no-verbose"),
]

_cls2_option = [
    click.option("--arg1", type=str),
    click.option("--arg2", type=int),
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
    return multi_options(_common_option)(wrap)


def cls_option(func):
    @functools.wraps(func)
    def wrap(verbose, arg1, arg2, *args, **kwargs):
        set_verbose(verbose)
        obj = Cls1(arg1=arg1, arg2=arg2)
        return func(obj, *args, **kwargs)
    return multi_options(_common_option + _cls2_option)(wrap)


@cli.command()
@cls_option
@click.option("--argf1/--no-argf1")
def fn(obj, argf1):
    res = obj.fn(argf1=argf1)
    log.debug("result: %s", res)


if __name__ == "__main__":
    cli()
