import re
from pygments.token import Token
from literate.renderer.poly import Tok, Sub


class Spacer(object):
    """
    State machine based on lhs2tex's spacer state machine idea that
    spaces out the tokens within columns (FromTo substitution tokens).
    """

    @classmethod
    def space_info(cls):
        return {}

    def consume(self, token, state):
        """
        Consume one token in the given state and return a list of tokens to
        emit along with a new state.
        """
        info = self.space_info()

        if not isinstance(token, Tok):
            return [token], state
        if not state:
            return [token], token

        for before, afters in info:
            if re.match(before, state.value):
                for after in afters:
                    if re.match(after, token.value):
                        return [Sub('Space'), token], token
        return [token], token


    @classmethod
    def respace(cls, buffer):
        """
        Return a new list of substitution tokens with the column (FromTo)
        tokens modified to have correct internal spacing.
        """
        spacer = cls()
        state = 0
        new_buffer = []
        for elem in buffer:
            if isinstance(elem, Sub) and elem.id == 'FromTo':
                col_from, col_to, content = elem.args
                new_content = []
                state = 0
                for tok in content:
                    (tokens, state) = spacer.consume(tok, state)
                    new_content += tokens
                new_buffer.append(Sub('FromTo', col_from, col_to, new_content))
            else:
                new_buffer.append(elem)
        return new_buffer