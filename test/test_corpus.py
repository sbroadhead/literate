import unittest
import literate


class LiterateTests(unittest.TestCase):
    lipsum = ["""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur placerat neque vitae
        neque scelaerisque, id blandit tortor condimentum. Nullam ut pellentesque mi, eget suscipit elit.
        Nulla dictum risus non felis gravida cursus. Maecenas eu euismod libero. Donec ultrices efficitur
        purus quis vulputate.""",
        """Integer in efficitur dolor. Phasellus luctus erat at turpis rutrum,
        eu sagittis lacus aliquet. Quisque sodales dapibus quam aliquam vehicula. Lorem ipsum dolor sit
        amet, consectetur adipiscing elit.""",
        """Duis ut scelerisque sem. Mauris viverra enim sed semper
        pulvinar. Ut sit amet rhoncus tellus, et eleifend dui. Aliquam sodales tempor ante, vitae
        pretium odio gravida sed."""]

    def setUp(self):
        self.corpus = literate.Corpus(LiterateTests.lipsum[0] + r"""
                Hello
                \begin{code}{lang=haskell}
                foo      :: Int -> Int
                foo x    =
                  let y  = x + 5 in
                  y + y
                foo 0    = 0
                \end{code}
                """ + LiterateTests.lipsum[1] + r"""
                \begin{code}{lang=scala,numbers=yes}
                  object simpleExprCodeGraph extends ExpressionGraphBuilder {
                    type Input   = (INT, INT)
                    type Output  = (INT, BOOL)

                    import mutators._

                    val (x, y)        = input
                    val sum           = x + y
                    val prod          = x * y
                    val prodMinusSum  = prod - sum
                    val resultGt100   = prodMinusSum > 100

                    output(prodMinusSum, resultGt100)
                  }
                \end{code}

            """ + LiterateTests.lipsum[2])

    def test_find_blocks(self):
        self.assertNotIn('\\begin', self.corpus._text)
        self.assertEquals(2, len(self.corpus.code_regions))
        self.assertEquals('haskell', self.corpus.code_regions[0].options['lang'])
        self.assertEquals('scala', self.corpus.code_regions[1].options['lang'])
        self.assertEquals('yes', self.corpus.code_regions[1].options['numbers'])

    def test_render(self):
        hcode = self.corpus.code_regions[0].text
        scode = self.corpus.code_regions[1].text

        rendered = self.corpus.render()

        stripped = ''.join(c if c.isalpha() else ' ' for c in hcode + scode + ' '.join(LiterateTests.lipsum))

        for t in stripped.split():
            self.assertIn(t, rendered)