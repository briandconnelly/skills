# Scenario 2 (Audit) — baseline run

- **Date:** 2026-10-11
- **Tree:** `c154b17` (branch `fix/agent-friendly-cli-review-2026-10-11`, skill files as of commit c154b17)
- **Mode:** baseline (fresh general-purpose subagent, prompt only; challenge set)
- **Score:** 6/8 scored; 0/4 non-scored conformance
- **Subagent tokens:** 41,044 (harness-reported total for the run)
- **Transcript sha256:** `1a0436391c577220d59fa23306ace0c18de7816371abca0760cc27a6800ddc01` (session-local copy; not committed)

## Exact prompt given

> Audit this CLI for agent-friendliness and report your findings.
> You cannot run the tool; you have only this captured material.
> Each capture discards stderr (`2>/dev/null`), so every line shown is stdout.
> The audience is the tool's author, who can change anything.
>
> ```text
> $ depman --help 2>/dev/null
> DepMan 3.2 — the friendly dependency manager!
> Usage: depman [command] [options]
> Commands:
>   install     Install dependencies (aliases: i, add)
>   ls          Show stuff
>   clean       Remove unused packages from the global cache
>   sync        Sync the lockfile (asks for confirmation first)
> Options:
>   --quiet     Less output
>   --yes       Assume yes
>
> $ depman ls --json 2>/dev/null
> ✨ DepMan 3.2
> Checking for updates...
> [{"name":"left-pad","version":"1.3.0"},{"name":"is-odd","version":"3.0.1"}]
> Done in 0.42s ✓
>
> $ depman install nonexistent-pkg 2>/dev/null
> Error: something went wrong (see log)
> $ echo $?
> 1
> ```

Baseline wrapper: "Your only input is the task below. Do not read any file in this repository or anywhere on disk, do not run any command, and do not use any tool; answer from the task text alone."
Tool audit: 0 tool calls other than the final hand-back, so no skill access.

## Per-assertion scoring

| # | Assertion (verbatim) | Result | Evidence |
| --- | --- | --- | --- |
| S1 | `sync` prompting for confirmation is flagged as a hang risk in automation and ranked as the most severe finding, above stdout pollution (Invocation Safety, Severity). | **FAIL** | The hang is not a finding: it sits in "What I could not verify" ("Does `sync` hang waiting for confirmation when stdin is not a TTY? Probe: ..."); finding 1 (stdout pollution) is ranked first and the hang is "item 6" of the priority list, conditional on a probe. |
| S2 | The hang finding distinguishes what the capture shows (the documented prompt) from what is deduced (the non-TTY hang mechanism), whether or not it uses the skill's label words (Evidence). | **PASS** | Explicit observed-vs-unverifiable split; the prompt is taken from help and the hang is stated as unconfirmed. Passed on the split even though the hang was demoted out of the findings (that is S1's failure). |
| S3 | Banner, update-check line, and `Done in...` mixed with JSON on stdout is flagged as breaking machine parsing, and the finding treats the pollution as established by the capture rather than as a guess (Output, Evidence). | **PASS** | Finding 1: "writes four lines to stdout ... `depman ls --json \| jq .` fails"; scope note: "stderr discarded, so every line below is confirmed stdout". |
| S4 | The unstructured error plus generic exit `1` is flagged: no symbolic code to branch on (Errors And Exit Codes). | **PASS** | Finding 2: "Exit status is the generic `1` ... use distinct, documented exit codes ... so an agent can branch without parsing prose". |
| S5 | The implicit update check on a read path is flagged as a hidden side effect / phone-home finding (Side Effects And Telemetry). | **PASS** | Finding 5: "A read-only listing performs a network check ... hidden side effect". |
| S6 | `clean` mutating the global cache without `--dry-run` is flagged (Mutations). | **PASS** | Finding 10: "`clean` is destructive with no visible dry run". |
| S7 | Alias duplication (`i`, `add`) and the vague `ls  Show stuff` description are flagged against the discovery path (Command Model / Discovery). | **FAIL** | `ls` "Show stuff" flagged (finding 4); the aliases appear only as an unverifiable question ("Are `i`/`add` true aliases"), not as a discovery-path finding. |
| S8 | The report states which checklist areas the captured material cannot answer (e.g., stdin contract, tests) instead of silently skipping them (Report Format). | **PASS** | A dedicated "What I could not verify" section with a probe per item; it does not name stdin or tests specifically. |
| C1 | Findings use the `P0`-`P3` words and the finding template from `review-workflow.md`. | not met | Numbered findings with "(blocker)" tags; no template fields. |
| C2 | Evidence labels use the literal words `observed`, `inferred`, `absence-of-evidence`. | not met | Uses "observed" and "unverifiable". |
| C3 | The hang finding is `P0` and the stdout pollution finding is `P1` or higher. | not met | No P scale. |
| C4 | The coverage statement takes the form of the checklist coverage table with `not-checked` reasons. | not met | Prose list instead. |

**Set:** challenge.
**Notes:** the baseline is strong on everything the capture shows directly and weak on exactly the two skill-sensitive judgments: ranking a documented prompt as the top automation hazard without a probe, and treating alias duplication as a discovery defect.
The fixture change (stderr discarded) worked as intended: pollution is now reported as confirmed rather than guessed.

## Full final output

Verbatim final message returned by the subagent:

## Agent-friendliness audit: `depman` 3.2 (from captured output only)

Scope note: three captures, stderr discarded, so every line below is confirmed stdout. I did not run the tool; findings are split into **observed** (directly in the captures) and **unverifiable** (worth checking, but the captures cannot show them). Nothing in the second list is reported as a defect.

