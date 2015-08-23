from importlib import import_module
import json
import os


def latex_escape(text):
    """Replace special LaTeX characters with their escaped counterparts."""
    escape_map = {
        r'#': r'\#', r'$': r'\$', r'%': r'\%', '^': r'\^{}', r'&': r'\&',
        r'_': r'\_', r'{': r'\{', r'}': r'\}', '~': r'\~{}', r'"': r'\char34 ',
        r"'": r'\char39 '
    }
    text = text.replace('\\', r'\textbackslash')
    for k, v in escape_map.iteritems():
        text = text.replace(k, v)
    return text


def get_class(name):
    """Get the class object from a fully-qualified class name."""
    modname, clsname = name.rsplit('.', 1)
    mod = import_module(modname)
    if not mod:
        raise ValueError('Lexer module "{}" not found'.format(modname))
    if not hasattr(mod, clsname):
        raise ValueError('Lexer module "{}" does not contain a lexer "{}"'.format(modname, clsname))
    return getattr(mod, clsname)


def load_json(filename, module=False):
    """
    Load a JSON file from a filename. If module is True, the file
    will be imported relative to the literate package root.
    """
    if module:
        filename = os.path.join(os.path.dirname(__file__), os.path.join('..', filename))
    with open(filename) as f:
        return json.load(f)
