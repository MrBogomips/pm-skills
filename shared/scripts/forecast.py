#!/usr/bin/env python3
"""Monte Carlo delivery forecast from the weekly throughput of a flow snapshot.

The snapshot format and the rules are in shared/registers/flow-snapshot.md. Python 3 standard library only.

Usage:
    forecast.py when FILE --items N --started S[,S...] --finished S[,S...] [--type T] [--weeks-history 12]
                [--runs 10000] [--seed S] [--today D] [--start D]
    forecast.py how-many FILE --until D --started ... --finished ... [same options]
Exit 0 on success, 1 when the snapshot is invalid or has no throughput to sample, 2 on a usage or I/O error.
"""
from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Sequence

import flow_data as fd
import md_register as md

DEFAULT_WEEKS_HISTORY = 12
DEFAULT_RUNS = 10000
MAX_WEEKS = fd.MAX_WEEKS
SEED_RANGE = 1_000_000


class NoThroughput(ValueError):
    """The history has nothing to sample (exit 1)."""


@dataclass(frozen=True)
class History:
    weeks: tuple[fd.Week, ...]
    throughput: tuple[int, ...]
    trimmed: bool


def history(items: Sequence[fd.Item], wf: fd.Workflow, today: date, weeks: int,
            item_type: Optional[str]) -> History:
    """Weekly throughput of the last whole weeks ending on today, never before the first transition recorded."""
    chosen = [i for i in items if item_type in (None, i.type)]
    earliest = min((t.entered_at.date() for i in items for t in i.transitions), default=today)
    wanted = today - timedelta(days=weeks * fd.WEEK_DAYS - 1)
    found = fd.weeks_ending(today, max(wanted, earliest))
    return History(found, fd.throughput(chosen, wf, found), earliest > wanted)


def simulate_when(samples: Sequence[int], items: int, runs: int, rng: random.Random) -> tuple[int, ...]:
    """Weeks each run needs to finish items, drawing one week of throughput at a time with replacement."""
    if not any(samples):
        raise NoThroughput("no item finished in the history weeks: nothing to sample")
    results = []
    for _ in range(runs):
        done = weeks = 0
        while done < items:
            weeks += 1
            done += rng.choice(samples)
            if weeks > MAX_WEEKS:
                raise NoThroughput(f"a run needed more than {MAX_WEEKS} weeks: the history is too thin")
        results.append(weeks)
    return tuple(results)


def simulate_how_many(samples: Sequence[int], weeks: int, runs: int, rng: random.Random) -> tuple[int, ...]:
    """Items each run finishes in the given whole weeks."""
    if not samples:
        raise NoThroughput("no history weeks to sample")
    return tuple(sum(rng.choice(samples) for _ in range(weeks)) for _ in range(runs))


def when_percentiles(weeks: Sequence[int]) -> dict[int, int]:
    """p% of the runs finish within this many weeks."""
    return {p: int(fd.percentile(weeks, p)) for p in fd.PERCENTILES}


def how_many_percentiles(counts: Sequence[int]) -> dict[int, int]:
    """p% of the runs finish at least this many items: the (100 - p)th nearest-rank percentile."""
    return {p: int(fd.percentile(counts, 100 - p)) for p in fd.PERCENTILES}


def finish_date(start: date, weeks: int) -> date:
    return start + timedelta(days=weeks * fd.WEEK_DAYS - 1)


def _history_lines(h: History, item_type: Optional[str], asked: int) -> list[str]:
    lines = [f"History: {len(h.weeks)} whole weeks, {h.weeks[0].start} to {h.weeks[-1].end}, "
             f"item type: {item_type or 'all'}"]
    if h.trimmed:
        lines.append(f"  (asked for {asked} weeks; the snapshot starts later, so only the weeks it covers are used)")
    lines += [f"  {w.start} to {w.end}: {n}" for w, n in zip(h.weeks, h.throughput)]
    lines.append(f"Samples (items finished per week, zero weeks included): {', '.join(map(str, h.throughput))}")
    return lines


ASSUMPTIONS = ("Assumptions: the coming weeks look like the history weeks (same process, team and kind of work), "
               "weeks are independent, and the scope does not grow. Percentiles are nearest-rank over the runs.")


