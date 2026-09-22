from pathlib import Path

from models import Result, Status, ValidationReport


def plan_project_structure(
    development_root: Path,
    project_name: str,
) -> ValidationReport:
    project_root = development_root / project_name

    planned_paths = (
        project_root,
        project_root / "src",
        project_root / "src" / project_name,
        project_root / "tests",
        project_root / "scripts",
        project_root / ".vscode",
    )

    results: list[Result] = []

    if project_root.exists():
        results.append(
            Result(
                Status.SKIP,
                f"Project directory already exists: {project_root}",
            )
        )
    else:
        results.append(
            Result(
                Status.CREATE,
                f"Project directory: {project_root}",
            )
        )

    for path in planned_paths[1:]:
        if path.exists():
            if path.is_dir():
                results.append(
                    Result(
                        Status.SKIP,
                        f"Directory already exists: {path}",
                    )
                )
            else:
                results.append(
                    Result(
                        Status.ERROR,
                        f"Expected directory but found file: {path}",
                    )
                )
        else:
            results.append(
                Result(
                    Status.CREATE,
                    f"Directory: {path}",
                )
            )

    return ValidationReport(results=tuple(results))


def create_project_structure(
    development_root: Path,
    project_name: str,
) -> ValidationReport:
    report = plan_project_structure(
        development_root=development_root,
        project_name=project_name,
    )

    if report.has_errors:
        return report

    project_root = development_root / project_name

    paths_to_create = (
        project_root,
        project_root / "src",
        project_root / "src" / project_name,
        project_root / "tests",
        project_root / "scripts",
        project_root / ".vscode",
    )

    for path in paths_to_create:
        path.mkdir(parents=True, exist_ok=True)

    return plan_project_structure(
        development_root=development_root,
        project_name=project_name,
    )