import sphinx_rtd_theme

project = 'VaxPress'
copyright = '2023 Seoul National University'
author = 'Sohyeon Ju, Jayoung Ku, and Hyeshik Chang'
release = '0.4'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.duration',
    'sphinx_rtd_theme',
    'sphinx.ext.mathjax'
]
bibtex_bibfiles = ['refs.bib']
templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']
source_suffix = '.rst'
master_doc = 'index'
# mathjax_path = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = []

highlight_language = 'bash'

# -- Options for PDF output --------------------------------------------------
latex_engine = 'xelatex'
