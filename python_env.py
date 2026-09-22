from pathlib import Path
import subprocess

from models import Result, Status, ValidationReport


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
            results.append(
                Result(
                    Status.SKIP,
                    f"Virtual environment already exists: {venv_path}",
                )
            )
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