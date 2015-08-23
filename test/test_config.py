import unittest
import literate


class LiterateTests(unittest.TestCase):
    def test_config_get(self):
        config = literate.Config({'foo': 'bar', 'One': {'Two': {'Three': 5}}})
        self.assertEqual('bar', config.foo)
        self.assertFalse(config['baz'])
        self.assertEqual(5, config.One.Two.Three)
        self.assertFalse(config.One.Three.Five)

    def test_config_plus(self):
        config = literate.Config({'foo': 'bar'}) + literate.Config({'bar': 'baz'})
        self.assertEqual('bar', config['foo'])
        self.assertEqual('baz', config['bar'])
        config2 = config + literate.Config({'foo': 'quux'})
        self.assertEqual('quux', config2['foo'])
