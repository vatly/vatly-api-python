"""Install the built wheel outside the source tree; check runtime and typing marker."""

import pathlib
import subprocess
import tempfile

wheel = next(pathlib.Path("dist").glob("*.whl")).resolve()
with tempfile.TemporaryDirectory() as tmp:
    env = pathlib.Path(tmp) / "venv"
    subprocess.run(["uv", "venv", str(env)], check=True)
    python = str(env / "bin/python")
    subprocess.run(["uv", "pip", "install", "--python", python, str(wheel)], check=True)
    subprocess.run(
        [
            python,
            "-c",
            "from importlib.resources import files; from vatly import VatlyClient, AsyncVatlyClient; assert files('vatly').joinpath('py.typed').is_file(); print('Wheel imports and py.typed OK')",
        ],
        cwd=tmp,
        check=True,
    )
