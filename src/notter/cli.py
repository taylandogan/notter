import os
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional, Tuple

import click
from click import Context, pass_context

from notter.notter import Notter
import notter.constants as ncons

SRC_PATH_VAR = "SRC_PATH"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

pass_notter = click.make_pass_decorator(Notter)


@click.group(invoke_without_command=True)
@click.option("--init", is_flag=True, help="Initialize Notter tool.")
@click.option("--version", is_flag=True, help="Print Notter version.")
@click.pass_context
def cli(ctx, init, version) -> None:
    src_path = os.getenv(SRC_PATH_VAR)
    if not src_path:
        click.secho(
            f"Could not find the source folder. Please export your source folder as the environment variable: `{SRC_PATH_VAR}`",
            fg="red",
        )
        quit()

    notter = Notter()
    if init:
        # TODO: Do not initialize if the Notter instance is already there
        click.echo(f"Initializing Notter with `{src_path}` as source folder.")
        notter.configure(Path(src_path))
    else:
        notter.load(src_path)
    ctx.obj = notter

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
@pass_notter
def config(notter: Notter, get: Optional[str], setc: Optional[Tuple[str, str]], allc: bool) -> None:
    """Configure Notter configuration."""
    if get:
        value = notter.get_config(get)
        click.echo(value)
    elif setc:
        key, value = setc
        notter.set_config(key, value)
    elif allc:
        click.echo(notter.repr_config())


@cli.command()
@pass_notter
@click.pass_context
def destroy(ctx: Context, notter: Notter):
    """Deletes configured Notter instance"""
    notter_path = notter.get_config(ncons.PATH)
    click.confirm(f"Do you really want to delete the Notter instance initialized at `{notter_path}` ?", abort=True)
    notter.destroy()
    ctx.obj = None


if __name__ == "__main__":
    # cli(["init", "./tests/test2"])
    # cli(["config", "--set", "name", "taylan"])
    # cli(["config", "--get", "name"])
    pass
