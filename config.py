# config.py

import os


class Config:
    def __init__(self, out_dir, ninja_args=None):
        self.out_dir = os.path.realpath(out_dir)
        self.ninja_args = ninja_args or self._parse_env_args()
        self.keep_going = int(os.getenv("NINJA_KEEP_GOING", "1"))
        self.parallel = int(os.getenv("NINJA_JOBS", os.cpu_count()))
        self.combined_ninja_file = os.path.join(self.out_dir, "build.ninja")
        self.ninja_command = os.getenv(
            "NINJA_BACKEND", "ninja"
        )  # "ninja", "n2", or "siso"
        self.dist_dir = os.path.join(self.out_dir, "dist")
        self.soong_out_dir = self.out_dir
        self.heartbeat_interval = int(os.getenv("NINJA_HEARTBEAT_INTERVAL", "300"))
        self.use_abfs = os.getenv("USE_ABFS", "0") == "1"

        # Binary paths
        self.ninja_bin = os.path.abspath("prebuilts/build-tools/linux-x86/bin/ninja")
        self.n2_bin = os.getenv("N2_BIN", "n2")
        self.siso_bin = os.getenv("SISO_BIN", "siso")

    def _parse_env_args(self):
        args = []
        if "NINJA_ARGS" in os.environ:
            args += os.environ["NINJA_ARGS"].split()
        if "NINJA_EXTRA_ARGS" in os.environ:
            args += os.environ["NINJA_EXTRA_ARGS"].split()
        return args

    def __repr__(self):
        return f"<Config out_dir={self.out_dir} ninja_args={self.ninja_args} parallel={self.parallel}>"
