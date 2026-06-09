#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyobjc-framework-Quartz"]
# ///
"""Detect whether the user has stepped away from a macOS machine.

Combines several independent signals so that no single false reading
(e.g. watching a video with no input) flips the verdict on its own:

  - screen lock state        (deliberate "I'm leaving")
  - screensaver activity     (idle long enough that the saver kicked in)
  - input idle time          (seconds since last mouse / keyboard event)
  - active Focus mode         (reported as context; only counts as "away"
                               for the modes you opt in via --away-focus)

This script carries inline PEP 723 metadata, so run it with uv — which reads
that metadata and provisions an ephemeral environment with the one dependency
(PyObjC's Quartz, needed for reliable lock + idle detection):

  uv run scripts/presence.py                        # JSON verdict
  uv run scripts/presence.py --idle 180             # >=180s idle counts as away (default 120)
  uv run scripts/presence.py --away-focus Sleep,Personal   # these Focus modes mean "away"
  ./scripts/presence.py                             # if chmod +x'd (uses the uv shebang)

Exit code: 0 if present, 1 if away. Handy for launchd / shell guards.
"""

import argparse
import json
import os
import subprocess
import sys

from Quartz import (
    CGEventSourceSecondsSinceLastEventType,
    CGSessionCopyCurrentDictionary,
    kCGAnyInputEventType,
    kCGEventSourceStateHIDSystemState,
)


def idle_seconds() -> float:
    """Seconds since the last keyboard / mouse event."""
    return float(
        CGEventSourceSecondsSinceLastEventType(
            kCGEventSourceStateHIDSystemState, kCGAnyInputEventType
        )
    )


def screen_locked() -> bool:
    """True if the lock screen is showing."""
    session = CGSessionCopyCurrentDictionary() or {}
    return bool(session.get("CGSSessionScreenIsLocked", False))


def screensaver_running() -> bool:
    """True if a screensaver process is currently engaged."""
    for args in (["pgrep", "-x", "ScreenSaverEngine"], ["pgrep", "-f", "legacyScreenSaver"]):
        try:
            if subprocess.run(args, capture_output=True).returncode == 0:
                return True
        except OSError:
            continue  # this probe failed; still try the other matcher
    return False


def focus_mode() -> str | None:
    """Name of the active macOS Focus mode, or None if none / undetermined.

    There is no public API for Focus state, so this reads the undocumented
    Do Not Disturb database. It is best-effort and may break on a major
    macOS release; every failure path simply returns None.
    """
    base = os.path.expanduser("~/Library/DoNotDisturb/DB")
    assertions_path = os.path.join(base, "Assertions.json")
    config_path = os.path.join(base, "ModeConfigurations.json")

    # Which mode is currently asserted? Absent records == no active Focus.
    try:
        with open(assertions_path) as f:
            records = json.load(f)["data"][0]["storeAssertionRecords"]
        if not records:
            return None
        mode_id = records[0]["assertionDetails"]["assertionDetailsModeIdentifier"]
    except (OSError, KeyError, IndexError, ValueError):
        return None

    # Resolve the human-readable name; fall back to the raw identifier.
    try:
        with open(config_path) as f:
            configs = json.load(f)["data"][0]["modeConfigurations"]
        return configs[mode_id]["mode"]["name"]
    except (OSError, KeyError, IndexError, ValueError):
        return mode_id  # e.g. "com.apple.focus.work"


def assess(idle_threshold: float, away_focus: tuple[str, ...] = ()) -> dict:
    locked = screen_locked()
    saver = screensaver_running()
    idle = idle_seconds()
    focus = focus_mode()

    away_focus_norm = {f.strip().lower() for f in away_focus if f.strip()}
    focus_is_away = focus is not None and focus.lower() in away_focus_norm

    # Order matters: strongest, most deliberate signals win first.
    if locked:
        status, reason = "away", "screen is locked"
    elif saver:
        status, reason = "away", "screensaver is active"
    elif focus_is_away:
        status, reason = "away", f"focus mode '{focus}' is configured as away"
    elif idle >= idle_threshold:
        status, reason = "away", f"idle {idle:.0f}s (>= {idle_threshold:.0f}s)"
    else:
        status, reason = "present", f"active within last {idle:.0f}s"

    return {
        "status": status,
        "reason": reason,
        "signals": {
            "screen_locked": locked,
            "screensaver_running": saver,
            "idle_seconds": round(idle, 1),
            "focus_mode": focus,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect macOS presence.")
    parser.add_argument(
        "--idle", type=float, default=120.0,
        help="Idle seconds before counting as away (default: 120)",
    )
    parser.add_argument(
        "--away-focus", default="",
        help="Comma-separated Focus mode names that should count as away "
             "(e.g. 'Sleep,Personal'). Matches the human name or raw identifier.",
    )
    args = parser.parse_args()

    away_focus = tuple(args.away_focus.split(",")) if args.away_focus else ()
    result = assess(args.idle, away_focus)
    print(json.dumps(result))
    return 0 if result["status"] == "present" else 1


if __name__ == "__main__":
    sys.exit(main())
