from collections import Mapping, defaultdict
import json
import os
from literate import utils


class Config(Mapping):
    """
    Dictionary-like object that forgives missing key accesses, even recursively.
    """

    @staticmethod
    def load(filename, **kwargs):
        return Config(utils.load_json(filename, **kwargs))

    def __init__(self, other=None, filename=None, **kwargs):
        def mkdict():
            return defaultdict(mkdict)
        self.config = defaultdict(mkdict)
        if filename:
            self._update(utils.load_json(filename, **kwargs))
        if other:
            self._update(other)

    def _update_dict(self, dst, src):
        for k, v in src.iteritems():
            if isinstance(v, Mapping) and isinstance(dst[k], Mapping):
                r = self._update_dict(dst[k], v)
                dst[k] = r
            else:
                dst[k] = v
        return dst

    def _update(self, other):
        if isinstance(other, Config):
            other = other.config
        self._update_dict(self.config, other)

    def copy(self):
        return Config(self)

    def __add__(self, other):
        cfg = Config(self)
        if other:
            cfg._update(other)
        return cfg

    def __len__(self):
        return self.config

    def __iter__(self):
        return iter(self.config)

    def __nonzero__(self):
        return len(self.config) > 0

    def __contains__(self, item):
        return item in self.config

    def __getitem__(self, key):
        val = self.config[str(key)]
        if hasattr(val, 'keys'):
            subconfig = Config(val)
            return subconfig
        return val

    def __getattr__(self, item):
        return self[item]

    def __repr__(self):
        return repr(self.config)