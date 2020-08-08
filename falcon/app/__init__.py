import os
import logging
from logging.handlers import RotatingFileHandler
from .__version__ import __version__  # noqa

__code_root = os.path.dirname(os.path.realpath(__file__))
root = os.path.abspath(os.path.join(__code_root, ".."))