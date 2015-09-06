from collections import Sequence

import pygments
from pygments.token import Token, string_to_tokentype
from literate import utils

from renderer import Renderer


class Sub(object):
    def __init__(self, id, *args):
        self.id = id
        self.args = args

    def __repr__(self):
        return "<Sub(id={}, args={})>".format(repr(self.id), repr(self.args))

    def __eq__(self, other):
        if not isinstance(other, Sub):
            return False
        return other.id == self.id and other.args == self.args


class Tok(object):
    def __init__(self, type, value, row, col, aligned=False):
        self.type = type
        self.value = value
        self.row = row
        self.col = col
        self.aligned = aligned

    def __repr__(self):
        return "<Tok(type={}, value={}, row={}, col={}, aligned={})>".format(
            repr(self.type), repr(self.value), repr(self.row), repr(self.col), repr(self.aligned))

    def is_whitespace(self):
        return self.type is Token.Text and self.value.isspace()

    def is_leading(self):
        return self.col == 0


class TokStream(Sequence):
    def __init__(self, iter):
        self.stream = list(iter)

    def _whitespace_prefix_length(self, row):
        if not row or not row[0].is_whitespace():
            return 0
        return len(row[0].value)

    def __len__(self):
        return len(self.stream)

    def __getitem__(self, index):
        return self.stream[index]

    @property
    def aligned_cols(self):
        """The set of column indices at which text is aligned."""
        return {t.col for t in self.stream if t.aligned}

    @property
    def num_rows(self):
        """The number of rows in this token stream."""
        return max(t.row for t in self.stream)

    @property
    def gobble_size(self):
        """The amount of whitespace by which every line is indented."""
        return min([self._whitespace_prefix_length(self.get_row_contents(i, True))
                    for i in xrange(self.num_rows)] or [0])

    def get_row_contents(self, row, include_whitespace=False):
        """Return a list containing every token in a given row."""
        return [tok for tok in self if tok.row == row and (include_whitespace or not tok.is_whitespace())]

    def get_column_contents(self, col, include_whitespace=False):
        """Return the contents of the given column, as a list of list of tokens."""
        out = []
        capture = False
        capture_row = 0
        current = []
        for tok in self:
            if tok.aligned and tok.col == col:
                capture_row = tok.row
                capture = True
            elif (tok.aligned and tok.col != col) or (capture and tok.row != capture_row):
                capture = False
                if current:
                    out.append(current)
                current = []

            if capture and (include_whitespace or not tok.is_whitespace()):
                current.append(tok)
        if current:
            out.append(current)
        return out


