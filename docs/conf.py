# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath(".."))

# Derive the navy PDF cover logo from the white HTML SVG at build time, so only the
# SVG is a committed source asset (needs cairosvg + Pillow, both in the docs requirements).
try:
    import io as _io
    import cairosvg
    from PIL import Image as _Image
except ImportError as _e:
    raise RuntimeError(
        "Docs build requires cairosvg and Pillow to generate the PDF cover logo; "
        "install them (pip install cairosvg pillow)."
    ) from _e
_static = os.path.join(os.path.dirname(__file__), "_static")
with open(os.path.join(_static, "cryptnox-logo.svg"), encoding="utf-8") as _f:
    _svg = _f.read()
_png = cairosvg.svg2png(
    bytestring=_svg.replace('fill="white"', 'fill="#101f2e"').encode(),
    output_width=1200, output_height=226,
)
_Image.open(_io.BytesIO(_png)).save(
    os.path.join(_static, "cryptnox-logo-dark.png"), dpi=(400, 400)
)

project = 'cryptnox-sdk-py'
copyright = '2026, Cryptnox SA'
author = 'Cryptnox'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_sitemap",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
]

# Disable autosummary generation to prevent hangs
autosummary_generate = False

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Mock external dependencies to prevent import errors during doc build
autodoc_mock_imports = [
    'pyscard',
    'smartcard',
    'smartcard.System',
    'smartcard.CardConnection',
    'smartcard.Exceptions',
    'smartcard.CardType',
    'smartcard.CardRequest',
    'smartcard.util',
    'smartcard.scard',
    'cryptography',
    'cffi',
    'aiohttp',
    'aiosignal',
    'attrs',
]

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Handle ambiguous cross-references
nitpicky = False
nitpick_ignore = [
    ('py:class', 'Base'),
    ('py:class', 'ConnectionException'),
    ('py:class', 'CardException'),
]

# Suppress specific warnings
suppress_warnings = [
    'ref.python',
    'toc.not_included',
]

# -- Graphviz configuration --------------------------------------------------
# Configuration for automatic class diagram generation

# Graphviz output format (svg provides high quality, scalable diagrams)
graphviz_output_format = 'svg'

# Global Graphviz options - gray color style
graphviz_dot_args = [
    '-Gbgcolor=transparent',
    '-Nshape=box',
    '-Nstyle=rounded,filled',
    '-Nfillcolor=lightgray',
    '-Ncolor=black',
    '-Nfontcolor=black',
    '-Nfontname=Arial',
    '-Nfontsize=10',
    '-Ecolor=black',
    '-Efontsize=9',
]

# Inheritance diagram configuration - gray color style
inheritance_graph_attrs = {
    'rankdir': 'TB',  # Top to Bottom layout
    'size': '"8.0, 12.0"',
    'bgcolor': 'transparent',
}

inheritance_node_attrs = {
    'shape': 'box',
    'style': '"rounded,filled"',
    'fillcolor': 'lightgray',
    'color': 'black',
    'fontcolor': 'black',
    'fontname': 'Arial',
    'fontsize': '10',
}

inheritance_edge_attrs = {
    'arrowsize': '0.8',
    'color': 'black',
}

# -- SEO meta tags -----------------------------------------------------------

html_baseurl = 'https://docs.cryptnox.com/cryptnox-sdk-py/'

# sphinx-sitemap writes sitemap.xml next to the pages, with html_baseurl as the prefix.
# The docs hub (cryptnox.github.io) lists it in docs.cryptnox.com/robots.txt.
sitemap_url_scheme = "{link}"
sitemap_excludes = ["search.html", "genindex.html", "py-modindex.html"]

