import os
from typing import List, Dict
from bp_parser.ast import BpModule
from bp_parser.globber import resolve_globs

def resolve_filegroups(modules: List[BpModule], module_map: Dict[str, BpModule]):
    filegroup_map = {
        m.name: m.props.get("srcs", [])
        for m in modules if m.type == "filegroup"
    }

    for m in modules:
        if "srcs" in m.props:
            resolved = []
            for s in m.props["srcs"]:
                if isinstance(s, str) and s.startswith(":"):
                    ref = s[1:]
                    resolved.extend(filegroup_map.get(ref, []))
                else:
                    resolved.append(s)
            m.props["srcs"] = resolved

def write_ninja(modules: List[BpModule], out_dir: str, base_path: str):
    out_dir = os.path.realpath(out_dir)
    base_path = os.path.realpath(base_path)
    os.makedirs(out_dir, exist_ok=True)
    ninja_path = os.path.join(out_dir, "build.ninja")

    module_map = {m.name: m for m in modules}
    built_libs = {}

    with open(ninja_path, "w") as f:
        f.write("rule cc\n  command = clang -c $in -o $out\n\n")
        f.write("rule ar\n  command = llvm-ar rcs $out $in\n\n")
        f.write("rule shared\n  command = clang -shared $in -o $out\n\n")
        f.write(f"rule link\n  command = clang $in $libs -o $out -L{out_dir}\n\n")

        for m in modules:
            mtype = m.type
            name = m.name
            props = m.props
            srcs = resolve_globs(props.get("srcs", []), base_path=base_path)
            objs = []

            if mtype.startswith("prebuilt_"):
                if "src" in props:
                    f.write(f"build {os.path.join(out_dir, name)}: phony {os.path.realpath(props['src'])}\n")
                continue

            for src in srcs:
                rel_src = os.path.relpath(src, base_path)
                obj = os.path.normpath(os.path.join(out_dir, f"obj/{name}/{os.path.splitext(rel_src)[0]}.o"))
                os.makedirs(os.path.dirname(obj), exist_ok=True)
                f.write(f"build {obj}: cc {os.path.realpath(src)}\n")
                objs.append(obj)

            if mtype == "cc_static_library":
                out_lib = os.path.join(out_dir, f"lib{name}.a")
                f.write(f"build {out_lib}: ar {' '.join(objs)}\n\n")
                built_libs[name] = out_lib

            elif mtype == "cc_shared_library":
                out_lib = os.path.join(out_dir, f"lib{name}.so")
                f.write(f"build {out_lib}: shared {' '.join(objs)}\n\n")
                built_libs[name] = out_lib

            elif mtype == "cc_library":
                out_a = os.path.join(out_dir, f"{name}.a")
                out_so = os.path.join(out_dir, f"{name}.so")
                f.write(f"build {out_a}: ar {' '.join(objs)}\n")
                f.write(f"build {out_so}: shared {' '.join(objs)}\n\n")
                built_libs[name] = out_a

        for m in modules:
            if m.type != "cc_binary":
                continue

            name = m.name
            props = m.props
            srcs = resolve_globs(props.get("srcs", []), base_path=base_path)
            objs = []

            for src in srcs:
                rel_src = os.path.relpath(src, base_path)
                obj = os.path.normpath(os.path.join(out_dir, f"obj/{name}/{os.path.splitext(rel_src)[0]}.o"))
                os.makedirs(os.path.dirname(obj), exist_ok=True)
                f.write(f"build {obj}: cc {os.path.realpath(src)}\n")
                objs.append(obj)

            deps = []
            libs = []

            for dep in props.get("static_libs", []) + props.get("shared_libs", []):
                dep_name = dep[1:] if dep.startswith(":") else dep
                if dep_name in built_libs:
                    deps.append(built_libs[dep_name])
                    libs.append(f"-l{dep_name}")
                elif dep_name in module_map and module_map[dep_name].type.startswith("prebuilt_"):
                    deps.append(os.path.join(out_dir, dep_name))
                    libs.append(os.path.join(out_dir, dep_name))

            bin_out = os.path.join(out_dir, name)
            f.write(f"build {bin_out}: link {' '.join(objs)} || {' '.join(deps)}\n")
            f.write(f"  libs = {' '.join(libs)}\n\n")

        binaries = [os.path.join(out_dir, m.name) for m in modules if m.type == "cc_binary"]
        if binaries:
            f.write(f"build all: phony {' '.join(binaries)}\n")
            f.write("default all\n")
