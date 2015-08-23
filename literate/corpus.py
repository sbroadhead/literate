import os
import literate
import utils
from literate.config import Config
from literate.region import CodeRegion, Region


class Corpus(object):
    """
    A block of text with delimited code sections.
    """

    def __init__(self, text, config=None, formats=None):
        """
        Initialize a new Corpus with the specified text. If config is not
        specified, the default config is used.
        """
        self.config = literate.default_config + config
        self.formats = formats or {}
        self._original_text = text
        self._text = text
        self._code_regions = []
        self._find_code_regions()

    def _find_code_regions(self):
        code_start = self.config.delimiters.begin
        code_end = self.config.delimiters.end

        start = 0
        while True:
            start = self._text.find(code_start, start)
            if start == -1:
                return
            end = self._text.find(code_end, start + 1)
            if end == -1:
                raise ValueError("Mismatched code blocks found")

            # Parse out the code delimiters and the options block
            block_start = start + len(code_start)
            block_end = end
            end = end + len(code_end)
            inner_text = self._text[block_start:block_end]
            opts, inner_text = parse_options(inner_text)

            # Remove the actual code delimiters from the text
            self._text = (
                self._text[:start] +
                inner_text +
                self._text[end:])
            end = start + len(inner_text)

            region = CodeRegion(self, start, len(inner_text), opts)
            self._code_regions.append(region)
            start = region.start + region.length

    def _render_region(self, region):
        if region not in self.code_regions:
            raise RuntimeError("Region not scanned")
        lang = region.options.get('lang')
        renderer_name = self.config.renderers[lang]
        if not renderer_name:
            raise RuntimeError("No language specified for code block")
        renderer_cls = utils.get_class(renderer_name)
        if not renderer_cls:
            raise RuntimeError("Invalid renderer: {}".format(renderer_name or '(none)'))

        format = Config(utils.load_json(os.path.join('languages', lang + '.json'), True))
        extra_format = self.formats.get(lang)
        if extra_format:
            format += extra_format
        renderer = renderer_cls(self.config, format)
        text = renderer.render(region)
        self._text = (
            self._text[:region.start] +
            text +
            self._text[region.start + region.length:])
        self.code_regions.remove(region)
        new_region = Region(self, region.start, len(text))
        self._update_regions(new_region.start, new_region.length - region.length)

    def _update_regions(self, after, offset):
        for region in self.code_regions:
            if region.start > after:
                region.start += offset

    @property
    def original_text(self):
        return self._original_text

    @property
    def code_regions(self):
        return self._code_regions

    def render(self):
        rendered_corpus = Corpus(self._original_text, self.config, self.formats)
        for region in rendered_corpus.code_regions[:]:
            rendered_corpus._render_region(region)
        return rendered_corpus._text


def parse_options(text):
    """
    Attempt to parse a comma-delimited key-value pair surrounded by braces,
    and return the resulting dictionary. Failures result in {}.
    """
    nl = text.find('\n')
    brace = text.find('{')
    if brace == -1 or brace > nl:
        return {}, text[nl + 1:]

    text = text[brace:]
    end = text.find('}')
    result = {}
    if end != -1:
        # We actually want to skip the entire line that the code block is on
        nl = text.find('\n', end)
        opt_string = text[1:end]
        opts = opt_string.split(',')
        for opt in opts:
            if '=' not in opt:
                continue
            k, v = opt.split('=')
            result[k] = v
    return result, text[nl + 1:]