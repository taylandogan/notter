import click
import json
import notter.constants as ncons


def persist_after(function):
    def wrapper(self, *args, **kwargs):
        retval = function(self, *args, **kwargs)

        config_file = self.get_config(ncons.CONFIG_PATH)
        with open(config_file, "w+") as file:
            json.dump(self.config, file)

        click.secho(f"Notter config persisted", fg="green")
        return retval

    return wrapper
