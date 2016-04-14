import argparse as _argparse
import enum as _enum
from os import environ as _environ


class ConfigFileType(_enum.Enum):
    CONFIG_PARSER = 0
    YAML = 1


# arg env config
class ConfigInterface:
    def __init__(self, *args, **kwargs):
        self._arg = _argparse.ArgumentParser(*args, **kwargs)
        self._config_path = {}
        self._keys = set()

        self.search_environment = True
        self.search_configuration = True
        self.search_arguments = True

    def add_argument(self, *args, **kwargs):
        # TODO: add internal tracking of kwargs
        self._arg.add_argument(*args, **kwargs)

    def get_kwargs(self, **kwargs):
        if self.search_configuration:
            # FIXME
            kwargs = self._get_settings()

        if self.search_environment:
            for k in kwargs.keys().update(self._keys)
                environ_value = _environ.get(k)
                if environ_value:
                    kwargs[k] = environ_value

        if self.search_arguments:
            parser_kwargs = vars(self._arg.parse_args())
            for k, v in parser_kwargs.items():
                if v:
                    kwargs[k] = v

        return kwargs

    def _get_settings(self):
        """
        helper method that returns a dict like obj
        """`
        if not self._config_path:
            return {}

        # FIXME

    def add_settings_file(self, path, type=ConfigFileType.CONFIG_PARSER)
        self._config_path[path] = type
