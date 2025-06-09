import os
import sys
sys.path.insert(0, os.path.abspath('../..'))


project = 'Projekt Python'
copyright = '2025, Dominik Zamęcki'
author = 'Dominik Zamęcki'
release = '1'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = []

language = 'pl'

html_theme = 'alabaster'
html_static_path = ['_static']
