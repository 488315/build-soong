# bp_parser/globber.py
"""
Handles wildcard expansion (globs) for file lists in Android.bp modules.
Supports patterns like:
    - "*.c"
    - "src/**/*.cpp"
    - "include/**/*.h"
"""

import os
import glob
from typing import List


def resolve_globs(paths: List[str], base_path: str = ".") -> List[str]:
    """
    Expand glob patterns into full file paths.

    Args:
        paths: List of glob patterns or static paths
        base_path: Directory relative to which globs are evaluated

    Returns:
        List of resolved file paths
    """
    result = []
    for entry in paths:
        if isinstance(entry, str) and any(c in entry for c in ["*", "?", "[", "]"]):
            full_pattern = os.path.join(base_path, entry)
            result.extend(glob.glob(full_pattern, recursive=True))
        else:
            result.append(os.path.join(base_path, entry))
    return sorted(set(result))
