---
name: presence-detector
description: Use when checking whether the user is at their macOS machine — "am I away", idle/away detection, or presence-gating an automation. Combines screen lock, screensaver, input idle time, and Focus mode into one verdict. macOS only.
---

# Presence Detector

Determines whether the user is **present** or **away** from a macOS machine by
combining four independent signals, so no single false reading (e.g. watching a
video with no input) flips the verdict on its own.

## Running it

The script carries PEP 723 inline metadata; run it with `uv`, which provisions
the one dependency (PyObjC's Quartz) in an ephemeral environment.

```bash
uv run scripts/presence.py                      # JSON verdict
uv run scripts/presence.py --idle 180           # >=180s idle counts as away (default 120)
uv run scripts/presence.py --away-focus Sleep,Personal   # these Focus modes mean "away"
```

`scripts/presence.py` is `chmod +x` and uses a `uv run` shebang, so `./scripts/presence.py` also works.

## Output

- **Exit code:** `0` if present, `1` if away — usable directly in launchd / shell guards.
- **stdout:** JSON `{status, reason, signals}` where `signals` carries the raw
  `screen_locked`, `screensaver_running`, `idle_seconds`, and `focus_mode` readings.

## Signal precedence

The verdict is decided by the strongest, most deliberate signal first:

1. **screen locked** → away (an explicit "I'm leaving")
2. **screensaver active** → away
3. **active Focus mode in `--away-focus`** → away (Focus is otherwise reported as context only)
4. **idle ≥ threshold** → away (default 120s)
5. otherwise → present

## Notes

- macOS only. Lock + idle detection use Quartz, which `uv` provisions from the
  script's PEP 723 metadata.
- Focus state is read from the undocumented Do Not Disturb database — best-effort,
  may break on a major macOS release; every failure path returns `None` safely.
