from pathlib import Path
from shutil import rmtree
from typing import Any

import click
import notter.constants as ncons
from notter.utils import load_config, persist_config_after


class Notter:
    def __init__(self) -> None:
        self.config = {}
        self.config["initialized"] = False

    @persist_config_after
    def configure(self, src_folder: Path) -> None:
        self.path = src_folder.parent / ".notter"
        self.config[ncons.CONFIG_PATH] = str(self.path / ncons.CONFIG_FILENAME)
        self.config[ncons.SRC_PATH] = str(src_folder)
        self.config[ncons.PATH] = str(self.path)
        self.config[ncons.ASSUMPTIONS_PATH] = str(self.path / ncons.ASSUMPTIONS_DIRNAME)
        self.config[ncons.NOTES_PATH] = str(self.path / ncons.NOTES_DIRNAME)
        self.config[ncons.TODOS_PATH] = str(self.path / ncons.TODOS_DIRNAME)
        self.init_notter_folders()

    def init_notter_folders(self) -> None:
        if self.get_config("initialized"):
            click.secho(f"Notter folders found at location: {self.path}", fg="red")
        else:
            click.secho(f"Creating Notter folders at location: {self.path}", fg="yellow")
            Path(self.get_config(ncons.PATH)).mkdir(parents=True, exist_ok=True)
            Path(self.get_config(ncons.ASSUMPTIONS_PATH)).mkdir(parents=True, exist_ok=True)
            Path(self.get_config(ncons.NOTES_PATH)).mkdir(parents=True, exist_ok=True)
            Path(self.get_config(ncons.TODOS_PATH)).mkdir(parents=True, exist_ok=True)
            self.set_config("initialized", True)

    def load(self, src_folder: str) -> None:
        src_path = Path(src_folder).resolve()
        parent_path = src_path.parent
        notter_path = parent_path / ".notter"
        notter_config_file = str(notter_path / ncons.CONFIG_FILENAME)
        loaded_config = load_config(notter_config_file)
        if not loaded_config:
            click.secho("Could not load Notter configuration", fg="red")
            quit()

        self.config = loaded_config
        click.secho(f"Loaded Notter config from file: {notter_config_file}", fg="green")

    def destroy(self) -> None:
        if not self.get_config("initialized"):
            click.secho("No Notter instance is found, nothing to delete", fg="red")
        else:
            # TODO: Make sure it is not a critical path
            notter_path = self.get_config(ncons.PATH)
            rmtree(notter_path)
            click.secho(f"Notter instance deleted", fg="green")

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
