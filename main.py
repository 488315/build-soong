# main.py

import os
import sys
import shutil
from pathlib import Path

from bp_parser import parser, dependency
from ninja_writer import writer
from ninja import NinjaRunner
from config import Config

sys.dont_write_bytecode = True  # Prevent writing .pyc files


def main():
    bp_file = "examples/Android.bp"
    out_dir = "out"
    base_dir = os.path.dirname(os.path.abspath(bp_file))

    modules = parser.parse_bp_file(bp_file)
    module_map = {m.name: m for m in modules}
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir, exist_ok=True)

    writer.resolve_filegroups(modules, module_map)

    graph = dependency.build_dependency_graph(modules)
    cycles = dependency.detect_cycles(graph)
    if cycles:
        print("❌ Dependency cycle(s) detected:")
        for cycle in cycles:
            print(" -> ".join(cycle))
        sys.exit(1)

    writer.write_ninja(modules, out_dir, base_dir)

    # print(f"✅ build.ninja generated at {out_dir}/build.ninja")
    # print("[+] Running ninja build with ninja.py...")

    config = Config(out_dir)
    ninja_runner = NinjaRunner(config, None)
    ninja_runner.run([])


if __name__ == "__main__":
    main()
