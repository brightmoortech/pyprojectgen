"""Build staging from a verified remote commit without changing conflicting checkouts."""

from pathlib import Path
import subprocess

from models import Result, Status, ValidationReport


def _run_command(
    args: list[str],
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )


def _python_version(python_executable: Path) -> str | None:
    result = _run_command(
        [
            str(python_executable),
            "-c",
            "import platform; print(platform.python_version())",
        ]
    )

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def plan_stage(
    stage_root: Path,
    project_name: str,
    remote_url: str,
) -> ValidationReport:
    """Describe staging work without cloning or installing; execution verifies the revision."""
    results: list[Result] = []

    project_root = stage_root / project_name
    venv_path = project_root / ".venv"

    if not remote_url.strip():
        return ValidationReport(
            results=(
                Result(
                    Status.WARNING,
                    "Staging cannot be configured because the GitHub remote URL is empty",
                ),
            )
        )

    if project_root.exists():
        if not project_root.is_dir():
            return ValidationReport(
                results=(
                    Result(
                        Status.ERROR,
                        f"Expected staging directory but found another object: {project_root}",
                    ),
                )
            )

        git_dir = project_root / ".git"

        if not git_dir.is_dir():
            return ValidationReport(
                results=(
                    Result(
                        Status.ERROR,
                        f"Existing staging directory is not a Git repository: {project_root}",
                    ),
                )
            )

        results.append(
            Result(
                Status.SKIP,
                f"Staging repository already exists: {project_root}",
            )
        )
    else:
        results.append(
            Result(
                Status.CREATE,
                f"Clone staging repository: {remote_url} -> {project_root}",
            )
        )

    if venv_path.exists():
        if (venv_path / "bin" / "python").is_file():
            results.append(
                Result(
                    Status.SKIP,
                    f"Staging virtual environment already exists: {venv_path}",
                )
            )
        else:
            results.append(
                Result(
                    Status.ERROR,
                    f"Existing staging .venv is invalid: {venv_path}",
                )
            )
    else:
        results.append(
            Result(
                Status.CREATE,
                f"Create staging virtual environment: {venv_path}",
            )
        )

    results.append(
        Result(
            Status.CREATE,
            "Install or verify frozen staging dependencies",
        )
    )

    results.append(
        Result(
            Status.CREATE,
            "Install or verify project non-editably in staging",
        )
    )

    results.append(
        Result(
            Status.CREATE,
            "Run staging test suite",
        )
    )

    results.append(Result(Status.WARNING, "Execution will verify remote identity, clean checkout, and the published commit before installing"))
    return ValidationReport(results=tuple(results))


def validate_stage_checkout(project_root: Path, remote_url: str, expected_commit: str) -> ValidationReport:
    """Reject stale, dirty, or unrelated staging trees; never reset user work."""
    origin = _run_command(["git", "remote", "get-url", "origin"], cwd=project_root)
    head = _run_command(["git", "rev-parse", "HEAD"], cwd=project_root)
    status = _run_command(["git", "status", "--porcelain", "--untracked-files=all"], cwd=project_root)
    if origin.returncode or origin.stdout.strip() != remote_url:
        return ValidationReport((Result(Status.ERROR, "Existing staging origin differs from the intended remote; review the directory manually"),))
    if head.returncode or head.stdout.strip() != expected_commit:
        return ValidationReport((Result(Status.ERROR, f"Staging is not at intended GitHub commit {expected_commit}; no reset performed. Review/update the checkout manually and rerun"),))
    if status.returncode or status.stdout.strip():
        return ValidationReport((Result(Status.ERROR, "Staging has local or untracked changes, an interrupted checkout, or unreadable Git status. Nothing was reset. Inspect git status and follow README.md: Interrupted staging checkout recovery"),))
    return ValidationReport((Result(Status.OK, f"Staging origin and clean checkout match commit {expected_commit}"),))


