import json
import os
from typing import Any, Dict, Optional

import click

import notter.constants as ncons


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def load_config(config_file: str) -> Optional[Dict[str, Any]]:
    config_data = None
    try:
        with open(config_file, "r") as file:
            config_data = json.loads(file.read())
    except FileNotFoundError:
        click.secho(f"Could not load Notter config from: {config_file}", fg="red")

    return config_data


def convert_to_local_path(filepath: str, src_path: str) -> str:
    filepath = filepath.replace(src_path, "")
    if filepath.startswith(os.sep):
        filepath = filepath.lstrip(os.sep)

    return filepath


def persist_config_after(function):
    def wrapper(self, *args, **kwargs):
        retval = function(self, *args, **kwargs)

        config_file = self.get_config(ncons.CONFIG_PATH)
        with open(config_file, "w+") as file:
            json.dump(self.config, file, indent=4)

        # click.secho("Notter config updated", fg="green")
        return retval

    return wrapper