def _when(args: argparse.Namespace, h: History, start: date, rng: random.Random, seed_line: str) -> list[str]:
    weeks = simulate_when(h.throughput, args.items, args.runs, rng)
    lines = [f"Monte Carlo: {args.runs} runs, {seed_line}; each run draws one history week at random, with "
             f"replacement, until {args.items} items are finished",
             f"Start: {start}; a run that needs w weeks finishes on start + 7w - 1 days",
             f"Done by (share of runs finished on or before the date):"]
    lines += [f"  {p}%: {finish_date(start, w)} ({w} weeks)" for p, w in when_percentiles(weeks).items()]
    return lines


def _how_many(args: argparse.Namespace, h: History, start: date, rng: random.Random, seed_line: str) -> list[str]:
    days = (args.until - start).days + 1
    weeks = days // fd.WEEK_DAYS
    if weeks < 1:
        raise ValueError(f"from {start} to {args.until} there is not one whole week")
    if weeks > MAX_WEEKS:
        raise ValueError(f"from {start} to {args.until} there are {weeks} whole weeks: at most {MAX_WEEKS} can be "
                         "forecast")
    counts = simulate_how_many(h.throughput, weeks, args.runs, rng)
    lines = [f"Monte Carlo: {args.runs} runs, {seed_line}; each run adds {weeks} history weeks drawn at random, "
             f"with replacement",
             f"Period: {start} to {finish_date(start, weeks)}, {weeks} whole weeks"
             + (f" ({days - weeks * fd.WEEK_DAYS} days before {args.until} left out: not a whole week)"
                if days % fd.WEEK_DAYS else ""),
             "Items finished (p% of runs finish at least this many):"]
    lines += [f"  {p}%: at least {n}" for p, n in how_many_percentiles(counts).items()]
    return lines


def _parser(command: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=f"forecast.py {command}")
    parser.add_argument("file", type=Path)
    if command == "when":
        parser.add_argument("--items", type=md.whole_number, required=True)
    else:
        parser.add_argument("--until", type=date.fromisoformat, required=True)
    parser.add_argument("--started", required=True)
    parser.add_argument("--finished", required=True)
    parser.add_argument("--type", dest="item_type")
    parser.add_argument("--weeks-history", type=md.whole_number, default=DEFAULT_WEEKS_HISTORY)
    parser.add_argument("--runs", type=md.whole_number, default=DEFAULT_RUNS)
    parser.add_argument("--seed", type=md.whole_number)
    parser.add_argument("--today", type=date.fromisoformat)
    parser.add_argument("--start", type=date.fromisoformat)
    return parser


def _check(args: argparse.Namespace) -> None:
    if getattr(args, "items", 1) < 1 or args.runs < 1 or args.weeks_history < 1:
        raise ValueError("--items, --runs and --weeks-history must be at least 1")
    if args.weeks_history > MAX_WEEKS:
        raise ValueError(f"--weeks-history must be at most {MAX_WEEKS}")


def _go(command: str, args: argparse.Namespace) -> int:
    _check(args)
    wf = fd.Workflow.parse(args.started, args.finished)
    items = fd.load(args.file)
    today, source = fd.snapshot_today(args.file, items, args.today)
    h = history(items, wf, today, args.weeks_history, args.item_type)
    if not h.weeks:
        raise NoThroughput(f"the snapshot covers less than one whole week before {today}")
    start = args.start or today + timedelta(days=1)
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1, SEED_RANGE)
    seed_line = f"seed {seed}" + ("" if args.seed is not None else " (chosen at random; pass --seed to repeat)")
    run = _when if command == "when" else _how_many
    body = run(args, h, start, random.Random(seed), seed_line)
    print("\n".join([f"Snapshot: {args.file}; today {today} ({source})",
                     *_history_lines(h, args.item_type, args.weeks_history), *body, ASSUMPTIONS]))
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("when", "how-many"):
        print("usage: forecast.py when|how-many FILE ... (see --help of each)", file=sys.stderr)
        return 2
    try:
        args = _parser(argv[0]).parse_args(argv[1:])
    except SystemExit:
        return 2
    try:
        return _go(argv[0], args)
    except (fd.DataError, NoThroughput) as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    except OverflowError:
        print("a date of the forecast falls outside the supported range (years 1 to 9999): check --today, "
              "--start and --until", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
