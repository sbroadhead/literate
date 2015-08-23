from pygments.token import *

from literate.renderer import PolyTableRenderer
from literate.renderer.poly import Tok, Sub
from literate.renderer.spacer import Spacer


class HaskellSpacer(Spacer):
    def consume(self, token, state):
        DEFAULT = 0
        SPACE = 1
        AFTER = 2

        def iskw(tok):
            return tok.type in Token.Keyword or tok.type in Token.Name or tok.type in Token.Word

        if not isinstance(token, Tok):
            return [token], state
        if token.type in Token.Operator or token.value in ')]},;':
            return [token], DEFAULT
        if state == DEFAULT or state == SPACE:
            if token.value in ',;([{':
                return [token], DEFAULT
            if iskw(token):
                if state == DEFAULT:
                    return [token], AFTER
                elif state == SPACE:
                    return [Sub('Space'), token], AFTER
            return [token], SPACE
        elif state == AFTER:
            if token.value in ',;([{':
                return [Sub('Space'), token], DEFAULT
            if iskw(token):
                return [Sub('Space'), token], AFTER
            return [Sub('Space'), token], SPACE


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