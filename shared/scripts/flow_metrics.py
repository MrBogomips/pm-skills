#!/usr/bin/env python3
"""Flow metrics from a flow snapshot: cycle time, weekly throughput, WIP and work item age, team-level only.

The snapshot format and the rules are in shared/registers/flow-snapshot.md. Python 3 standard library only.

Usage:
    flow_metrics.py FILE --started S[,S...] --finished S[,S...] [--from D] [--to D] [--today D]
                    [--sle-days N] [--sle-percent P]
    flow_metrics.py compare OLD.csv NEW.csv --started ... --finished ... [--weeks N]
                    [--old-today D] [--new-today D] [--sle-days N] [--sle-percent P]
Exit 0 on success, 1 when a snapshot holds invalid data, 2 on a usage or I/O error.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Sequence

import flow_data as fd
import md_register as md

ALL = "all"
DEFAULT_SLE_PERCENT = 85


@dataclass(frozen=True)
class Sle:
    """Service Level Expectation: percent of items finish within days."""
    days: int
    percent: int


@dataclass(frozen=True)
class Finished:
    key: str
    type: str
    started: Optional[date]
    finished: date
    cycle_time: Optional[int]


@dataclass(frozen=True)
class InProgress:
    key: str
    type: str
    started: date
    age: int
    reopened: bool
    past_sle: bool


@dataclass(frozen=True)
class Group:
    label: str
    finished: tuple[Finished, ...]
    cycle_percentiles: dict[int, float] = field(hash=False)
    weeks: tuple[fd.Week, ...]
    throughput: tuple[int, ...]
    wip: tuple[InProgress, ...]
    wip_average: float
    within_sle: Optional[int]


def _finished(items: Sequence[fd.Item], wf: fd.Workflow, start: date, end: date) -> tuple[Finished, ...]:
    rows = [Finished(i.key, i.type, i.started_on(wf), f, i.cycle_time(wf))
            for i in items for f in [i.finished_on(wf)] if f and start <= f <= end]
    return tuple(sorted(rows, key=lambda r: (r.finished, r.key)))


def _wip(items: Sequence[fd.Item], wf: fd.Workflow, today: date, sle: Optional[Sle]) -> tuple[InProgress, ...]:
    rows = []
    for i in items:
        start, age = i.started_on(wf), i.age_on(wf, today)
        if i.in_progress_on(wf, today) and start and age:
            rows.append(InProgress(i.key, i.type, start, age, i.reopened_on(wf, today),
                                   bool(sle and age > sle.days)))
    return tuple(sorted(rows, key=lambda r: (-r.age, r.key)))


def _wip_average(items: Sequence[fd.Item], wf: fd.Workflow, start: date, end: date) -> float:
    days = [start + timedelta(days=n) for n in range((end - start).days + 1)]
    return sum(1 for d in days for i in items if i.in_progress_on(wf, d)) / len(days) if days else 0.0


def _group(label: str, items: Sequence[fd.Item], wf: fd.Workflow, start: date, end: date, today: date,
           sle: Optional[Sle]) -> Group:
    weeks = fd.weeks_ending(end, start)
    finished = _finished(items, wf, start, end)
    times = [f.cycle_time for f in finished if f.cycle_time is not None]
    percentiles = {p: fd.percentile(times, p) for p in fd.PERCENTILES} if times else {}
    within = sum(1 for t in times if t <= sle.days) if sle else None
    return Group(label, finished, percentiles, weeks, fd.throughput(items, wf, weeks),
                 _wip(items, wf, today, sle), _wip_average(items, wf, start, end), within)


def compute(items: Sequence[fd.Item], wf: fd.Workflow, start: date, end: date, today: date,
            sle: Optional[Sle]) -> tuple[Group, ...]:
    """Metrics for all items, then for each item type in alphabetical order."""
    types = sorted({i.type for i in items})
    groups = [_group(ALL, items, wf, start, end, today, sle)]
    groups += [_group(t, [i for i in items if i.type == t], wf, start, end, today, sle) for t in types]
    return tuple(groups)


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def _num(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".") if value != int(value) else str(int(value))


def _percentiles(group: Group) -> str:
    if not group.cycle_percentiles:
        return "no finished item with a start in the window"
    return ", ".join(f"p{p} {_num(v)}" for p, v in group.cycle_percentiles.items())


def _mean(values: Sequence[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def _finished_lines(group: Group) -> list[str]:
    no_start = sum(1 for f in group.finished if f.cycle_time is None)
    lines = [f"Finished in the window: {len(group.finished)}"
             + (f" ({no_start} without a started state, so without cycle time)" if no_start else "")]
    for f in group.finished:
        span = f"started {f.started}, " if f.started else "never in a started state, "
        cycle = f"cycle time {_days(f.cycle_time)}" if f.cycle_time is not None else "no cycle time"
        lines.append(f"  {f.key} {f.type}: {span}finished {f.finished}, {cycle}")
    return lines


def _throughput_lines(group: Group) -> list[str]:
    lines = ["Throughput per week (items finished, zero weeks included):"]
    lines += [f"  {w.start} to {w.end}: {n}" for w, n in zip(group.weeks, group.throughput)]
    if group.throughput:
        lines.append(f"  mean {_num(round(_mean(group.throughput), 2))} per week over {len(group.weeks)} weeks "
                     f"(min {min(group.throughput)}, max {max(group.throughput)})")
    return lines


def _wip_lines(group: Group, today: date) -> list[str]:
    lines = [f"WIP on {today}: {len(group.wip)} (average {_num(round(group.wip_average, 2))} per day "
             f"over the window)"]
    for w in group.wip:
        marks = [m for m, on in (("reopened", w.reopened), ("past the SLE", w.past_sle)) if on]
        suffix = f", {', '.join(marks)}" if marks else ""
        lines.append(f"  {w.key} {w.type}: started {w.started}, age {_days(w.age)}{suffix}")
    return lines


def _sle_lines(group: Group, sle: Optional[Sle]) -> list[str]:
    if sle is None or group.within_sle is None:
        return []
    timed = sum(1 for f in group.finished if f.cycle_time is not None)
    past = sum(1 for w in group.wip if w.past_sle)
    if not timed:
        return [f"SLE {sle.days} days at {sle.percent}%: no finished item to check; "
                f"{past} items in progress past the SLE"]
    share = 100 * group.within_sle / timed
    verdict = "met" if share >= sle.percent else "not met"
    return [f"SLE {sle.days} days at {sle.percent}%: {group.within_sle} of {timed} finished items "
            f"({share:.1f}%) within {sle.days} days: {verdict}; {past} items in progress past the SLE"]


def report(groups: Sequence[Group], wf: fd.Workflow, start: date, end: date, today: date,
           sle: Optional[Sle]) -> str:
    lines = [f"Started states (work in progress): {', '.join(sorted(wf.started))}",
             f"Finished states: {', '.join(sorted(wf.finished))}",
             f"Window: {start} to {end} ({len(groups[0].weeks)} whole weeks); WIP and age on {today}",
             "Cycle time: calendar days from the first started state to the first finished state after it, "
             "both days counted; a reopened item keeps its first finish and is in progress again, "
             "its age counted from its first start.",
             "Percentiles: nearest-rank (the value at rank ceil(p/100 x n) of the sorted values)."]
    for group in groups:
        lines += ["", f"== {group.label} ==", *_finished_lines(group),
                  f"Cycle time (days): {_percentiles(group)}", *_throughput_lines(group),
                  *_wip_lines(group, today), *_sle_lines(group, sle)]
    return "\n".join(lines)


def compare_rows(old: Optional[Group], new: Optional[Group]) -> list[tuple[str, str, str]]:
    """Metric name, old value, new value."""
    def cell(group: Optional[Group], fn) -> str:
        return fn(group) if group else "-"

    def pct(p: int):
        return lambda g: _num(g.cycle_percentiles[p]) if p in g.cycle_percentiles else "-"

    metrics = [("Finished", lambda g: str(len(g.finished)))]
    metrics += [(f"Cycle time p{p} (days)", pct(p)) for p in fd.PERCENTILES]
    metrics += [("Throughput mean per week", lambda g: _num(round(_mean(g.throughput), 2))),
                ("Weeks in the window", lambda g: str(len(g.weeks))),
                ("WIP now", lambda g: str(len(g.wip))),
                ("WIP average per day", lambda g: _num(round(g.wip_average, 2))),
                ("Oldest item in progress (days)", lambda g: str(g.wip[0].age) if g.wip else "-"),
                ("Items past the SLE", lambda g: str(sum(1 for w in g.wip if w.past_sle)))]
    return [(name, cell(old, fn), cell(new, fn)) for name, fn in metrics]


def compare_report(old: tuple[Group, ...], new: tuple[Group, ...], heads: tuple[str, str]) -> str:
    olds, news = {g.label: g for g in old}, {g.label: g for g in new}
    labels = [ALL] + sorted((set(olds) | set(news)) - {ALL})
    lines: list[str] = []
    for label in labels:
        lines += ["", f"== {label} ==", f"| Metric | {heads[0]} | {heads[1]} |", "|---|---|---|"]
        lines += [f"| {n} | {a} | {b} |" for n, a, b in compare_rows(olds.get(label), news.get(label))]
    return "\n".join(lines)


def _mapping_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--started", required=True, help="comma-separated states that mean work in progress")
    parser.add_argument("--finished", required=True, help="comma-separated states that mean finished")
    parser.add_argument("--sle-days", type=md.whole_number)
    parser.add_argument("--sle-percent", type=md.whole_number, default=DEFAULT_SLE_PERCENT)


def _parse(parser: argparse.ArgumentParser, argv: list[str]) -> Optional[argparse.Namespace]:
    try:
        return parser.parse_args(argv)
    except SystemExit:
        return None


def _common(args: argparse.Namespace) -> tuple[fd.Workflow, Optional[Sle]]:
    """ValueError on an invalid mapping or SLE."""
    wf = fd.Workflow.parse(args.started, args.finished)
    if args.sle_days is not None and (args.sle_days < 1 or not 1 <= args.sle_percent <= 100):
        raise ValueError("--sle-days must be at least 1 and --sle-percent from 1 to 100")
    return wf, Sle(args.sle_days, args.sle_percent) if args.sle_days is not None else None


def _window(items: tuple[fd.Item, ...], start: Optional[date], end: date) -> tuple[date, date]:
    """The window aligned to whole weeks ending on end. ValueError when shorter than a week."""
    earliest = start or min((t.entered_at.date() for i in items for t in i.transitions), default=end)
    weeks = fd.weeks_ending(end, earliest)
    if not weeks:
        raise ValueError(f"the window {earliest} to {end} is shorter than one week")
    return weeks[0].start, end


def _run(fn) -> int:
    try:
        return fn()
    except fd.DataError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    except OverflowError:
        print("a date of the window falls outside the supported range (years 1 to 9999)", file=sys.stderr)
        return 2


def _metrics_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="flow_metrics.py")
    parser.add_argument("file", type=Path)
    _mapping_args(parser)
    parser.add_argument("--from", dest="start", type=date.fromisoformat)
    parser.add_argument("--to", dest="end", type=date.fromisoformat)
    parser.add_argument("--today", type=date.fromisoformat)
    args = _parse(parser, argv)
    if args is None:
        return 2

    def go() -> int:
        wf, sle = _common(args)
        items = fd.load(args.file)
        today, source = fd.snapshot_today(args.file, items, args.today)
        start, end = _window(items, args.start, args.end or today)
        print(f"Snapshot: {args.file}; today {today} ({source})")
        if args.start and start != args.start:
            print(f"Window start moved from {args.start} to {start} to cover whole weeks ending on {end}")
        print(report(compute(items, wf, start, end, today, sle), wf, start, end, today, sle))
        return 0
    return _run(go)


def _side(path: Path, given: Optional[date], weeks: Optional[int], wf: fd.Workflow,
          sle: Optional[Sle]) -> tuple[tuple[Group, ...], str]:
    items = fd.load(path)
    today, source = fd.snapshot_today(path, items, given)
    start = today - timedelta(days=weeks * fd.WEEK_DAYS - 1) if weeks else None
    start, end = _window(items, start, today)
    print(f"{path}: today {today} ({source}), window {start} to {end}")
    return compute(items, wf, start, end, today, sle), f"{path.name} ({today})"


def _compare_cli(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="flow_metrics.py compare")
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    _mapping_args(parser)
    parser.add_argument("--weeks", type=md.whole_number, help="window of each snapshot: the last N weeks before its date")
    parser.add_argument("--old-today", type=date.fromisoformat)
    parser.add_argument("--new-today", type=date.fromisoformat)
    args = _parse(parser, argv)
    if args is None:
        return 2

    def go() -> int:
        wf, sle = _common(args)
        if args.weeks is not None and not 1 <= args.weeks <= fd.MAX_WEEKS:
            raise ValueError(f"--weeks must be from 1 to {fd.MAX_WEEKS}")
        old, old_head = _side(args.old, args.old_today, args.weeks, wf, sle)
        new, new_head = _side(args.new, args.new_today, args.weeks, wf, sle)
        print("Same rules as flow_metrics.py: cycle time first start to first finish, both days counted; "
              "percentiles nearest-rank.")
        print(compare_report(old, new, (old_head, new_head)))
        return 0
    return _run(go)


def main(argv: list[str]) -> int:
    if argv and argv[0] == "compare":
        return _compare_cli(argv[1:])
    return _metrics_cli(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
