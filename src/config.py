import os
from copy import deepcopy


from .errors import ConfigException


class DictConfig:

    def __init__(self, config):
        self._config = deepcopy(config)

        self._substitute_vars(self._config)

    def as_dict(self):
        return self._config

    def _substitute_vars(self, section):
        for key, value in section.items():
            if isinstance(value, dict):
                self._substitute_vars(value)
            elif isinstance(value, str) and value.startswith('$'):
                section[key] = os.environ[value.lstrip('$')]

    def _validate(self, vars):
        missing = vars.difference(set(os.environ.keys()))
        if missing:
            msg = '''Missing environment variables:
                \t{missing}.
                Full list of required variables:
                \t{all}
            '''.format(
                missing=',\n\t'.join(sorted(missing)),
                all=',\n\t'.join(sorted(vars))
            )
            raise ConfigException(msg)

    def __getattr__(self, item):
        try:
            return self._config[item]
        except KeyError:
            raise AttributeError(
                'Field `{}` can not be found in config'.format(item)
            )
