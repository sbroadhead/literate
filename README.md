# literate

This is a Python package and command line utility for processing
LaTeX source code that may contain source code listings, and preprocessing
it into typesetting code for LaTeX. It was heavily inspired by
[lhs2tex] (http://www.andres-loeh.de/lhs2tex/). The included LaTeX
style file is mostly lifted directly from there.

I wrote this for my Masters thesis and it works exactly as well as I needed it to. The feature-set is limited, bugs are many, test coverage is small. This package is provided as-is.

Built-in support is included for Haskell and Scala code. Other languages will require a new `literate.renderer.Renderer` subclass, which generally will also require writing a `literate.renderer.Spacer` subclass along with coming up with an algorithm to determine token spacing.

By default code blocks are delimited like

  ```
  \begin{code}{lang=haskell}
  module MyCode where
  -- ...
  \end{code}
  ```

Use

    python setup.py install
     
to install it. This installs a `lit` command line utility.

    usage: lit [-h] [-o [OUTFILE]] [--config CONFIG] [--format FORMAT] [infile]

| Argument | Description |
| --- | --- |
| `-h` | Show the built-in help text. |
| `-o OUTFILE` | Write the result to file OUTFILE instead of stdout. |
| `--config CONFIG` | Load an additional JSON config file. |
| `--format LANG=FILENAME` | Load an additional format file (in JSON format`) for the specified language. |  

<img src="https://rawgit.com/sbroadhead/literate/master/example.png">
