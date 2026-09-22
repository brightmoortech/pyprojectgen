from pathlib import Path
import shutil
import subprocess
import sys

from config import CONFIG_PATH, validate_config
from models import Result, Status, ValidationReport


def _validate_project_name(project_name: str) -> list[Result]:
    if not project_name:
        return [
            Result(
                Status.ERROR,
                "Project name is required",
            )
        ]

    if not project_name.isidentifier():
        return [
            Result(
                Status.ERROR,
                (
                    "Project name must be a valid Python identifier "
                    "using letters, numbers, and underscores"
                ),
            )
        ]

    return [
        Result(
            Status.OK,
            f"Project name '{project_name}' is valid",
        )
    ]


def _validate_python() -> list[Result]:
    executable = Path(sys.executable)

    if not executable.exists():
        return [
            Result(
                Status.ERROR,
                "Current Python interpreter could not be located",
            )
        ]

    version = (
        f"{sys.version_info.major}."
        f"{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )

    return [
        Result(
            Status.OK,
            f"Python {version} available at {executable}",
        )
    ]


def _validate_git() -> list[Result]:
    git_path = shutil.which("git")

    if git_path is None:
        return [
            Result(
                Status.ERROR,
                "Git is not available on PATH",
            )
        ]

    try:
        completed = subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return [
            Result(
                Status.ERROR,
                "Git was found but could not be executed",
            )
        ]

    version = completed.stdout.strip()

    return [
        Result(
            Status.OK,
            f"{version} available at {git_path}",
        )
    ]


def run_preflight(project_name: str) -> ValidationReport:
    results: list[Result] = []

    if CONFIG_PATH.exists():
        results.append(
            Result(
                Status.OK,
                f"Configuration file found at {CONFIG_PATH}",
            )
        )
    else:
        results.append(
            Result(
                Status.ERROR,
                f"Configuration file not found at {CONFIG_PATH}",
            )
        )
        return ValidationReport(results=tuple(results))

    config_report = validate_config()
    results.extend(config_report.results)

    results.extend(_validate_project_name(project_name))
    results.extend(_validate_python())
    results.extend(_validate_git())

    return ValidationReport(results=tuple(results))