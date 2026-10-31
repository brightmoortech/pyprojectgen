"""Select an exact project interpreter and create or validate its isolated venv."""

from pathlib import Path
import subprocess
import json
import re
import shutil
import sys

from models import Result, Status, ValidationReport


DEFAULT_PYTHON_VERSION = "3.12.10"


def select_python_version(project_root: Path, requested: str | None) -> str:
    """Keep a project's recorded pin on resume; defaults apply only to new pins."""
    recorded_path = project_root / ".python-version"
    recorded = recorded_path.read_text(encoding="utf-8").strip() if recorded_path.is_file() else None
    version = requested if requested is not None else (recorded or DEFAULT_PYTHON_VERSION)
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Python version must be exact, for example --python 3.12.10")
    if recorded is not None and recorded != version:
        raise ValueError(f"Requested Python {version} conflicts with recorded Python {recorded}; no changes made")
    return version


def find_python(version: str) -> Path:
    """Find an installed exact version without installing or substituting Python."""
    major_minor = version.rsplit(".", 1)[0]
    candidates = [str(sys.executable), f"python{major_minor}", "python3",
                  f"/Library/Frameworks/Python.framework/Versions/{major_minor}/bin/python3"]
    for candidate in candidates:
        path = shutil.which(candidate)
        if path is None:
            continue
        try:
            if get_python_version(Path(path)) == version:
                return Path(path)
        except (OSError, subprocess.CalledProcessError):
            continue
    raise ValueError(f"Python {version} is not installed or executable on PATH. Install that exact version and retry; no project resources created")


def get_python_version(python_executable: Path) -> str:
    completed = subprocess.run(
        [
            str(python_executable),
            "-c",
            "import platform; print(platform.python_version())",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return completed.stdout.strip()


def plan_python_environment(
    project_root: Path,
    python_executable: Path,
) -> ValidationReport:
    """Validate the recorded version and any existing isolated environment before writes."""
    results: list[Result] = []

    if not python_executable.exists():
        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Python interpreter does not exist: {python_executable}",
                ),
            )
        )

    version = get_python_version(python_executable)

    python_version_file = project_root / ".python-version"
    venv_path = project_root / ".venv"

    if python_version_file.exists():
        current_version = python_version_file.read_text(
            encoding="utf-8"
        ).strip()

        if current_version == version:
            results.append(
                Result(
                    Status.SKIP,
                    f".python-version already specifies Python {version}",
                )
            )
        else:
            results.append(
                Result(
                    Status.ERROR,
                    (
                        f".python-version specifies Python {current_version}, "
                        f"expected {version}"
                    ),
                )
            )
    else:
        results.append(
            Result(
                Status.CREATE,
                f".python-version with Python {version}",
            )
        )

    if venv_path.exists():
        if not venv_path.is_dir():
            results.append(
                Result(
                    Status.ERROR,
                    f"Expected virtual environment directory: {venv_path}",
                )
            )
        elif not (venv_path / "bin" / "python").exists():
            results.append(
                Result(
                    Status.ERROR,
                    f"Existing .venv is not a valid Python environment: {venv_path}",
                )
            )
        else:
            probe = subprocess.run(
                [str(venv_path / "bin" / "python"), "-I", "-c",
                 "import json,platform,sys; print(json.dumps([platform.python_version(),sys.prefix != sys.base_prefix]))"],
                check=True, capture_output=True, text=True,
            )
            actual_version, isolated = json.loads(probe.stdout)
            config = (venv_path / "pyvenv.cfg").read_text(encoding="utf-8").lower()
            valid = actual_version == version and isolated and "include-system-site-packages = false" in config
            results.append(Result(
                Status.SKIP if valid else Status.ERROR,
                f"Virtual environment matches Python {version} and isolation settings: {venv_path}"
                if valid else f"Existing .venv does not match Python {version} or isolation settings; review it manually: {venv_path}",
            ))
    else:
        results.append(
            Result(
                Status.CREATE,
                f"Virtual environment: {venv_path}",
            )
        )

    return ValidationReport(results=tuple(results))


def create_python_environment(
    project_root: Path,
    python_executable: Path,
) -> ValidationReport:
    """Create a missing environment and version pin; never replace an existing venv."""
    plan = plan_python_environment(
        project_root=project_root,
        python_executable=python_executable,
    )

    if plan.has_errors:
        return plan

    results: list[Result] = []
    version = get_python_version(python_executable)

    python_version_file = project_root / ".python-version"
    venv_path = project_root / ".venv"

    if python_version_file.exists():
        results.append(
            Result(
                Status.SKIP,
                f".python-version already specifies Python {version}",
            )
        )
    else:
        python_version_file.write_text(
            f"{version}\n",
            encoding="utf-8",
        )
        results.append(
            Result(
                Status.CREATE,
                f".python-version with Python {version}",
            )
        )

    if venv_path.exists():
        results.append(
            Result(
                Status.SKIP,
                f"Virtual environment already exists: {venv_path}",
            )
        )
    else:
        subprocess.run(
            [
                str(python_executable),
                "-m",
                "venv",
                str(venv_path),
            ],
            check=True,
        )

        results.append(
            Result(
                Status.CREATE,
                f"Virtual environment: {venv_path}",
            )
        )

    venv_python = venv_path / "bin" / "python"

    completed = subprocess.run(
        [
            str(venv_python),
            "-c",
            "import platform; print(platform.python_version())",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    venv_version = completed.stdout.strip()

    if venv_version != version:
        results.append(
            Result(
                Status.ERROR,
                (
                    f"Virtual environment uses Python {venv_version}, "
                    f"expected {version}"
                ),
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"Virtual environment uses Python {venv_version}",
            )
        )

    return ValidationReport(results=tuple(results))