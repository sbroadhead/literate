from collections import defaultdict


class Region(object):
    """
    Represents a region inside a Corpus.
    """
    def __init__(self, corpus, start, length):
        self._corpus = corpus
        self._start = start
        self._text = corpus._text[start:start + length]

    def __repr__(self):
        return "Region<start: {}, length: {}>".format(self.start, self.length)

    @property
    def length(self):
        return len(self.text)

    @property
    def text(self):
        return self._text

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value
        self._text = self._corpus._text[value:value + self.length]


class CodeRegion(Region):
    """
    Represents a code region inside a Corpus, including its options.
    """
    def __init__(self, corpus, start, length, opts):
        super(CodeRegion, self).__init__(corpus, start, length)
        self._options = defaultdict(str)
        self._options.update(opts)
        self._offset = 0

    def __repr__(self):
        return "CodeRegion<start: {}, length: {}, opts: {}>".format(
            self.start, self.length, self.options)

    @property
    def options(self):
        return self._options

    @property
    def text(self):
        return super(CodeRegion, self).text[self._offset:]