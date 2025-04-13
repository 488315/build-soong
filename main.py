import os
import sys
import subprocess

from bp_parser import parser, dependency
from ninja_writer import writer

def main():
    bp_file = "examples/Android.bp"
    out_dir = "out"
    base_dir = os.path.dirname(os.path.abspath(bp_file))
    out_dir = os.path.realpath(out_dir)

    modules = parser.parse_bp_file(bp_file)
    module_map = {m.name: m for m in modules}

    writer.resolve_filegroups(modules, module_map)

    graph = dependency.build_dependency_graph(modules)
    cycles = dependency.detect_cycles(graph)
    if cycles:
        print("Dependency cycle(s) detected:")
        for cycle in cycles:
            print(" -> ".join(cycle))
        sys.exit(1)

    writer.write_ninja(modules, out_dir, base_dir)
    print(f"✅ build.ninja generated in {out_dir}/")

    # Run ninja
    print("[+] Running ninja build...")
    try:
        subprocess.run(["/bin/bash", "-c", f"NINJA_STATUS='' ninja -C {out_dir}"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Ninja build failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()