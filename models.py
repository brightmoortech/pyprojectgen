from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    OK = "OK"
    CREATE = "CREATE"
    SKIP = "SKIP"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class Result:
    status: Status
    message: str


@dataclass(frozen=True)
class ValidationReport:
    results: tuple[Result, ...]

    @property
    def has_errors(self) -> bool:
        return any(result.status is Status.ERROR for result in self.results)

    @property
    def has_warnings(self) -> bool:
        return any(result.status is Status.WARNING for result in self.results)