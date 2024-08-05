import sys
from pathlib import Path
from shutil import rmtree
from typing import Any, Dict

import click

import notter.constants as ncons
from notter.utils import load_config, persist_config_after


class Notter:
    def __init__(self) -> None:
        self.config: Dict[str, Any] = {}
        self.config[ncons.INITIALIZED_FLAG] = False
        self.config[ncons.DB_INITIALIZED_FLAG] = False

    @persist_config_after
    def configure(self, src_folder: Path) -> None:
        path = src_folder.parent / ".notter"
        self.config[ncons.CONFIG_PATH] = str(path / ncons.CONFIG_FILENAME)
        self.config[ncons.SRC_PATH] = str(src_folder)
        self.config[ncons.PATH] = str(path)
        self.init_notter_folders()

    def init_notter_folders(self) -> None:
        if self.get_config(ncons.INITIALIZED_FLAG):
            click.secho(f"Notter folders found at location: {self.config[ncons.PATH]}", fg="red")
        else:
            click.secho(f"Creating Notter folders at location: {self.config[ncons.PATH]}", fg="yellow")
            Path(self.get_config(ncons.PATH)).mkdir(parents=True, exist_ok=True)
            self.set_config(ncons.INITIALIZED_FLAG, True)

    def load(self, src_folder: str) -> None:
        src_path = Path(src_folder).resolve()
        notter_path = src_path.parent / ".notter"
        notter_config_file = str(notter_path / ncons.CONFIG_FILENAME)
        loaded_config = load_config(notter_config_file)
        if not loaded_config:
            click.secho("Could not load Notter configuration", fg="red")
            sys.exit()

        self.config = loaded_config

    def destroy(self) -> None:
        if not self.get_config(ncons.INITIALIZED_FLAG):
            click.secho("No Notter instance is found, nothing to delete", fg="red")
        else:
            # TODO: Make sure it is not a critical path
            notter_path = self.get_config(ncons.PATH)
            rmtree(notter_path)
            click.secho("Notter instance deleted", fg="green")

    def repr_config(self) -> str:
        repr = "Notter config:\n==============\n"
        configs_str = "\n".join([f"{key}: {value}" for key, value in self.config.items()])
        return repr + configs_str

    def get_config(self, key: str) -> Any:
        value = self.config.get(key, None)
        if value is None:
            click.secho(f"Config `{key}` is not set", fg="red")
            return None

        return value

    @persist_config_after
    def set_config(self, key: str, value: Any) -> None:
        self.config[key] = value
        click.secho(f"Set config `{key}` to `{value}`", fg="yellow")
