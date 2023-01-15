from typing import Any, Dict
import click
import json
import notter.constants as ncons


def load_config(config_file) -> Dict[str, Any]:
    config_data = None
    try:
        with open(config_file, "r") as file:
            config_data = json.loads(file.read())
    except FileNotFoundError:
        click.secho(f"Could not load Notter config from: {config_file}", fg="red")

    return config_data


def persist_config_after(function):
    def wrapper(self, *args, **kwargs):
        retval = function(self, *args, **kwargs)

        config_file = self.get_config(ncons.CONFIG_PATH)
        with open(config_file, "w+") as file:
            json.dump(self.config, file)

        click.secho(f"Notter config updated", fg="green")
        return retval

    return wrapper
