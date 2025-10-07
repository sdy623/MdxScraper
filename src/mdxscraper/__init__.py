"""MdxScraper - MDX Dictionary Query and Extraction Library.

MdxScraper is a powerful library for querying MDX dictionaries and extracting
content to various formats (HTML, PDF, images). It can be used as both a
headless library and a GUI application.

Headless Library Usage:
    The core functionality can be used without any GUI dependencies:
    
    >>> from mdxscraper import Dictionary, mdx2html
    >>> 
    >>> # Query a dictionary
    >>> with Dictionary("dict.mdx") as dict:
    ...     result = dict.lookup_html("word")
    >>> 
    >>> # Convert words to HTML
    >>> found, not_found, invalid = mdx2html(
    ...     mdx_file="dict.mdx",
    ...     input_file="words.txt",
    ...     output_file="output.html"
    ... )

GUI Application:
    Run the GUI application:
    
    >>> from mdxscraper.gui import run_gui
    >>> run_gui()
    
    Or from command line:
    $ mdxscraper

For more information, see:
    - Core API: mdxscraper.core
    - MDX Query: mdxscraper.mdict
    - GUI: mdxscraper.gui
"""

# Core headless functionality (no GUI dependencies)
from mdxscraper.core import (
    Dictionary,
    WordParser,
    mdx2html,
    mdx2img,
    mdx2pdf,
)

__version__ = "5.2.13"

__all__ = [
    # Core headless API
    "Dictionary",
    "WordParser",
    "mdx2html",
    "mdx2pdf",
    "mdx2img",
    # Version
    "__version__",
]