def create_stage(
    stage_root: Path,
    project_name: str,
    remote_url: str,
    python_executable: Path,
    expected_commit: str | None = None,
) -> ValidationReport:
    """Reconstruct staging at the verified commit, then install and test independently."""
    results: list[Result] = []

    project_root = stage_root / project_name
    venv_path = project_root / ".venv"

    if not remote_url.strip():
        return ValidationReport(
            results=(
                Result(
                    Status.WARNING,
                    "Staging cannot be configured because the GitHub remote URL is empty",
                ),
            )
        )

    if not expected_commit:
        return ValidationReport((Result(Status.ERROR, "Staging requires a verified GitHub commit before any installation"),))

    selected_version = _python_version(python_executable)

    if selected_version is None:
        return ValidationReport(
            results=(
                Result(
                    Status.ERROR,
                    f"Could not execute Python interpreter: {python_executable}",
                ),
            )
        )

    if project_root.exists():
        if not project_root.is_dir():
            return ValidationReport(
                results=(
                    Result(
                        Status.ERROR,
                        f"Expected staging directory but found another object: {project_root}",
                    ),
                )
            )

        if not (project_root / ".git").is_dir():
            return ValidationReport(
                results=(
                    Result(
                        Status.ERROR,
                        f"Existing staging directory is not a Git repository: {project_root}",
                    ),
                )
            )

        results.append(
            Result(
                Status.SKIP,
                f"Staging repository already exists: {project_root}",
            )
        )
    else:
        stage_root.mkdir(parents=True, exist_ok=True)

        clone_result = _run_command(
            [
                "git",
                "clone",
                "--no-checkout",
                remote_url,
                str(project_root),
            ]
        )

        if clone_result.returncode != 0:
            message = clone_result.stderr.strip() or clone_result.stdout.strip()

            return ValidationReport(
                results=(
                    Result(
                        Status.ERROR,
                        f"Staging clone failed: {message}",
                    ),
                )
            )

        checkout = _run_command(["git", "checkout", "--detach", expected_commit], cwd=project_root)
        if checkout.returncode:
            return ValidationReport((Result(Status.ERROR, f"Cannot check out verified commit: {checkout.stderr.strip()}"),))
        results.append(
            Result(
                Status.CREATE,
                f"Staging repository cloned: {project_root}",
            )
        )

    checkout_report = validate_stage_checkout(project_root, remote_url, expected_commit)
    results.extend(checkout_report.results)
    if checkout_report.has_errors:
        return ValidationReport(tuple(results))

    version_file = project_root / ".python-version"

    if not version_file.is_file():
        results.append(
            Result(
                Status.ERROR,
                f"Staging project is missing .python-version: {version_file}",
            )
        )
        return ValidationReport(results=tuple(results))

    required_version = version_file.read_text(
        encoding="utf-8"
    ).strip()

    if required_version != selected_version:
        results.append(
            Result(
                Status.ERROR,
                (
                    f"Staging requires Python {required_version}, "
                    f"but selected interpreter is {selected_version}"
                ),
            )
        )
        return ValidationReport(results=tuple(results))

    if venv_path.exists():
        from python_env import plan_python_environment
        environment_report = plan_python_environment(project_root, python_executable)
        results.extend(environment_report.results)
        if environment_report.has_errors:
            return ValidationReport(tuple(results))
        venv_python = venv_path / "bin" / "python"

        if not venv_python.is_file():
            results.append(
                Result(
                    Status.ERROR,
                    f"Existing staging .venv is invalid: {venv_path}",
                )
            )
            return ValidationReport(results=tuple(results))

        staged_version = _python_version(venv_python)

        if staged_version != required_version:
            results.append(
                Result(
                    Status.ERROR,
                    (
                        f"Existing staging virtual environment uses Python "
                        f"{staged_version}, expected {required_version}"
                    ),
                )
            )
            return ValidationReport(results=tuple(results))

        results.append(
            Result(
                Status.SKIP,
                f"Staging virtual environment already exists: {venv_path}",
            )
        )
    else:
        venv_result = _run_command(
            [
                str(python_executable),
                "-m",
                "venv",
                str(venv_path),
            ]
        )

        if venv_result.returncode != 0:
            message = venv_result.stderr.strip() or venv_result.stdout.strip()

            results.append(
                Result(
                    Status.ERROR,
                    f"Could not create staging virtual environment: {message}",
                )
            )
            return ValidationReport(results=tuple(results))

        results.append(
            Result(
                Status.CREATE,
                f"Staging virtual environment created: {venv_path}",
            )
        )

    venv_python = venv_path / "bin" / "python"

    bootstrap_result = _run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            "requirements-bootstrap.txt",
        ],
        cwd=project_root,
    )

    if bootstrap_result.returncode != 0:
        message = bootstrap_result.stderr.strip() or bootstrap_result.stdout.strip()
        results.append(
            Result(
                Status.ERROR,
                f"Staging bootstrap dependency installation failed: {message}",
            )
        )
        return ValidationReport(results=tuple(results))

    requirements_result = _run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
        ],
        cwd=project_root,
    )

    if requirements_result.returncode != 0:
        message = (
            requirements_result.stderr.strip()
            or requirements_result.stdout.strip()
        )
        results.append(
            Result(
                Status.ERROR,
                f"Staging dependency installation failed: {message}",
            )
        )
        return ValidationReport(results=tuple(results))

    results.append(
        Result(
            Status.OK,
            "Frozen staging dependencies installed and verified",
        )
    )

    project_result = _run_command(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            ".",
            "--no-deps",
            "--no-build-isolation",
        ],
        cwd=project_root,
    )

    if project_result.returncode != 0:
        message = project_result.stderr.strip() or project_result.stdout.strip()
        results.append(
            Result(
                Status.ERROR,
                f"Staging project installation failed: {message}",
            )
        )
        return ValidationReport(results=tuple(results))

    results.append(
        Result(
            Status.OK,
            "Project installed non-editably in staging",
        )
    )

    dependency_check = _run_command([str(venv_python), "-m", "pip", "check"], cwd=project_root)
    if dependency_check.returncode:
        results.append(Result(Status.ERROR, f"Staging dependency validation failed: {dependency_check.stdout.strip()} {dependency_check.stderr.strip()}"))
        return ValidationReport(tuple(results))

    test_result = _run_command(
        [
            str(venv_python),
            "-m",
            "pytest",
        ],
        cwd=project_root,
    )

    if test_result.returncode != 0:
        message = test_result.stderr.strip() or test_result.stdout.strip()
        results.append(
            Result(
                Status.ERROR,
                f"Staging tests failed: {message}",
            )
        )
        return ValidationReport(results=tuple(results))

    results.append(
        Result(
            Status.OK,
            "Staging test suite passed",
        )
    )

    staged_version = _python_version(venv_python)

    if staged_version != required_version:
        results.append(
            Result(
                Status.ERROR,
                (
                    f"Staging virtual environment uses Python {staged_version}, "
                    f"expected {required_version}"
                ),
            )
        )
    else:
        results.append(
            Result(
                Status.OK,
                f"Staging virtual environment uses Python {staged_version}",
            )
        )

    return ValidationReport(results=tuple(results))