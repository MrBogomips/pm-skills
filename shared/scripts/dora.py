#!/usr/bin/env python3
"""The four DORA metrics from a deployments CSV and an optional incidents CSV, team-level only.

The input formats are in shared/registers/flow-snapshot.md, section "DORA inputs". Python 3 standard library only.

Usage:
    dora.py --deployments FILE [--incidents FILE] --from YYYY-MM-DD --to YYYY-MM-DD
Exit 0 on success, 1 when an input holds invalid data, 2 on a usage or I/O error.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Optional, Sequence, TypeVar

import flow_data as fd

DEPLOYMENT_HEADER = ("deployed_at", "commit_at", "failed")
INCIDENT_HEADER = ("opened_at", "restored_at")
FAILED = {"yes": True, "no": False}
SECONDS_PER_HOUR = 3600
WEEK_DAYS = 7
T = TypeVar("T")


@dataclass(frozen=True)
class Deployment:
    deployed_at: datetime
    commit_at: Optional[datetime]
    failed: bool


@dataclass(frozen=True)
class Incident:
    opened_at: datetime
    restored_at: Optional[datetime]


@dataclass(frozen=True)
class Result:
    start: date
    end: date
    days: int
    deployments: int
    deployment_days: int
    failed: int
    lead_times: tuple[float, ...]
    incidents: Optional[int]
    restore_times: tuple[float, ...]
    unresolved: int


def _time(number: int, name: str, value: str, errors: list[str], required: bool = True) -> Optional[datetime]:
    if not value:
        if required:
            errors.append(f"line {number}: {name} is empty")
        return None
    parsed = fd.parse_timestamp(value)
    if parsed is None:
        errors.append(f"line {number}: {name} '{value}' is not an ISO 8601 date or date-time")
    return parsed


def _deployment(number: int, cells: list[str], errors: list[str]) -> Optional[Deployment]:
    deployed = _time(number, "deployed_at", cells[0], errors)
    commit = _time(number, "commit_at", cells[1], errors, required=False)
    failed = FAILED.get(cells[2].lower())
    if failed is None:
        errors.append(f"line {number}: failed '{cells[2]}' must be yes or no")
    if deployed and commit and commit > deployed:
        errors.append(f"line {number}: commit_at {commit} is after deployed_at {deployed}")
    return Deployment(deployed, commit, failed) if deployed and failed is not None else None


def _incident(number: int, cells: list[str], errors: list[str]) -> Optional[Incident]:
    opened = _time(number, "opened_at", cells[0], errors)
    restored = _time(number, "restored_at", cells[1], errors, required=False)
    if opened and restored and restored < opened:
        errors.append(f"line {number}: restored_at {restored} is before opened_at {opened}")
    return Incident(opened, restored) if opened else None


def _parse(text: str, header: tuple[str, ...],
           row: Callable[[int, list[str], list[str]], Optional[T]]) -> tuple[tuple[T, ...], list[str]]:
    errors: list[str] = []
    found = [r for number, cells in fd.read_csv(text, header, errors) for r in [row(number, cells, errors)] if r]
    return tuple(found), errors


def parse_deployments(text: str) -> tuple[tuple[Deployment, ...], list[str]]:
    return _parse(text, DEPLOYMENT_HEADER, _deployment)


def parse_incidents(text: str) -> tuple[tuple[Incident, ...], list[str]]:
    return _parse(text, INCIDENT_HEADER, _incident)


def _hours(later: datetime, earlier: datetime) -> float:
    return (later - earlier).total_seconds() / SECONDS_PER_HOUR


def compute(deployments: Sequence[Deployment], incidents: Optional[Sequence[Incident]], start: date,
            end: date) -> Result:
    """Deployments and incidents count when deployed or opened between start and end, both days included."""
    inside = [d for d in deployments if start <= d.deployed_at.date() <= end]
    leads = sorted(_hours(d.deployed_at, d.commit_at) for d in inside if d.commit_at)
    opened = [i for i in incidents or () if start <= i.opened_at.date() <= end]
    restores = sorted(_hours(i.restored_at, i.opened_at) for i in opened if i.restored_at)
    return Result(start, end, (end - start).days + 1, len(inside), len({d.deployed_at.date() for d in inside}),
                  sum(1 for d in inside if d.failed), tuple(leads),
                  len(opened) if incidents is not None else None, tuple(restores),
                  sum(1 for i in opened if not i.restored_at))


def _num(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _spread(values: Sequence[float]) -> str:
    return ", ".join(f"p{p} {_num(fd.percentile(values, p))}" for p in fd.PERCENTILES)


def _lead_line(r: Result) -> str:
    if not r.lead_times:
        return "Lead time for changes: not available (no deployment in the window has a commit time)"
    return (f"Lead time for changes (commit to deployment, hours, nearest-rank percentiles): "
            f"{len(r.lead_times)} of {r.deployments} deployments with a commit time: {_spread(r.lead_times)}")


def _restore_line(r: Result) -> str:
    if r.incidents is None:
        return "Time to restore service: not available (no incidents file)"
    open_note = f"; {r.unresolved} incident{'s' if r.unresolved != 1 else ''} not restored in the data"
    if not r.restore_times:
        return f"Time to restore service: {r.incidents} incidents opened, none restored{open_note}"
    return (f"Time to restore service (opened to restored, hours, nearest-rank percentiles): "
            f"{len(r.restore_times)} restored of {r.incidents} opened: {_spread(r.restore_times)}{open_note}")


def report(r: Result) -> str:
    per_week = r.deployments / r.days * WEEK_DAYS
    rate = (f"{r.failed} of {r.deployments} deployments failed = {100 * r.failed / r.deployments:.1f}%"
            if r.deployments else "not available (no deployment in the window)")
    return "\n".join([
        f"Window: {r.start} to {r.end} ({r.days} days)",
        f"Deployment frequency: {r.deployments} deployments, {per_week:.2f} per week "
        f"({r.deployments} / {r.days} days x 7), on {r.deployment_days} distinct days",
        _lead_line(r),
        f"Change failure rate: {rate}",
        _restore_line(r)])


def _read(path: Path, parse: Callable[[str], tuple[tuple[T, ...], list[str]]], what: str) -> tuple[T, ...]:
    found, errors = parse(path.read_text(encoding="utf-8"))
    if errors:
        raise fd.DataError("\n".join([f"{path} is not a valid {what} file:", *errors]))
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="dora.py")
    parser.add_argument("--deployments", type=Path, required=True)
    parser.add_argument("--incidents", type=Path)
    parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    parser.add_argument("--to", dest="end", type=date.fromisoformat, required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if args.end < args.start:
        print(f"--to {args.end} is before --from {args.start}", file=sys.stderr)
        return 2
    try:
        deployments = _read(args.deployments, parse_deployments, "deployments")
        incidents = _read(args.incidents, parse_incidents, "incidents") if args.incidents else None
    except fd.DataError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2
    print(report(compute(deployments, incidents, args.start, args.end)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
