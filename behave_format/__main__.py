"""Allow running as `python -m behave_format`."""

from __future__ import annotations

import sys

from behave_format.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
