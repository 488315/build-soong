# bp_parser/__init__.py

from .parser import parse_bp_file
from .ast import BpModule
from .globber import resolve_globs
from . import dependency
