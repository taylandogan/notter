import os
import subprocess
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional, Tuple

import click
from click import Context, pass_context
from notter.context import NotterContext
from notter.controller import NoteController
from notter.exceptions import NotterException
from notter.note import NoteType

from notter.notter import Notter
import notter.constants as ncons

SRC_PATH_VAR = "SRC_PATH"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


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

    # Initialize Notter instance
    notter = Notter()

    if version:
        click.echo(f'Notter {pkg_version("notter")}')

    if not init:
        notter.load(src_path)
    else:
        # TODO: Do not initialize if the Notter instance is already there
        # TODO: Separate/handle username & config properly
        click.echo(f"Binding your Git user to Notter")
        username_process = subprocess.run(["git", "config", "user.name"], capture_output=True)
        email_process = subprocess.run(["git", "config", "user.email"], capture_output=True)

        if username_process.returncode != 0 or email_process.returncode != 0:
            click.secho(
                "Could not fetch your Git username/email, please make sure that `git config` command works.",
                fg="red",
            )
            quit()

        username = username_process.stdout.decode("utf-8").strip("\n")
        email = email_process.stdout.decode("utf-8").strip("\n")
        if not username or not email:
            click.secho("Git username/email not configured properly.", fg="red")
            quit()

        click.secho(f"Using Git username: {username}", fg="yellow")
        click.secho(f"Initializing Notter with `{src_path}` as source folder.", fg="yellow")
        notter.configure(Path(src_path).resolve())
        notter.set_config(ncons.USERNAME, username)
        notter.set_config(ncons.EMAIL, email)

    controller = NoteController(notter)
    # Add a custom object to context so they are available for other commands
    if ctx.obj is None:
        ctx.obj = NotterContext(notter, controller)


@cli.command()
@click.option("--get", help="get value of a config")
@click.option("--set", "setc", nargs=2, type=str, help="set a config with a key-value pair")
@click.option("--all", "allc", is_flag=True, help="show all the config")
@pass_context
def config(ctx: Context, get: Optional[str], setc: Optional[Tuple[str, str]], allc: bool) -> None:
    """Configure Notter configuration."""
    notter = ctx.obj.notter
    if get:
        value = notter.get_config(get)
        click.echo(value)
    elif setc:
        key, value = setc
        notter.set_config(key, value)
    elif allc:
        click.echo(notter.repr_config())


@cli.command()
@click.pass_context
def destroy(ctx: Context):
    """Deletes configured Notter instance"""
    notter = ctx.obj.notter
    notter_path = notter.get_config(ncons.PATH)
    click.confirm(f"Do you really want to delete the Notter instance initialized at `{notter_path}` ?", abort=True)
    notter.destroy()
    ctx.obj = None


@cli.command()
@click.argument("filepath", type=str)
@click.argument("line", type=int)
@click.argument("text", type=str)
@click.argument("type", type=NoteType)
@pass_context
def create(ctx: Context, filepath: str, line: int, text: str, type: NoteType) -> None:
    try:
        ctx.obj.controller.create(filepath, line, text, type)
        click.secho(f"Note created", fg="green")
    except NotterException as exc:
        click.secho(exc.message, fg="red")


@cli.command()
@click.argument("filepath", type=str)
@click.argument("line", type=int)
@pass_context
def read(ctx: Context, filepath: str, line: int) -> None:
    try:
        note = ctx.obj.controller.read(filepath, line)
        click.echo(note)
    except NotterException as exc:
        click.secho(exc.message, fg="red")


@cli.command()
@click.argument("filepath", type=str)
@click.argument("line", type=int)
@click.argument("text", type=str)
@click.argument("type", type=NoteType)
@pass_context
def update(ctx: Context, filepath: str, line: int, text: str, type: NoteType) -> None:
    try:
        ctx.obj.controller.update(filepath, line, text, type)
        click.secho(f"Note updated", fg="green")
    except NotterException as exc:
        click.secho(exc.message, fg="red")


@cli.command()
@click.argument("filepath", type=str)
@click.argument("line", type=int)
@pass_context
def delete(ctx: Context, filepath: str, line: int) -> None:
    try:
        ctx.obj.controller.delete(filepath, line)
        click.secho(f"Note deleted", fg="green")
    except NotterException as exc:
        click.secho(exc.message, fg="red")
