from click.testing import CliRunner
from notter.cli import cli

from importlib.metadata import version as pkg_version


class TestCLI:
    # def test_cli_version(self) -> None:
    #     runner = CliRunner(env={"SRC_PATH": "."})
    #     result = runner.invoke(cli, ["dummy  --version"])
    #     assert result.exit_code == 0
    #     assert result.output.strip("\n") == pkg_version("notter")
    pass
