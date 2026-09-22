import argparse

from config import init_config, validate_config
from models import Result, ValidationReport
from workflow import run_create_workflow


def print_result(result: Result) -> None:
    print(f"[{result.status.value}] {result.message}")


def print_report(report: ValidationReport) -> None:
    for result in report.results:
        print_result(result)

    print()

    if report.has_errors:
        print("[ERROR] Validation failed")
    elif report.has_warnings:
        print("[OK] Validation passed with warnings")
    else:
        print("[OK] Validation passed")


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyprojectgen")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "config-init",
        help="Create ~/.pyprojectgenrc if it does not already exist",
    )

    subparsers.add_parser(
        "config-validate",
        help="Validate ~/.pyprojectgenrc without modifying it",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new Python project",
    )

    create_parser.add_argument(
        "project_name",
        help="Name of the project to create",
    )

    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without modifying the system",
    )

    args = parser.parse_args()

    if args.command == "config-init":
        print_result(init_config())

    elif args.command == "config-validate":
        print_report(validate_config())

    elif args.command == "create":
        run_create_workflow(
            project_name=args.project_name,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()