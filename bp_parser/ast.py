# bp_parser/ast.py

from typing import List, Dict, Union, Optional


class BpModule:
    def __init__(self, mtype: str, name: str, props: Dict):
        self.type = mtype
        self.name = name
        self.props = props
        self.deps: List[str] = []
