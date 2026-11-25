"""Critical path method over working days, for the schedule register (shared/registers/schedule.md).

Times are points on a working-day axis: an activity of duration d starting at point s ends at point s + d, so it
works the days s .. s + d - 1. A date maps to the point at the start of that day (a start) or at its end (a finish,
or a milestone). Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import bisect
import math
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import schedule_register as sr

ORIGIN = date(1990, 1, 1)
HORIZON = date(2200, 1, 1)
MAX_PATHS = 20
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DEFAULT_WORKING_DAYS = ("mon", "tue", "wed", "thu", "fri")


class WorkCalendar:
    """The working days of a project: days of the week, minus days off."""

    def __init__(self, working_days: tuple[str, ...], days_off: frozenset[date]) -> None:
        if not set(working_days) & set(WEEKDAYS):
            raise ValueError("a calendar needs at least one working day of the week")
        self.working_days = tuple(working_days)
        self.days_off = frozenset(days_off)
        self._days: list[date] = []
        self._next = ORIGIN

    def is_working(self, day: date) -> bool:
        return WEEKDAYS[day.weekday()] in self.working_days and day not in self.days_off

    def _extend(self, until: date) -> None:
        if until >= HORIZON or until < ORIGIN:
            raise ValueError(f"date {until} is outside the calendar ({ORIGIN} to {HORIZON})")
        while self._next <= until:
            if self.is_working(self._next):
                self._days.append(self._next)
            self._next += timedelta(days=1)

    def after(self, day: date) -> int:
        """The index of the first working day on or after the day."""
        ahead = timedelta(days=31)
        self._extend(day if day > date.max - ahead else day + ahead)
        return bisect.bisect_left(self._days, day)

    def before(self, day: date) -> int:
        """The index of the last working day on or before the day."""
        self._extend(day)
        return bisect.bisect_right(self._days, day) - 1

    def day(self, index: int) -> date:
        while index >= len(self._days):
            self._extend(self._next + timedelta(days=366))
        if index < 0:
            raise ValueError("date before the calendar origin")
        return self._days[index]

    def next_working(self, day: date) -> date:
        return self.day(self.after(day))

    def add(self, day: date, days: int) -> date:
        """The working day `days` working days after the day (the day itself when 0)."""
        return self.day(self.after(day) + days)

    def between(self, start: date, end: date) -> int:
        """Working days from one date to another: negative when the second is earlier."""
        return self.before(end) - self.before(start)


def calendar_from_capacity(register) -> WorkCalendar:
    """The working days and the holiday and closure days of a parsed capacity register."""
    import capacity_register as cr

    days_off: set[date] = set()
    for entry in register.calendar:
        if entry.kind not in cr.DAYS_OFF or entry.start is None:
            continue
        end = entry.end or entry.start
        days_off.update(entry.start + timedelta(days=i) for i in range((end - entry.start).days + 1))
    return WorkCalendar(register.working_days, frozenset(days_off))


@dataclass(frozen=True)
class Timing:
    id: str
    name: str
    duration: int
    progress: int
    es: int
    ef: int
    ls: int
    lf: int
    early_start: date
    early_finish: date
    late_start: Optional[date]
    late_finish: Optional[date]
    total_float: Optional[int]
    critical: bool
    deadline: Optional[date]

    @property
    def done(self) -> bool:
        return self.progress == 100


@dataclass(frozen=True)
class Schedule:
    start: date
    status: Optional[date]
    finish: date
    timings: tuple[Timing, ...]
    paths: tuple[tuple[str, ...], ...]
    truncated: bool
    missed: tuple[Timing, ...]

    def timing(self, activity: str) -> Timing:
        return next(t for t in self.timings if t.id == activity)


def topological(activities: tuple[sr.Activity, ...]) -> list[sr.Activity]:
    """Activities in dependency order, file order among equals; the network must have no cycle."""
    by_id = {a.id: a for a in activities}
    successors = sr.successors(activities)
    waiting = {a.id: len({l.pred for l in a.links if l.pred in by_id}) for a in activities}
    ready = [a.id for a in activities if waiting[a.id] == 0]
    order: list[sr.Activity] = []
    while ready:
        current = ready.pop(0)
        order.append(by_id[current])
        for s in successors[current]:
            waiting[s] -= 1
            if waiting[s] == 0:
                ready.append(s)
    if len(order) != len(activities):
        raise ValueError("the dependencies form a cycle")
    return order


class _Pass:
    """Forward and backward pass over one network."""

    def __init__(self, activities: tuple[sr.Activity, ...], cal: WorkCalendar, start: date,
                 status: Optional[date]) -> None:
        self.cal = cal
        self.order = topological(activities)
        self.successors = sr.successors(activities)
        self.p = cal.after(start)
        self.s = cal.before(status) + 1 if status else None
        self.es: dict[str, int] = {}
        self.ef: dict[str, int] = {}
        self.lf: dict[str, int] = {}
        self.tight: dict[str, set[str]] = {}
        self.by_id = {a.id: a for a in activities}

    def start_point(self, a: sr.Activity, day: date) -> int:
        return self.cal.before(day) + 1 if a.milestone else self.cal.after(day)

    def finish_point(self, day: date) -> int:
        return self.cal.before(day) + 1

    def _bound(self, link: sr.Link, a: sr.Activity) -> int:
        if link.kind == "SS":
            return self.es[link.pred] + link.lag
        if link.kind == "FF":
            return self.ef[link.pred] + link.lag - a.duration
        return self.ef[link.pred] + link.lag

    def _planned_start(self, a: sr.Activity, status: bool) -> int:
        es = max([self.p] + [self._bound(link, a) for link in a.links])
        if a.start and a.progress == 0:
            es = max(es, self.start_point(a, a.start))
        if status and self.s is not None:
            es = max(es, self.s)
        return es

    def forward(self) -> None:
        for a in self.order:
            if a.progress == 100:
                self._done(a)
            elif a.progress > 0:
                self._in_progress(a)
            else:
                self.es[a.id] = self._planned_start(a, True)
                self.ef[a.id] = self.es[a.id] + a.duration

    def _done(self, a: sr.Activity) -> None:
        es = self.start_point(a, a.start) if a.start else None
        ef = (self.start_point(a, a.finish) if a.milestone else self.finish_point(a.finish)) if a.finish else None
        if es is None and ef is None:
            es = self._planned_start(a, False)
        self.es[a.id] = es if es is not None else ef - a.duration
        self.ef[a.id] = ef if ef is not None else es + a.duration

    def _in_progress(self, a: sr.Activity) -> None:
        es = self.start_point(a, a.start) if a.start else self._planned_start(a, False)
        if self.s is not None:
            remaining = math.ceil(a.duration * (100 - a.progress) / 100)
            ef = max(es, self.s) + remaining
        else:
            ef = es + a.duration
        for link in a.links:
            if link.kind == "FF":
                ef = max(ef, self.ef[link.pred] + link.lag)
        self.es[a.id], self.ef[a.id] = es, ef

    def deadline(self, a: sr.Activity) -> Optional[int]:
        return self.finish_point(a.finish) if a.finish and a.progress < 100 else None

    def backward(self) -> None:
        end = max(self.ef.values())
        for a in reversed(self.order):
            if a.progress == 100:
                self.lf[a.id], self.tight[a.id] = self.ef[a.id], set()
                continue
            bounds = self._successor_bounds(a)
            lf = min([end] + list(bounds.values()))
            deadline = self.deadline(a)
            if deadline is not None:
                lf = min(lf, deadline)
            self.lf[a.id] = lf
            self.tight[a.id] = {s for s, bound in bounds.items() if bound == lf}

    def _successor_bounds(self, a: sr.Activity) -> dict[str, int]:
        bounds: dict[str, int] = {}
        span = self.ef[a.id] - self.es[a.id]
        for s in self.successors[a.id]:
            succ = self.by_id[s]
            for link in (l for l in succ.links if l.pred == a.id):
                if succ.progress == 100 or (succ.progress > 0 and link.kind != "FF"):
                    continue
                ls_s = self.lf[s] - (self.ef[s] - self.es[s])
                if link.kind == "SS":
                    bound = ls_s - link.lag + span
                elif link.kind == "FF":
                    bound = self.lf[s] - link.lag
                else:
                    bound = ls_s - link.lag
                bounds[s] = min(bound, bounds.get(s, bound))
        return bounds

    def start_date(self, a: sr.Activity, point: int) -> date:
        return self.cal.day(max(point - 1, self.p)) if a.milestone else self.cal.day(point)

    def finish_date(self, a: sr.Activity, point: int) -> date:
        return self.cal.day(max(point - 1, self.p)) if a.milestone else self.cal.day(point - 1)

    def timing(self, a: sr.Activity) -> Timing:
        es, ef, lf = self.es[a.id], self.ef[a.id], self.lf[a.id]
        ls = lf - (ef - es)
        done = a.progress == 100
        total_float = None if done else lf - ef
        return Timing(a.id, a.name, a.duration, a.progress, es, ef, ls, lf, self.start_date(a, es),
                      self.finish_date(a, ef), None if a.progress > 0 else self.start_date(a, ls),
                      None if done else self.finish_date(a, lf), total_float,
                      total_float is not None and total_float <= 0, a.finish if self.deadline(a) is not None else None)


def _paths(order: list[sr.Activity], file_order: tuple[sr.Activity, ...], timings: dict[str, Timing],
           tight: dict[str, set[str]], successors: dict[str, list[str]]) -> tuple[tuple[tuple[str, ...], ...], bool]:
    """Chains of critical activities through the dependencies that bind their late dates, at most MAX_PATHS."""
    critical = [a.id for a in order if timings[a.id].critical]
    links = {p: [s for s in successors[p] if s in tight[p] and timings[s].critical] for p in critical}
    targets = {s for p in critical for s in links[p]}
    position = {a.id: i for i, a in enumerate(file_order)}
    starts = sorted((c for c in critical if c not in targets), key=position.__getitem__)
    paths: list[tuple[str, ...]] = []
    stack = [(start,) for start in reversed(starts)]
    while stack and len(paths) <= MAX_PATHS:
        path = stack.pop()
        nexts = links[path[-1]]
        if not nexts:
            paths.append(path)
        stack.extend(path + (s,) for s in reversed(nexts))
    truncated = len(paths) > MAX_PATHS
    return tuple(paths[:MAX_PATHS]), truncated


def cpm(activities: tuple[sr.Activity, ...], cal: WorkCalendar, start: date,
        status: Optional[date] = None) -> Schedule:
    """Early and late dates, total float and critical paths of a valid, non-empty network."""
    run = _Pass(activities, cal, start, status)
    run.forward()
    run.backward()
    timings = {a.id: run.timing(a) for a in activities}
    paths, truncated = _paths(run.order, activities, timings, run.tight, run.successors)
    in_file_order = tuple(timings[a.id] for a in activities)
    finish = max(t.early_finish for t in in_file_order)
    missed = tuple(t for t in in_file_order
                   if t.deadline and not t.done and t.ef > run.finish_point(t.deadline))
    return Schedule(start, status, finish, in_file_order, paths, truncated, missed)


@dataclass(frozen=True)
class VarianceRow:
    id: str
    name: str
    baseline_start: date
    start: date
    start_variance: int
    baseline_finish: date
    finish: date
    finish_variance: int


@dataclass(frozen=True)
class Variance:
    baseline: sr.Baseline
    rows: tuple[VarianceRow, ...]
    added: tuple[str, ...]
    removed: tuple[str, ...]
    baseline_end: date
    end: date
    end_variance: int


def variance(schedule: Schedule, baseline: sr.Baseline, cal: WorkCalendar) -> Variance:
    """Start and finish variance in working days against a baseline: positive when later."""
    planned = {r.id: r for r in baseline.rows}
    rows = tuple(VarianceRow(t.id, t.name, planned[t.id].start, t.early_start,
                             cal.between(planned[t.id].start, t.early_start), planned[t.id].finish, t.early_finish,
                             cal.between(planned[t.id].finish, t.early_finish))
                 for t in schedule.timings if t.id in planned)
    current = {t.id for t in schedule.timings}
    baseline_end = max(r.finish for r in baseline.rows)
    return Variance(baseline, rows, tuple(t.id for t in schedule.timings if t.id not in planned),
                    tuple(r.id for r in baseline.rows if r.id not in current), baseline_end, schedule.finish,
                    cal.between(baseline_end, schedule.finish))


# --- report and command line --------------------------------------------------------------------------------------

def _ranges(days: frozenset[date]) -> str:
    ordered = sorted(days)
    parts: list[str] = []
    i = 0
    while i < len(ordered):
        j = i
        while j + 1 < len(ordered) and ordered[j + 1] - ordered[j] == timedelta(days=1):
            j += 1
        parts.append(str(ordered[i]) if i == j else f"{ordered[i]} to {ordered[j]}")
        i = j + 1
    return ", ".join(parts)


def _signed(value: int) -> str:
    return f"+{value}" if value > 0 else str(value)


def _row(t: Timing) -> str:
    late = (t.late_start or "-", t.late_finish, _signed(t.total_float)) if not t.done else ("-", "-", "done")
    mark = " (critical)" if t.critical else ""
    return (f"| {t.id} | {t.name} | {t.duration} | {t.progress}% | {t.early_start} | {t.early_finish} | "
            f"{late[0]} | {late[1]} | {late[2]}{mark} |")


def report(schedule: Schedule, cal: WorkCalendar, source: str, calendar_source: Optional[str],
           var: Optional[Variance]) -> str:
    timings = schedule.timings
    done = sum(t.done for t in timings)
    started = sum(0 < t.progress < 100 for t in timings)
    off = (f"days off from {calendar_source}: {_ranges(cal.days_off) or 'none'}" if calendar_source
           else "no days off (no capacity register given)")
    lines = [f"Activities from: {source}",
             f"Calendar: working days {', '.join(cal.working_days)}; {off}",
             f"Start: {schedule.start}"]
    if schedule.status:
        lines.append(f"Status date: {schedule.status} (progress as of the end of that day; work left starts "
                     f"from {cal.day(cal.before(schedule.status) + 1)})")
    else:
        lines.append("Status date: none (activities in progress keep their full duration)")
    lines += [f"Activities: {len(timings)} ({done} done, {started} in progress, {len(timings) - done - started} "
              "not started)", "",
              "Dates are working days; total float = late finish - early finish, in working days.",
              "| ID | Activity | Duration | Progress | Early start | Early finish | Late start | Late finish | "
              "Total float |", "|---|---|---|---|---|---|---|---|---|"]
    lines += [_row(t) for t in timings]
    lines += ["", f"Project finish: {schedule.finish}"]
    lines += _missed(schedule)
    lines += _critical(schedule)
    if var:
        lines += [""] + _variance_lines(var)
    return "\n".join(lines)


def _missed(schedule: Schedule) -> list[str]:
    if not schedule.missed:
        return ["Deadlines missed: none"]
    return ["Deadlines missed:"] + [f"- {t.id} {t.name}: early finish {t.early_finish} after the deadline "
                                    f"{t.deadline} (total float {_signed(t.total_float)})" for t in schedule.missed]


def _critical(schedule: Schedule) -> list[str]:
    if not schedule.paths:
        return ["Critical path: none (every activity is done)"]
    lines = [f"Critical path {i} (total float {_signed(min(schedule.timing(a).total_float for a in path))}): "
             f"{' → '.join(path)}" for i, path in enumerate(schedule.paths, start=1)]
    if schedule.truncated:
        lines.append(f"… more critical paths: only the first {MAX_PATHS} are listed")
    return lines


def _variance_lines(v: Variance) -> list[str]:
    b = v.baseline
    change = f", change {b.change}" if b.change else ""
    lines = [f"Baseline {b.id} {b.name} (approved {b.approved} by {b.approved_by}{change})",
             "Variance in working days: positive when later than the baseline.",
             "| ID | Activity | Baseline start | Start | Start variance | Baseline finish | Finish | "
             "Finish variance |", "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r.id} | {r.name} | {r.baseline_start} | {r.start} | {_signed(r.start_variance)} | "
              f"{r.baseline_finish} | {r.finish} | {_signed(r.finish_variance)} |" for r in v.rows]
    lines.append(f"Activities not in the baseline: {', '.join(v.added) or 'none'}")
    lines.append(f"Baseline activities no longer in the plan: {', '.join(v.removed) or 'none'}")
    lines.append(f"End date: baseline {v.baseline_end}, forecast {v.end}: {_signed(v.end_variance)} working days")
    return lines


class _Exit(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _Exit(2, f"cannot read {path}: {exc}")


def _invalid(what: str, errors: list[str]) -> _Exit:
    return _Exit(1, "\n".join([f"{what} is not valid:"] + errors))


def _activities(args: argparse.Namespace, register: sr.Register) -> tuple[tuple[sr.Activity, ...], str]:
    if args.activities:
        activities, errors = sr.parse_activities_csv(_read(args.activities))
        if errors:
            raise _invalid(str(args.activities), errors)
        source = f"{args.activities} (CSV)"
    elif register.has_activities:
        activities, source = register.activities, f"{args.file} (register)"
    else:
        raise _Exit(1, f"{args.file} has no Activities section (Source: {register.source}): export the plan "
                       "and pass it with --activities")
    if not activities:
        raise _Exit(1, "there are no activities to schedule")
    return activities, source


def _baseline(name: Optional[str], register: sr.Register) -> Optional[sr.Baseline]:
    if not name:
        return None
    if name == "latest":
        if not register.baselines:
            raise _Exit(2, "the register has no baseline")
        return register.baselines[-1]
    for b in register.baselines:
        if b.id == name:
            return b
    raise _Exit(2, f"no baseline {name}; the baselines are: {', '.join(b.id for b in register.baselines) or 'none'}")


def _calendar(path: Optional[Path]) -> WorkCalendar:
    if path is None:
        return WorkCalendar(DEFAULT_WORKING_DAYS, frozenset())
    import capacity_register as cr

    register, errors = cr.parse(_read(path))
    if errors:
        raise _invalid(str(path), errors)
    return calendar_from_capacity(register)


def _run(args: argparse.Namespace) -> str:
    register, errors = sr.parse(_read(args.file))
    if errors:
        raise _invalid(str(args.file), errors)
    activities, source = _activities(args, register)
    baseline = _baseline(args.baseline, register)
    cal = _calendar(args.capacity)
    dates = [a.start for a in activities if a.start]
    start = args.start or (min(dates) if dates else None)
    if start is None:
        raise _Exit(2, "no activity has a Start date: give the project start with --start")
    try:
        schedule = cpm(activities, cal, start, args.status_date)
        var = variance(schedule, baseline, cal) if baseline else None
    except ValueError as exc:
        raise _Exit(1, str(exc))
    return report(schedule, cal, source, str(args.capacity) if args.capacity else None, var)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="schedule_register.py cpm")
    parser.add_argument("file", type=Path)
    parser.add_argument("--activities", type=Path)
    parser.add_argument("--capacity", type=Path)
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--status-date", dest="status_date", type=date.fromisoformat)
    parser.add_argument("--baseline")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if args.baseline and args.baseline != "latest" and not sr.BASELINE_ID_RE.match(args.baseline):
        print(f"--baseline '{args.baseline}' must be B-NN or latest", file=sys.stderr)
        return 2
    for option, day in (("--start", args.start), ("--status-date", args.status_date)):
        if day is not None and not ORIGIN <= day < HORIZON:
            print(f"{option} {day} is outside the calendar ({ORIGIN} to {HORIZON})", file=sys.stderr)
            return 2
    try:
        print(_run(args))
    except _Exit as exc:
        print(exc, file=sys.stderr)
        return exc.code
    return 0
