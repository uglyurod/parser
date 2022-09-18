r"""Parse command line arguments

Command parameters:
    refresh         : bool  - Refresh data from remote server.
    max_workers     : int   - Number of workers for threading.
    options         : dict  - Options for GET request to hh api.

Example:
    options:
        {
            "text": "Python Developer",
            "area": 1,
            "per_page": 50
        }

Parser parameters:
    update           : bool  - Update JSON config if needed.

"""

import argparse
import json
from typing import Dict, Optional, Sequence


class Settings:
    r"""Researcher parameters

    Parameters
    ----------
    config_path : str
        Path to config file
    input_args : tuple
        Command line arguments for tests.
    no_parse : bool
        Disable parsing arguments from command line.

    Attributes
    ----------
    options : dict
        Options for GET request to API.
    refresh : bool
        Refresh data from remote server.
    save_result : bool
        Save DataFrame with parsed vacancies to CSV file
    max_workers : int
        Number of workers for threading.
    rates : dict
        Dict of currencies. For example: {"RUB": 1, "USD": 0.001}
    """

    def __init__(
        self, config_path: str, input_args: Optional[Sequence[str]] = None, no_parse: bool = False,
    ):
        self.options: Optional[Dict] = None
        self.rates: Optional[Dict] = None
        self.refresh: bool = False
        self.max_workers: int = 1
        self.save_result: bool = False
        self.update: bool = False

        # Get config from file
        with open(config_path, "r") as cfg:
            config: Dict = json.load(cfg)

        if not no_parse:
            params = self.__parse_args(input_args)

            for key, value in params.items():
                if value is not None:
                    if key in config:
                        config[key] = value
                    if "options" in config and key in config["options"]:
                        config["options"][key] = value

            self.update = params.get("update", False)
            if params["update"]:
                with open(config_path, "w") as cfg:
                    json.dump(config, cfg, indent=2)

        # Update attributes:
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        txt = "\n".join([f"{k :<16}: {v}" for k, v in self.__dict__.items()])
        return f"Settings:\n{txt}"

    def update_params(self, **kwargs):
        """Update object params"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

    @staticmethod
    def __parse_args(inputs_args) -> Dict:
        """Read arguments from command line.

        Returns
        -------
        arguments : dict
            Parsed arguments from command line. Note: some arguments are positional.

        """

        parser = argparse.ArgumentParser(description="HeadHunter vacancies researcher")
        parser.add_argument(
            "--text", action="store", type=str, default=None, help='Search query text (e.g. "Machine learning")',
        )
        parser.add_argument(
            "--max_workers", action="store", type=int, default=None, help="Number of workers for multithreading.",
        )
        parser.add_argument(
            "--refresh", help="Refresh cached data from HH API", action="store_true", default=None,
        )
        parser.add_argument(
            "--save_result", help="Save parsed result as DataFrame to CSV file.", action="store_true", default=None,
        )
        parser.add_argument(
            "--update", action="store_true", default=None, help="Save command line args to file in JSON format.",
        )

        params, unknown = parser.parse_known_args(inputs_args)
        # Update config from command line
        return vars(params)


if __name__ == "__main__":
    settings = Settings(
        config_path="../settings.json", input_args=("--max_workers", "5", "--refresh", "--text", "Data Scientist"),
    )

    print(settings)
