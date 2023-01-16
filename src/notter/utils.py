from typing import Any, Dict
import click
import json
import notter.constants as ncons


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


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


def persist_index_after(function):
    def wrapper(self, *args, **kwargs):
        retval = function(self, *args, **kwargs)

        notter_idx_path = self.notter.get_config(ncons.NOTES_INDEX_PATH)
        with open(notter_idx_path, "w") as idx_file:
            idx_file.write(json.dumps(self.idx))

        click.secho(f"Notter index updated", fg="green")
        return retval

    return wrapper
