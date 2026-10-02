#!/usr/bin/env python3
"""Append one validated, idempotent release learning to this skill."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


LOG = Path(__file__).parents[1] / "references" / "observed-learnings.md"
MAX_FIELD_LENGTH = 600


def one_line(value: str, field: str) -> str:
    value = value.strip()
    if not value or "\n" in value or "\r" in value:
        raise ValueError(f"{field} must be one non-empty line")
    if len(value) > MAX_FIELD_LENGTH:
        raise ValueError(f"{field} must not exceed {MAX_FIELD_LENGTH} characters")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--status", required=True, choices=("succeeded", "failed-rolled-back"))
    parser.add_argument(
        "--category",
        required=True,
        choices=("deployment", "integration", "verification", "permissions"),
    )
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--learning", required=True)
    args = parser.parse_args()

    event_id = one_line(args.event_id, "event ID")
    evidence = one_line(args.evidence, "evidence")
    learning = one_line(args.learning, "learning")
    if not evidence.startswith("https://"):
        raise ValueError("evidence must be an HTTPS URL")

    marker = f"<!-- event:{event_id} -->"
    contents = LOG.read_text(encoding="utf-8")
    if marker in contents:
        print(f"Learning already recorded for {event_id}.")
        return 0

    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entry = (
        f"\n## {timestamp} — {args.category} ({args.status})\n"
        f"{marker}\n"
        f"- Evidence: {evidence}\n"
        f"- Learning: {learning}\n"
    )
    LOG.write_text(contents.rstrip() + entry, encoding="utf-8")
    print(f"Recorded learning for {event_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
