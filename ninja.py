# ninja.py

import os
import subprocess
import threading
import time
from pathlib import Path


OUT_DIR = os.path.realpath(os.getenv("OUT_DIR", "out"))
NINJA_ENV_FILE_NAME = f"{OUT_DIR}/.environment"
NINJA_LOG_FILE_NAME = f"{OUT_DIR}/.ninja_log"
NINJA_WEIGHT_LIST_FILE_NAME = f"{OUT_DIR}/.ninja_weight_list"
NINJA_FIFO_NAME = f"{OUT_DIR}/.ninja_fifo"
DEFAULT_NINJA_PATH = "prebuilts/build-tools/linux-x86/bin/ninja"


class NinjaRunner:
    def __init__(self, config, ctx):
        self.config = config
        self.ctx = ctx
        self.env = self._build_env()
        self.ninja_path = Path(DEFAULT_NINJA_PATH).resolve()
        self.fifo_path = Path(config.out_dir) / NINJA_FIFO_NAME
        self.log_path = Path(config.out_dir) / NINJA_LOG_FILE_NAME
        self.stuck_event = threading.Event()
        self.out_dir = OUT_DIR

    def _build_env(self):
        allowed = {
            "HOME",
            "LANG",
            "LC_MESSAGES",
            "PATH",
            "PWD",
            "TMPDIR",
            "USER",
            "SHELL",
            "ASAN_SYMBOLIZER_PATH",
            "ASAN_OPTIONS",
            "RUST_BACKTRACE",
            "RUST_LOG",
            "PYTHONDONTWRITEBYTECODE",
        }
        env = {k: os.environ[k] for k in allowed if k in os.environ}
        env["SHELL"] = "/bin/bash"
        env["DIST_DIR"] = self.config.dist_dir
        return env

    def _write_env_file(self):
        env_file = Path(self.config.out_dir) / NINJA_ENV_FILE_NAME
        with open(env_file, "w") as f:
            for k, v in self.env.items():
                f.write(f"{k}={v}\n")

    def _run_stuck_checker(self, interval_sec=300):
        """Monitor Ninja build progress based on log file modification time."""

        def check():
            prev_mtime = None
            while not self.stuck_event.wait(interval_sec):
                try:
                    if self.log_path.exists():
                        mtime = self.log_path.stat().st_mtime
                        if prev_mtime is not None and mtime == prev_mtime:
                            timestamp = time.strftime(
                                "%Y-%m-%d %H:%M:%S", time.localtime()
                            )
                            print(
                                f"[WARN] [{timestamp}] Ninja build may be stuck (log unchanged)."
                            )
                            subprocess.run(["pstree", "-palT", str(os.getpid())])
                        prev_mtime = mtime
                    else:
                        print(
                            f"[DEBUG] Ninja log file '{self.log_path}' does not exist yet."
                        )
                except Exception as e:
                    print(f"[ERROR] Exception in stuck checker: {e}")

        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        return thread

    def run(self, ninja_args):
        self._write_env_file()

        args = [
            str(self.ninja_path),
            "-d",
            "keepdepfile",
            "-d",
            "keeprsp",
            "-w",
            "dupbuild=err",
            "-w",
            "missingdepfile=err",
            "-j",
            str(self.config.parallel),
            "-f",
            self.config.combined_ninja_file,
        ] + ninja_args

        if self.config.keep_going != 1:
            args += ["-k", str(self.config.keep_going)]

        thread = self._run_stuck_checker(self.config.heartbeat_interval)
        try:
            print(f"[+] Running: {' '.join(args)}")
            subprocess.run(args, env=self.env, check=True)
        finally:
            self.stuck_event.set()
            thread.join(timeout=5)
            if thread.is_alive():
                print("[WARN] Stuck checker thread did not terminate in time.")

    def get_inputs(self, goal):
        args = [
            str(self.ninja_path),
            "-f",
            self.config.combined_ninja_file,
            "-t",
            "inputs",
            goal,
        ]
        if not self.config.use_abfs:
            args.insert(-1, "-d")
        try:
            output = subprocess.check_output(args, text=True)
            return output.strip().splitlines()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get inputs for {goal}: {e}")
            return []