class PolyTableRenderer(Renderer):
    """
    Base renderer for polytable-based rendering. Must override create_lexer.
    """

    def __init__(self, config=None, format=None):
        super(PolyTableRenderer, self).__init__(config, format)

    def create_lexer(self):
        """Return a Pygment lexer to use for this renderer."""
        raise NotImplementedError()

    def column_spec(self, token_stream):
        """
        Get the column specification.
        """
        spec = {}

        def should_center_column(cells):
            has_op = False
            for cell in cells:
                if len(cell) > 1:
                    return False
                if cell[0].type in Token.Operator:
                    has_op = True
            return has_op

        for c in token_stream.aligned_cols:
            if should_center_column(token_stream.get_column_contents(c)):
                spec[c] = Sub('CenterColumn')
            else:
                spec[c] = Sub('LeftColumn')
        return spec

    def get_token_stream(self, code_region):
        """
        Turn a CodeRegion (essentially raw source code) into a stream of
        syntax tokens and position information.
        """
        def _generator():
            lexer = self.create_lexer()
            raw = pygments.lex(code_region.text, lexer)

            row, col = 0, 0
            begin_column = False
            for type, value in raw:
                tok = Tok(type, value, row, col, begin_column)
                if '\n' in value:
                    # Pygments doesn't necessarily split spaces and newlines into
                    # separate tokens, so we do it ourselves, ensuring there is always
                    # a token at column 0 of every row
                    spaces = value.split('\n')
                    begin_column = False
                    if spaces[0]:
                        yield Tok(type, spaces[0], row, col)
                        col += len(spaces[0])
                    for sp in spaces[1:]:
                        yield Tok(Token.Text, '\n', row, col)
                        row += 1
                        col = 0
                        if not sp:
                            continue
                        yield Tok(Token.Text, sp, row, col)
                        begin_column = True
                        col += len(sp)
                    continue
                if tok.is_whitespace():
                    if len(value) > 1:
                        begin_column = True
                else:
                    begin_column = False
                col += len(value)
                yield tok
        return TokStream(_generator())

    def transform(self, token_stream, gobble=None):
        """
        Transform the input token stream and intersperse instances of Sub
        throughout it, representing substitution tokens. The return value of
        this function will be fully rendered (including the begin and end
        code fences) except for substitution of the tokens.
        """
        out = []
        gobble = gobble if gobble is not None else token_stream.gobble_size
        col_specs = self.column_spec(token_stream)
        indent = 0

        out.append(Sub('Code'))
        out.append(Sub('Column', '0', Sub('LeftColumn')))
        for col in token_stream.aligned_cols:
            out.append(Sub('Column', col, col_specs[col]))
        out.append(Sub('Column', 'E', Sub('LeftColumn')))

        aligncol = 0
        buffer = []
        for tok in token_stream:
            if tok.col == 0 or tok.aligned:
                if buffer:
                    if tok.aligned:
                        out.append(Sub('FromTo', aligncol, tok.col, buffer))
                    else:
                        out.append(Sub('FromTo', aligncol, 'E', buffer))
                        out.append(Sub('LineBreak'))
                aligncol = tok.col
                buffer = []
            if tok.col == 0 and tok.is_whitespace():
                indent = len(tok.value) - gobble
                if indent:
                    buffer = [Sub('Indent', indent)]
                continue
            if not tok.is_whitespace():
                buffer.append(tok)
        if buffer:
            out.append(Sub('FromTo', aligncol, 'E', buffer))
        out.append(Sub('EndCode'))
        return out

    def pre_substitute_hook(self, buffer):
        """
        Allow derived classes to modify the substitution token buffer before
        it is modified. This lets us, for example, add spaces differently depending
        on the language.
        """
        return buffer

    def substitute(self, sub):
        """
        Transform a stack of substitution tokens into a string,
        recursively substituting sub-tokens.
        """
        def subarg(arg):
            if isinstance(arg, Sub):
                return ' '.join(self.substitute(arg))
            elif hasattr(arg, '__iter__'):
                return ' '.join([' '.join(self.substitute(s)) for s in arg])
            return str(arg)

        if isinstance(sub, Sub):
            if sub.id not in self.format.subst:
                return "??{}??".format(sub.id)
            args = [subarg(x) for x in sub.args]
            strout = self.format.subst[sub.id]
            for x in xrange(len(args)):
                strout = strout.replace('^' + str(x+1), args[x])
            return [strout]
        elif isinstance(sub, Tok):
            if sub.is_whitespace():
                return [' ']
            value = utils.latex_escape(sub.value)
            subbed = False
            if sub.value in self.format.format:
                opt = self.format.format[sub.value]
                if not opt['if'] or any(sub.type in string_to_tokentype(tt) for tt in opt['if']):
                    value = opt['to']
                    subbed = True
            tok_types = map(lambda x: str(x).replace('.', '')[5:], reversed(sub.type.split()))
            found = [y for y in tok_types if y in self.format.subst]
            if found and not subbed:
                result = ' '.join(self.substitute(Sub(found[0], value)))
                return [result]
            return [value]
        return [str(sub)]

    def render(self, code_region):
        token_stream = self.get_token_stream(code_region)
        if 'gobble' not in code_region.options:
            gobble = None
        else:
            gobble = int(code_region.options['gobble'])
        transformed = self.transform(token_stream, gobble)
        transformed = self.pre_substitute_hook(transformed)
        substituted = ' '.join(''.join(self.substitute(t)) for t in transformed)
        return str(substituted)
