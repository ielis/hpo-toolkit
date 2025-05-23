import os
import sys

hpotk_src = os.path.abspath(os.path.join('..', 'src'))
sys.path.insert(0, hpotk_src)
# The import order is crucial to prevent having to install the library before generating documentation.
import hpotk


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'hpo-toolkit'
copyright = '2025, Daniel Danis'
author = 'Daniel Danis'
release = hpotk.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Autodoc setup ------------------------------------------------------------

autodoc_member_order = 'bysource'

# -- Doctest setup -------------------------------------------------------------

doctest_path = [hpotk_src]
doctest_test_doctest_blocks = ""

# Import `hpotk` followed by manual import of the most commonly used items.
doctest_global_setup = """
import hpotk
from hpotk import OntologyGraph, GraphAware
from hpotk import TermId, Term, MinimalTerm, Synonym, SynonymType, SynonymCategory
from hpotk import Ontology, MinimalOntology
"""

# -- Intersphinx setup --------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Sphinx copybutton setup --------------------------------------------------
# Exclude `>>>` when copying the cell
copybutton_exclude = '.linenos, .gp'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
pygments_style = 'sphinx'
html_theme = "sphinx_rtd_theme"

html_static_path = ['_static']
html_css_files = ['hpo-toolkit.css']
