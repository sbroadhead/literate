from literate import Config
import literate


class Renderer(object):
    """
    The base renderer class for rendering code regions.
    """
    def __init__(self, config=None, format=None):
        self.config = literate.default_config + config
        self.format = literate.default_format + format

    def render(self, code_region):
        raise NotImplementedError()
