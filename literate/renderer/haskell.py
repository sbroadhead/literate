from pygments.token import *

from literate.renderer import PolyTableRenderer
from literate.renderer.poly import Tok, Sub
from literate.renderer.spacer import Spacer


class HaskellSpacer(Spacer):
    @classmethod
    def space_info(cls):
        text = r'(?:\w|\d)(?:\w|\d|[.])*'
        return [
            (text, [r'[\(\[\{\'\"]', text]),
            (r'[,)}\]]', [r'.*']),
            (r'".*"', [text])
        ]


class HaskellRenderer(PolyTableRenderer):
    def create_lexer(self):
        from pygments.filters import TokenMergeFilter
        from pygments.lexers.haskell import HaskellLexer
        l = HaskellLexer()
        l.add_filter(TokenMergeFilter())
        return l

    def pre_substitute_hook(self, buffer):
        # We use this to correct token spacing
        return HaskellSpacer.respace(buffer)