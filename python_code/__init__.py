"""Campaign AI Python package loaded by Pythia as CAIPython."""

__version__ = "0.1.0"

from . import api  # Pythia resolves calls such as CAIPython.api.ping.

__all__ = ["api", "__version__"]

