"""Run the full suite from an isolated source copy with a fresh, offline venv."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix="adaptiveguard-verify-") as temporary:
        root = Path(temporary)
        workspace = root / "checkout"
        workspace.mkdir()
        for directory in ("src", "tests"):
            shutil.copytree(ROOT / directory, workspace / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("nemotron_review.py", "research/phase2_validity_challenge.jsonl"):
            destination = workspace / name
            destination.parent.mkdir(exist_ok=True)
            shutil.copy2(ROOT / name, destination)

        environment = root / "venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = {name: value for name, value in os.environ.items()
               if not name.upper().startswith(("OPENROUTER_", "NEMOTRON_"))}
        subprocess.run([executable, "-E", "-s", "--version"], env=env, check=True, cwd=workspace)
        return subprocess.run(
            [executable, "-E", "-s", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=workspace, env=env, check=False,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
