# bp_parser/parser.py

import re
import ast
import copy
from bp_parser.ast import BpModule

VAR_RE = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)')
MOD_RE = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*{$')

def strip_comments(lines):
    in_block = False
    stripped = []
    for line in lines:
        line = line.strip()
        if '/*' in line:
            in_block = True
        if not in_block and not line.startswith('//'):
            stripped.append(line)
        if '*/' in line:
            in_block = False
    return stripped

def merge_arch_props(base: dict, arch: dict):
    for arch_key, props in arch.items():
        for k, v in props.items():
            if k in base:
                if isinstance(base[k], list) and isinstance(v, list):
                    base[k].extend(v)
                elif isinstance(base[k], dict) and isinstance(v, dict):
                    base[k].update(v)
                else:
                    base[k] = v  # override
            else:
                base[k] = v

def parse_bp_file(path):
    with open(path, 'r') as f:
        lines = strip_comments(f.readlines())

    variables = {}
    modules = []
    current = {}
    module_type = None

    for line in lines:
        if not line:
            continue

        var_match = VAR_RE.match(line)
        if var_match:
            key, val = var_match.groups()
            variables[key] = eval(val, {}, variables)
            continue

        mod_match = MOD_RE.match(line)
        if mod_match:
            module_type = mod_match.group(1)
            current = {}
            continue

        if line == "}":
            name = current.get("name", None)
            if module_type and name:
                # Merge arch-specific props
                if "arch" in current:
                    merge_arch_props(current, current.pop("arch"))

                module = BpModule(module_type, name, current)
                if module_type in ["cc_binary", "cc_library", "cc_shared_library", "cc_static_library"]:
                    for k in ("static_libs", "shared_libs"):
                        module.deps.extend(current.get(k, []))
                modules.append(module)

            current = {}
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.rstrip(",").strip()
            try:
                current[key] = eval(value, {}, variables)
            except Exception:
                current[key] = value

    return modules
