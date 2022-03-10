from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional, Tuple

import click
from click import Context, pass_context

from notter.notter import Notter

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
pass_notter = click.make_pass_decorator(Notter)


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Print Notter version.")
@click.pass_context
def cli(ctx, version) -> None:
    if not ctx.obj:
        click.echo("Setting context object")
        ctx.obj = Notter()

    if version:
        click.echo(f'Notter {pkg_version("notter")}')


@cli.command()
@click.argument(
    "src",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
)
@pass_notter
def init(notter: Notter, src: str) -> None:
    """Initialize Notter tool"""
    click.echo(f"Using {src} as source folder.")
    src_path = Path(src)
    notter.configure(src_path)


@cli.command()
@click.option("--get", help="get value of a config")
@click.option("--set", "setc", nargs=2, type=str, help="set a config with a key-value pair")
@click.option("--all", "allc", is_flag=True, help="show all the config")
@pass_context
def config(ctx: Context, get: Optional[str], setc: Optional[Tuple[str, str]], allc: bool) -> None:
    """Configure Notter configuration."""
    click.echo(f"CONFIG_PATH: Passed notter obj: {ctx.obj}")

    notter = ctx.obj
    if get:
        value = notter.get_config(get)
        click.echo(value)
    elif setc:
        key, value = setc
        notter.set_config(key, value)
    elif allc:
        click.echo(notter.repr_config())


@cli.command()
@click.confirmation_option()
@pass_notter
@click.pass_context
def delete(ctx: Context, notter: Notter):
    """Deletes configured Notter instance"""
    click.echo(f"DELETE: Passed notter obj: {notter}")
    notter.destroy()
    ctx.obj = None


if __name__ == "__main__":
    # cli(["init", "./tests/test2"])
    # cli(["config", "--set", "name", "taylan"])
    # cli(["config", "--get", "name"])
    pass
