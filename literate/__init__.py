from .corpus import Corpus
from .region import Region, CodeRegion
from .config import Config
import utils
import renderer

default_config = Config(utils.load_json('literate.conf.json', True))
default_format = Config(utils.load_json('literate.fmt.json', True))