### Observed findings, highest impact first

**1. `--json` output is not parseable as a stream (blocker).**
`depman ls --json` writes four lines to stdout: a banner (`✨ DepMan 3.2`), a progress line (`Checking for updates...`), the JSON array, and a timing trailer (`Done in 0.42s ✓`). `depman ls --json | jq .` fails; an agent has to guess which line is the payload. Fix: when `--json` is given, stdout must contain exactly one JSON document and nothing else. Banner, progress, and timing go to stderr or are suppressed. Apply the same rule whenever stdout is not a TTY, independent of `--json`.

**2. Errors go to stdout and carry no information (blocker).**
`Error: something went wrong (see log)` appeared with `2>/dev/null`, so it was written to stdout. It names neither the package, nor the cause (not found vs. registry unreachable vs. auth), nor the log path it tells the reader to consult. Exit status is the generic `1`. Fix: errors to stderr; include the failing argument and a specific cause (`package "nonexistent-pkg" not found in registry <url>`); print the actual log path if you reference one; when `--json` is set, emit a JSON error object on stdout (`{"error": {"code": "not_found", "package": "...", "message": "..."}}`); and use distinct, documented exit codes (e.g. 2 usage, 3 not found, 4 network) so an agent can branch without parsing prose.

**3. `--json` is undocumented.**
It works on `ls` but does not appear in `--help`. An agent that reads help (the only discovery path it has) will never find it. Fix: list `--json` in global options, and state which commands honour it. Prefer making it a global flag that every command supports.

**4. `ls` is described as "Show stuff".**
Agents choose a command from the one-line summaries in help. "Show stuff" gives nothing to match on. Fix: say what it lists and from where (`List installed dependencies for the current project`), and mention `--json` there.

**5. A read-only listing performs a network check.**
`Checking for updates...` during `ls --json` means a read-only query has a hidden side effect, nondeterministic latency, and an offline failure mode. It is also ambiguous whether it checks for DepMan self-updates or package updates. Fix: never check for updates during a query command; make the self-update check opt-in (`depman check-update`) or, at minimum, disable it under `--json`, when stdout is not a TTY, or via a documented env var.

**6. Nondeterministic trailer.**
`Done in 0.42s ✓` changes on every run, which breaks golden-output tests and diff-based comparison. Fix: stderr only, and only when stdout is a TTY.

**7. No documented `--version` flag.**
The version is embedded in the banner but there is no `--version` in help, so an agent must parse the banner (which finding 1 says should disappear in machine modes). Fix: add `--version` printing only `3.2` (or the full semver) on stdout.

**8. Decorative Unicode in machine-facing output.**
`✨`, `✓`, and the em dash in the banner are fine for a terminal but are noise, and possibly encoding hazards, in logs and pipes. Fix: emit them only when stdout is a TTY, and honour `NO_COLOR`/`TERM=dumb` for any color codes (color is not visible in a text capture; see unverifiable list).

**9. Help text is thin on contract.**
Missing: per-command options (does `depman ls --help` exist?), exit code meanings, whether global options go before or after the command (`Usage: depman [command] [options]` suggests after only), `--yes` semantics for non-interactive use, and `--quiet`'s precise effect ("Less output" does not say whether it strips the banner in `--json` mode). Each of these is something an agent will otherwise discover by trial.

**10. `clean` is destructive with no visible dry run.**
`Remove unused packages from the global cache` is irreversible; help shows no `--dry-run` or listing of what would be removed. Fix: add `--dry-run` (and make `--json` report the planned removals).

### What I could not verify, and the probe for each

These are real hazards for agents but the captures cannot show them. Run each before treating it as a finding.

- **Does `sync` hang waiting for confirmation when stdin is not a TTY?** Probe: `depman sync < /dev/null; echo $?` with a timeout. Expected: immediate failure with a message naming `--yes`, non-zero exit, no hang.
- **Does `--yes` apply to all prompts, or only `sync`?** Probe: run `clean` and `install` under `< /dev/null` with and without `--yes`.
- **Does `--quiet --json` produce clean JSON?** If so, finding 1 is "wrong default"; if not, it is "no clean mode exists at all". Probe: `depman ls --json --quiet 2>/dev/null | jq .`.
- **What was on stderr** during each of the three commands? The captures discarded it; rerun with `2>&1 >/dev/null` to see the stderr-only stream. If the `--json` run wrote the same banner to both streams, that is a separate finding.
- **Does `--json` work on `install`, `clean`, and `sync`**, or only `ls`?
- **Exit code on success.** Not captured; confirm `depman ls --json >/dev/null; echo $?` is `0`.
- **Are ANSI color codes emitted when stdout is a pipe?** Probe: `depman ls | cat -v`. Text captures cannot show this.
- **Does the "log" referenced in the error exist, and where?** Probe: `find`/`ls` the likely config dirs after the failing `install`, or check whether a verbose flag prints the path.
- **Are `i`/`add` true aliases** (identical behaviour), or does `add` also edit a manifest? The help lists them as aliases; confirm with `depman add --help` vs `depman install --help`.

### Suggested priority for the author

1. Clean `--json` (findings 1, 6, 8): one document on stdout, everything else to stderr.
2. Structured errors on stderr with specific causes and distinct exit codes (finding 2).
3. Document `--json`, add `--version`, rewrite `ls` summary, document exit codes and `--yes` (findings 3, 4, 7, 9).
4. Remove the update check from query commands (finding 5).
5. Add `--dry-run` to `clean` (finding 10).
6. Run the non-TTY `sync` probe; if it hangs, that becomes a blocker alongside items 1 and 2.
