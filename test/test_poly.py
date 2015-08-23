import unittest
from pygments.token import Token
from literate import Corpus
from literate.renderer.haskell import HaskellRenderer
from literate.renderer.poly import Tok

latex = r"""
Foobar
\begin{code} -- {lang=haskell}
    align       ::  Int -> Int
    align  x    =   f x
      where
        f  0    =   0
        f  x    =   2 * (foo x)
\end{code}
"""

class PolyTests(unittest.TestCase):
    def setUp(self):
        self.renderer = HaskellRenderer()
        self.corpus = Corpus(latex)
        self.region = self.corpus.code_regions[0]
        self.tok_stream = self.renderer.get_token_stream(self.region)

    def test_columns(self):
        expected = {4, 6, 8, 11, 16, 20}
        found = set()


        for tok in self.tok_stream:
            if tok.aligned:
                self.assertFalse(tok.is_whitespace())
                self.assertIn(tok.col, expected)
                found.add(tok.col)
        self.assertEqual(expected, found)

        def col_toks(n):
            return [[y.value for y in x] for x in self.tok_stream.get_column_contents(n)]

        self.assertEqual([['align'], ['align']], col_toks(4))
        self.assertEqual([['where']], col_toks(6))
        self.assertEqual([['f'], ['f']], col_toks(8))
        self.assertEqual([['x'], ['0'], ['x']], col_toks(11))
        self.assertEqual([['::'], ['='], ['='], ['=']], col_toks(16))
        self.assertEqual([['Int', '->', 'Int'], ['f', 'x'], ['0'], ['2', '*', '(', 'foo', 'x', ')']], col_toks(20))

    def test_replace(self):
        self.assertIn('\\to', self.corpus.render())

    def test_gobble(self):
        self.assertEqual(4, self.tok_stream.gobble_size)
