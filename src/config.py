import os

from .errors import ConfigError


class Placeholder:
    """Placeholder for nested objects."""


class Config:

    def __init__(self, source, sep='|', strict=True):
        self._source = source

        # TODO: implement non-strict solution
        self._strict = strict
        self._sep = sep

        self._expand_variables(self, self._source)

    def _expand_variables(self, obj, source):
        for key, value in source.items():
            if isinstance(value, str) and value.startswith('$'):
                setattr(obj, key, self._retrieve_var(value))
            elif isinstance(value, dict):
                new_obj = Placeholder()
                setattr(obj, key, new_obj)
                self._expand_variables(new_obj, value)
            else:
                setattr(obj, key, value)

    def _retrieve_var(self, value):
        var, *optional = value.split(self._sep, maxsplit=1)
        env_var = var.lstrip('$')

        try:
            return os.environ[env_var]
        except KeyError:
            if optional:
                return self._retrieve_var(optional[0])

            exc = ConfigError('Environment variable {var} was not found'.format(var=env_var))

            if self._strict:
                raise exc
            else:
                return exc
