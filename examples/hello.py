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

_Cls1_option = [
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


def Cls1_option(func):
    @functools.wraps(func)
    def wrap(verbose, arg1, arg2, *args, **kwargs):
        set_verbose(verbose)
        obj = Cls1(arg1, arg2)
        return func(obj, *args, **kwargs)
    return multi_options(_common_option + _Cls1_option)(wrap)


@cli.command()
@Cls1_option
@click.option("--arga1", type=bool)
def absfn(obj, arga1):
    res = obj.absfn(arga1)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
def clsfn(obj, ):
    res = obj.clsfn()
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--argf1", type=bool)
def fn(obj, argf1):
    res = obj.fn(argf1)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--n", type=int)
@click.option("--args", type=str)
@click.option("--kwargs", type=str)
def fn2(obj, n, args, kwargs):
    res = obj.fn2(n, args, kwargs)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--n", type=int)
@click.option("--v1", type=str)
def fn3(obj, n, v1):
    res = obj.fn3(n, v1)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--n", type=int)
@click.option("--v1", type=str)
def fn4(obj, n, v1):
    res = obj.fn4(n, v1)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--arge1", type=int)
def fnenum(obj, arge1):
    res = obj.fnenum(arge1)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
@click.option("--n", type=int)
def gen1(obj, n):
    res = obj.gen1(n)
    log.debug("result: %s", res)


@cli.command()
@Cls1_option
def stfn(obj, ):
    res = obj.stfn()
    log.debug("result: %s", res)


if __name__ == "__main__":
    cli()
