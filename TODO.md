# TODO.md — Python-Based Soong-Compatible Build System (Bootstrap.bp)

## GOAL
Build a fully functional Soong-compatible build system in Python using `Bootstrap.bp` files, replacing `Android.bp`. This system must:
- Replace all GCC references with Clang (strictly Clang-only builds)
- Match Soong semantics: module types, visibility, namespaces, conditionals
- Output Ninja-compatible build graphs and support variant-aware builds

---

## ☑️ Phase 1: Minimal Working Build Graph

- [x] Parse `Bootstrap.bp` (JSON-like module format)
- [x] Parse top-level variables, `+=` append semantics
- [x] Support core module types:
  - [x] `cc_binary`
  - [x] `cc_library`
  - [x] `cc_static_library`
  - [x] `cc_shared_library`
  - [x] `filegroup`
  - [x] `prebuilt_etc`
- [x] Resolve `:module` syntax
- [x] Expand globs (`*.c`, `**/*.cpp`)
- [x] Resolve to actual filesystem paths
- [x] Write working `build.ninja` to `out/build.ninja`
- [x] Output to `out/obj/` and `out/`
- [x] Emit `cc`, `ar`, `shared`, `link` rules using Clang only
- [x] Disable Ninja "Entering directory" using `ninja -f`

---

## ⚙️ Phase 2: Core Module Graph Logic

- [x] Track dependencies between modules
- [x] Detect and report cycles in module graph
- [ ] Track reverse dependency edges for clean rebuild analysis
- [ ] Mark orphan modules not consumed by any target
- [ ] Emit DOT/JSON build graph (`module_graph.dot`, `graph.json`)
- [ ] Resolve `srcs: [":filegroup"]` properly with fallback handling
- [ ] Add Ninja rule dependency tag generation support

---

## 🧠 Phase 3: Soong Semantics

### ✅ Variables, Types, Maps

- [x] Support `bool`, `int`, `string`, `list`, `map` types
- [x] Support appending lists/maps with `+` operator
- [ ] Evaluate value substitution for `%s` logic in future config vars
- [ ] Add support for `.tag` expansions like `:module{.doc.zip}`

### ✅ Module System and Defaults

- [ ] Implement `cc_defaults`, `java_defaults`, etc.
- [ ] Merge properties from `defaults` list into consuming module
- [ ] Detect circular defaults references

### ✅ Conditionals

- [ ] Support `arch {}` blocks with merging (`arm`, `x86`, etc.)
- [ ] Add `target {}` evaluation blocks
- [ ] Support `soong_config_variables` resolution with defaults
- [ ] Add conditional fallback evaluation for unlisted keys

---

## 📦 Phase 4: Package Layout and Namespaces

- [ ] Implement `package { default_visibility: [...] }`
- [ ] Determine package path from `Bootstrap.bp` file location
- [ ] Implement `soong_namespace {}` support
- [ ] Parse `imports: []` to link namespaces together
- [ ] Resolve `//namespace:module` style references
- [ ] Validate uniqueness within and across namespaces

---

## 🔐 Phase 5: Visibility + Enforcement

- [ ] Enforce `visibility: ["//visibility:public"]`, `["//pkg:__pkg__"]`, etc.
- [ ] Support `:__subpackages__` expansion rules
- [ ] Validate that modules cannot access others without visibility
- [ ] Emit failure if access is attempted without proper scope

---

## ✨ Phase 6: Build Features

- [ ] Emit `.d` dependency files using `-MMD -MF`
- [ ] Support `cflags`, `ldflags`, `include_dirs`, `export_include_dirs`
- [ ] Track `runtime_libs`, `whole_static_libs`, `header_libs`
- [ ] Create install rules (copy or symlink into `out/install/`)
- [ ] Support optional `strip` of binaries

---

## ⚠️ Phase 7: Clang-Only Build Rules

- [x] Replace all `gcc`, `g++` with `clang`, `clang++`
- [x] Emit `rule cc` using `clang -c`
- [x] Emit `rule shared` using `clang -shared`
- [x] Emit `rule link` using `clang`
- [ ] Validate compiler flags are Clang-compatible only
- [ ] Emit errors on detection of `gcc`-only flags

---

## 🧪 Phase 8: Testing, Validation, Debugging

- [x] Add `BP2NINJA_DEBUG=1` env var for debug output
- [ ] Add `--debug` CLI flag using `argparse`
- [ ] Log to `out/build_debug.log`
- [ ] Emit resolved source paths per module
- [ ] Add unit tests for:
  - [ ] `.bp` parsing
  - [ ] dependency graph
  - [ ] filegroup resolution
  - [ ] visibility rules
- [ ] Compare `build.ninja` against AOSP for same module graph

---

## 🛠 Phase 9: Developer Tooling

- [ ] Rename repo to `build-soong`
- [x] Use `build/soong/` structure for imports
- [ ] Add `Makefile` or `tasks.py`:
  - [ ] `make ninja`
  - [ ] `make clean`
  - [ ] `make debug`
- [ ] Add `scripts/clean.fish` to wipe `out/`
- [ ] Add `.gitignore`, `.editorconfig`, and `pyproject.toml` for dev tools

---

## 🚀 Phase 10: Stretch Goals / Future

- [ ] Add support for `cc_test`, `java_library`, `genrule`
- [ ] Add `bp2bazel` mode to emit `BUILD.bazel` files
- [ ] Support recursive `Bootstrap.bp` scanning and caching
- [ ] Support hot reloading via `watchdog`
- [ ] Run on partial trees (e.g. `build only packages/apps/Settings`)
- [ ] Parse Android.mk and offer a conversion fallback

