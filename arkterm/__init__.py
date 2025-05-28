"""
Enforces the minimum Python version requirement for the arkterm package.

This module checks if the running Python interpreter is version 3.10 or higher.
If the requirement is not met, it prints an error message and exits the program.
"""

import sys

if sys.version_info <= (3, 9):
    print("This package requires Python 3.10 or higher.", file=sys.stderr)
    sys.exit(1)

__version__ = "0.1.0-dev.1"
