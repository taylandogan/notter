import json
import os
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Optional, Tuple

import click
from click import Context, pass_context

import notter.constants as ncons
from notter.context import NotterContext
from notter.controller import NoteController
from notter.exceptions import NotterException
from notter.model import NoteType
from notter.notter import Notter

SRC_PATH_VAR = "SRC_PATH"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(invoke_without_command=True)
@click.option("--init", nargs=2, type=str, help="Initialize Notter tool with a username & email.")
@click.option("--version", is_flag=True, help="Print Notter version.")
@click.pass_context
def cli(ctx: Context, init: Tuple[str, str], version: bool) -> None:
    src_path = os.getenv(SRC_PATH_VAR)
    if not src_path:
        click.secho(
            f"Could not find the source folder.\
            Please export your source folder as the environment variable: `{SRC_PATH_VAR}`",
            fg="red",
        )
        sys.exit(1)

    # Initialize Notter instance
    notter = Notter()

    if version:
        click.echo(f'{pkg_version("notter")}')
        return

    if not init:
        notter.load(src_path)
    else:
        # TODO: Do not initialize if the Notter instance is already there
        username, email = init
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
def destroy(ctx: Context) -> None:
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
        click.secho("Note created", fg="green")
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
        click.secho("Note updated", fg="green")
    except NotterException as exc:
        click.secho(exc.message, fg="red")


@cli.command()
@click.argument("filepath", type=str)
@click.argument("line", type=int)
@pass_context
def delete(ctx: Context, filepath: str, line: int) -> None:
    try:
        ctx.obj.controller.delete(filepath, line)
        click.secho("Note deleted", fg="green")
    except NotterException as exc:
        click.secho(exc.message, fg="red")


@cli.command()
@pass_context
def discover(ctx: Context) -> None:
    try:
        # TODO: Retrieve tags from user
        tags = ["TODO", "FIXME"]
        comments = ctx.obj.controller.discover(tags)
        click.echo(json.dumps(comments, default=lambda o: o.__dict__))
    except NotterException as exc:
        click.secho(exc.message, fg="red")
