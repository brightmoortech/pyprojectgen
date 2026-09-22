
import argparse

from config import init_config, validate_config
from models import Result, ValidationReport


def print_result(result: Result) -> None:
    print(f"[{result.status.value}] {result.message}")


def print_report(report: ValidationReport) -> None:
    for result in report.results:
        print_result(result)

    print()

    if report.has_errors:
        print("[ERROR] Configuration validation failed")
    elif report.has_warnings:
        print("[OK] Configuration valid with warnings")
    else:
        print("[OK] Configuration valid")


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

    args = parser.parse_args()

    if args.command == "config-init":
        print_result(init_config())

    elif args.command == "config-validate":
        print_report(validate_config())


if __name__ == "__main__":
    main()