html_meta = {
    'description': (
        'Cryptnox SDK for Python — Python library for communicating'
        ' with Cryptnox smartcards. Card management, key derivation,'
        ' signing, secure channel, and authentication.'
    ),
    'keywords': (
        'Cryptnox, SDK, Python, smartcard, JavaCard, APDU,'
        ' secure channel, BIP32, ECDSA, key derivation,'
        ' cryptocurrency, NFC, pyscard, pip'
    ),
    'author': 'Cryptnox',
    'robots': 'index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large',
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

# Logo configuration
html_logo = "_static/cryptnox-logo.svg"
html_favicon = "_static/favicon.png"

# Custom CSS and JS
html_css_files = [
    'custom.css',
]

html_js_files = [
    'custom.js',
]

# Theme options
html_theme_options = {
    'analytics_id': 'GT-PJ7HDFB',
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#101f2e',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Sitemap / SEO
html_show_sourcelink = False
html_copy_source = False
html_show_sphinx = False

# -- Options for PDF (LaTeX) output ------------------------------------------
# Built by CI with pdflatex, same as Yubico's tech manual. Output: cryptnox-sdk-py.pdf

today = 'June 20, 2026'  # fixed doc date on the cover
autodoc_preserve_defaults = True  # show source default exprs, not expanded values

latex_engine = 'pdflatex'
latex_logo = '_static/cryptnox-logo-dark.png'  # white logo is invisible on white PDF title page
latex_domain_indices = False  # no Python Module Index in the PDF (kept in HTML)
latex_documents = [
    ('index', 'cryptnox-sdk-py.tex', 'Cryptnox SDK for Python Manual', author, 'manual'),
]
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'figure_align': 'H',
    'sphinxsetup': 'pre_border-radius=0pt',  # sharp rectangle corners on code-block (command-line) frames
    'extraclassoptions': 'oneside,openany',  # no blank filler pages (web PDF)
    'printindex': '',  # drop the general Index from the PDF (kept in HTML)
    'fncychap': '',  # no fancy chapter rules; titlesec styles chapters instead
    'preamble': r'''
% pdflatex can't render colour emoji; drop the ones used in the docs
\DeclareUnicodeCharacter{1F4B3}{}% credit card
\DeclareUnicodeCharacter{1F4CA}{}% bar chart
\DeclareUnicodeCharacter{1F4DA}{}% books
\DeclareUnicodeCharacter{1F4C4}{}% page facing up
% Left-align body text (ragged right instead of justified)
\usepackage[document]{ragged2e}
% Drop the "(continues on next page)" / "(continued from previous page)" labels (parens included) on code blocks
\AtBeginDocument{\renewcommand*\sphinxstylecodecontinued[1]{}\renewcommand*\sphinxstylecodecontinues[1]{}}
% Whole document in the sans font (TeX Gyre Heros)
\renewcommand{\familydefault}{\sfdefault}
% Sans-serif TOC entries
\AtBeginDocument{\addtocontents{toc}{\protect\sffamily}}
% Left-align figures/diagrams too (neutralize their built-in \centering)
\usepackage{etoolbox}
\AtBeginEnvironment{figure}{\let\centering\raggedright}
% Cap figure height below the text height so tall diagrams leave room for their
% caption instead of pushing it onto the page footer
\makeatletter
\AtBeginDocument{\spx@image@maxheight=0.85\textheight}
\makeatother
% Flatten autodoc indentation: object descriptions + Parameters/Returns lists align left
\makeatletter
\renewenvironment{fulllineitems}{%
  \begin{list}{}{\labelwidth\z@ \leftmargin\z@ \rightmargin\z@
                 \topsep-\parskip \partopsep\parskip \itemsep-\parsep
                 \let\makelabel=\py@itemnewline}%
}{\end{list}}
\makeatother
\setlength{\leftmargini}{1.2em}
\setlength{\leftmarginii}{1.2em}
\setlength{\leftmarginiii}{1.2em}
% Left-aligned chapter headings
\usepackage{titlesec}
\titleformat{\chapter}[hang]{\sffamily\bfseries\huge}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{0pt}{20pt}
\usepackage{fancyhdr}
\def\headruleskip{4pt}\def\footruleskip{4pt}% gap between header/footer text and rule
\makeatletter
% Centered page header (doc title) + copyright footer
\AtBeginDocument{%
  \fancypagestyle{normal}{%
    \fancyhf{}%
    \fancyhead[C]{\sffamily\nouppercase{\@title}}%
    \fancyfoot[L]{\sffamily\copyright{} 2026 Cryptnox SA}%
    \fancyfoot[R]{\sffamily\thepage}%
    \renewcommand{\headrulewidth}{0.4pt}%
    \renewcommand{\footrulewidth}{0.4pt}%
  }%
  \fancypagestyle{plain}{%
    \fancyhf{}%
    \fancyfoot[L]{\sffamily\copyright{} 2026 Cryptnox SA}%
    \fancyfoot[R]{\sffamily\thepage}%
    \renewcommand{\headrulewidth}{0pt}%
    \renewcommand{\footrulewidth}{0.4pt}%
  }%
  \pagestyle{normal}%
}
% Centered title page (default is right-aligned); author line removed (logo brands it)
\renewcommand{\sphinxmaketitle}{%
  \let\sphinxrestorepageanchorsetting\relax
  \ifHy@pageanchor\def\sphinxrestorepageanchorsetting{\Hy@pageanchortrue}\fi
  \hypersetup{pageanchor=false}%
  \begin{titlepage}%
    \let\footnotesize\small \let\footnoterule\relax
    \begingroup
      \def\endgraf{ }\def\and{\& }%
      \pdfstringdefDisableCommands{\def\\{, }}%
      \hypersetup{pdfauthor={\@author}, pdftitle={\@title}}%
    \endgroup
    \noindent\rule{\textwidth}{1pt}\par
    \begin{flushright}%
      \vskip 1em%
      \includegraphics[width=7cm]{cryptnox-logo-dark}\par
      \vskip 2em%
      {\LARGE\py@HeaderFamily \@title \par}%
      \vskip 0.5em%
      {\large\itshape \py@release\releaseinfo \par}%
      \vfill
      {\large \@date \par}%
    \end{flushright}%
    \@thanks
  \end{titlepage}%
  \setcounter{footnote}{0}%
  \let\thanks\relax\let\maketitle\relax
  \clearpage
  \ifdefined\sphinxbackoftitlepage\sphinxbackoftitlepage\fi
  \if@openright\cleardoublepage\else\clearpage\fi
  \sphinxrestorepageanchorsetting
}
\makeatother
''',
}
