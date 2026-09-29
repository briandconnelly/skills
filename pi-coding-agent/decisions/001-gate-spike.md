# 001 — Gate spike results

Date: 2026-09-29 (all runs on this date)
Pi: 0.99.1 at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`, macOS (Darwin 27.0.0)
Spec: `docs/superpowers/specs/2026-09-29-pi-coding-agent-design.md`, section Spike (local planning file, not tracked).

Each item states the question, the exact command, the observed output (trimmed, not paraphrased), a verdict (confirmed / refuted / partial), and the consequence for the gate requirements (R3).
Probes ran from untracked scratch (`.eval-tmp/pi-spike/`); their sources are reproduced here so the runs can be repeated.
Every Pi run redirected stdin from `/dev/null`.
`dynamic-tools.ts` and `hello.ts` are Pi's own bundled examples under `$P/examples/extensions/`.
A cross-model review (Codex via amicus, job 72ab4bbb, 2026-09-29) found five overreaches in the first version of this record; the S2, S3, and S6 sections below were narrowed or extended by follow-up runs in response.

## Summary

| Item | Verdict | Consequence for R3 |
|---|---|---|
| S1 faux provider from outside Pi | confirmed | Tier 2 works as designed; event and message field names recorded |
| S2 isolation | confirmed (narrow) | the throwaway agent directory keeps the real one's regular files unchanged, and a scripted turn completes with outbound network denied; `PI_OFFLINE` is not a network boundary for extension code |
| S3 inventory point | confirmed after follow-up | load the harness last and take the inventory at `agent_end`; earlier points miss tools registered by later handlers; Tier 1 runs a one-step faux turn; tools carry `sourceInfo` |
| S4 themes | partial | Pi reports no invalid theme outside the TUI; Tier 1 validates against the installed schema, variable resolution unchecked |
| S5 project trust | confirmed | `--approve` loads project resources process-only; a skip is silent, caught only as a missing declared resource |
| S6 package via `-e` | partial after follow-up | only prompts carry `origin: "package"`; extension tools, extension commands, and skills report `origin: "top-level"`, so package provenance is a path-under-package-directory check for every kind |

## S1 — faux provider from outside Pi's package

Question: can an extension loaded with `-e` from outside Pi's package import `@earendil-works/pi-ai` through Pi's loader, register the faux provider, and have `--provider`/`--model` select it for a scripted turn?

Probe (`faux-probe.ts`):

```typescript
// Spike S1: can an extension outside Pi's package register pi-ai's faux provider?
import { writeFileSync } from "node:fs";
import { fauxAssistantMessage, fauxProvider, fauxText, fauxToolCall } from "@earendil-works/pi-ai";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	const faux = fauxProvider({ provider: "gate-faux", models: [{ id: "scripted" }] });
	faux.setResponses([
		fauxAssistantMessage(fauxToolCall("hello", { name: "gate" }), { stopReason: "toolUse" }),
		fauxAssistantMessage(fauxText("done")),
	]);
	pi.registerProvider(faux.provider);
	pi.on("agent_end", () => {
		writeFileSync(
			process.env.PI_SPIKE_FAUX_OUT ?? "faux-probe.json",
			JSON.stringify({ pending: faux.getPendingResponseCount(), state: faux.state }),
		);
	});
}
```

Command (`S` is the scratch directory, `P` the Pi package root):

```bash
cd $S/work
PI_CODING_AGENT_DIR=$S/agent PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 PI_SPIKE_FAUX_OUT=$S/s1-faux.json \
  pi -ne -ns -np --no-themes -nc --no-session \
  -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts \
  --provider gate-faux --model scripted --mode json "greet gate" \
  > $S/s1-events.jsonl 2> $S/s1-stderr.txt < /dev/null
```

Observed (exit 0, stderr empty, no `extension_error` events):

```text
{"type":"tool_execution_end","toolName":"hello","result":{"content":[{"type":"text","text":"Hello, gate!"}],"details":{"greeted":"gate"}},"isError":false}
{"provider":"gate-faux","model":"scripted","stopReason":"toolUse"}
{"provider":"gate-faux","model":"scripted","stopReason":"stop"}
{"pending":0,"state":{"callCount":2,"deferredFetchCount":0,"cancelledDeferred":[]}}
event types: agent_end×1 agent_settled×1 agent_start×1 message_end×5 message_start×5 message_update×6 session×1 tool_execution_end×1 tool_execution_start×1 turn_end×2 turn_start×2
```

Verdict: confirmed.

Consequence for R3: Tier 2 is feasible as designed.
`tool_execution_end` carries `toolName`, `result.content`, `result.details`, and `isError`; assistant `message_end` records carry `provider`, `model`, and `stopReason`; the faux handle's `getPendingResponseCount()` and `state.callCount` are readable at `agent_end`.

## S2 — isolation from the real agent directory and the network

Question: with `PI_CODING_AGENT_DIR` pointing at a throwaway directory plus `PI_OFFLINE=1` and `PI_SKIP_VERSION_CHECK=1`, does a gate run leave the real `~/.pi/agent` untouched and run with no network?

Command (the S1 run inside a network-denying sandbox, with the real agent directory hashed before and after):

```bash
find ~/.pi/agent -type f -print0 | xargs -0 shasum -a 256 | sort > $S/s2-real-before.txt
cd $S/work
PI_CODING_AGENT_DIR=$S/agent PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 PI_SPIKE_FAUX_OUT=$S/s2-faux.json \
  sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip "*:*"))' \
  pi -ne -ns -np --no-themes -nc --no-session \
  -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts \
  --provider gate-faux --model scripted --mode json "greet gate" \
  > $S/s2-events.jsonl 2> $S/s2-stderr.txt < /dev/null
find ~/.pi/agent -type f -print0 | xargs -0 shasum -a 256 | sort > $S/s2-real-after.txt
diff $S/s2-real-before.txt $S/s2-real-after.txt && echo "REAL AGENT DIR UNCHANGED"
```

Positive control for the sandbox (so a clean run is evidence, not an idle filter):

```bash
sandbox-exec -p '(version 1)(allow default)(deny network-outbound (remote ip "*:*"))' curl -sS -m 5 https://pi.dev
# curl: (7) Failed to connect to pi.dev port 443 after 40 ms: Couldn't connect to server
curl -sS -m 5 -o /dev/null -w '%{http_code}\n' https://pi.dev
# 200
```

Observed:

```text
exit=0
REAL AGENT DIR UNCHANGED   (38 regular files hashed)
files Pi wrote into the throwaway agent directory:
  auth.json
  models-store.json
{"pending":0,"state":{"callCount":2,"deferredFetchCount":0,"cancelledDeferred":[]}}
{"toolName":"hello","isError":false}
```

Verdict: confirmed.

What this shows, and what it does not:
the hashes cover the contents and names of regular files only (`find -type f`), not directories, symlinks, or metadata;
the network result shows a scripted turn needs no outbound network, not that `PI_OFFLINE` stops extension code from using it (the sandbox, not the environment variable, denied the network here).

Consequence for R3: R3.1's environment isolates Pi's own configuration; R3.2's before/after check must list the whole tree (`find ~/.pi/agent -print` with each entry's type and, for files, a content hash, and for symlinks, the target), not only regular files; R3.14's statement that the gate is not a sandbox stands.

## S3 — when the inventory sees every tool

Question: can an extension observe every registered tool, including one another extension registers during `session_start`, and at which event?

Probe (`inventory-probe.ts`):

```typescript
// Spike S3: when can an extension see every registered tool, command, and MCP server?
import { writeFileSync } from "node:fs";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	const out = process.env.PI_SPIKE_INVENTORY_OUT ?? "inventory.json";
	const snapshots: Record<string, unknown> = {};
	const snap = (label: string) => {
		let mcpServers: unknown;
		try {
			mcpServers = pi.getMcpServers();
		} catch (error) {
			mcpServers = { error: String(error) };
		}
		snapshots[label] = {
			all: pi.getAllTools().map((t) => ({ name: t.name, exposure: t.exposure, sourceInfo: t.sourceInfo })),
			active: pi.getActiveTools(),
			commands: pi.getCommands().map((c) => ({ name: c.name, source: c.source, sourceInfo: c.sourceInfo })),
			mcpServers,
		};
		writeFileSync(out, JSON.stringify(snapshots, null, 2));
	};
	pi.on("session_start", () => snap("session_start"));
	pi.on("agent_start", () => snap("agent_start"));
	pi.on("agent_end", () => snap("agent_end"));
}
```

Command, run once with the probe loaded first and once with it loaded last (`dynamic-tools.ts` registers `echo_session` in its `session_start` handler):

```bash
cd $S/work
run() {  # run <label> <extension flags...>
  PI_CODING_AGENT_DIR=$S/agent PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 \
    PI_SPIKE_FAUX_OUT=$S/s3-faux-$1.json PI_SPIKE_INVENTORY_OUT=$S/s3-inventory-$1.json \
    pi -ne -ns -np --no-themes -nc --no-session "${@:2}" \
    --provider gate-faux --model scripted --mode json "greet gate" \
    > $S/s3-events-$1.jsonl 2> $S/s3-stderr-$1.txt < /dev/null
}
run first -e $S/inventory-probe.ts -e $S/faux-probe.ts \
  -e $P/examples/extensions/hello.ts -e $P/examples/extensions/dynamic-tools.ts
run last -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts \
  -e $P/examples/extensions/dynamic-tools.ts -e $S/inventory-probe.ts
```

Observed (both runs exit 0, no `extension_error`, stderr empty; tool paths shortened to basenames):

```text
first session_start tools=["read","bash","powershell","edit","write","grep","find","ls","hello"] active=["read","bash","edit","write","hello"] mcpServers=[]
first agent_start   tools=["read","bash","powershell","edit","write","grep","find","ls","hello","echo_session"] active=["read","bash","edit","write","hello","echo_session"] mcpServers=[]
first agent_end     tools=["read","bash","powershell","edit","write","grep","find","ls","hello","echo_session"] active=["read","bash","edit","write","hello","echo_session"] mcpServers=[]
last  session_start tools=["read","bash","powershell","edit","write","grep","find","ls","hello","echo_session"] active=["read","bash","edit","write","hello","echo_session"] mcpServers=[]
last  agent_start   tools=["read","bash","powershell","edit","write","grep","find","ls","hello","echo_session"] active=["read","bash","edit","write","hello","echo_session"] mcpServers=[]
last  agent_end     tools=["read","bash","powershell","edit","write","grep","find","ls","hello","echo_session"] active=["read","bash","edit","write","hello","echo_session"] mcpServers=[]
sourceInfo of hello: {"path":"<P>/examples/extensions/hello.ts","source":"cli","scope":"temporary","origin":"top-level"}
sourceInfo of read:  {"path":"builtin:read","source":"builtin","scope":"temporary","origin":"top-level"}
```

Follow-up (review finding: a tool registered inside a later extension's own `agent_start` handler).
`late-tool.ts`:

```typescript
// Follow-up to S3: registers a tool inside its own agent_start handler.
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.on("agent_start", () => {
		pi.registerTool(
			defineTool({
				name: "late_tool",
				label: "Late Tool",
				description: "Registered during agent_start",
				parameters: Type.Object({}),
				async execute() {
					return { content: [{ type: "text", text: "late" }], details: {} };
				},
			}),
		);
	});
}
```

Run with the same `run` helper, loading `late-tool.ts` in place of `dynamic-tools.ts`:

```bash
run first -e $S/inventory-probe.ts -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts -e $S/late-tool.ts
run last -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts -e $S/late-tool.ts -e $S/inventory-probe.ts
```

Observed (both exit 0, stderr empty; output files `s3b-*`):

```text
first session_start late_tool present: False
first agent_start   late_tool present: False
first agent_end     late_tool present: True
last  session_start late_tool present: False
last  agent_start   late_tool present: True
last  agent_end     late_tool present: True
```

Verdict: confirmed after follow-up, with a timing constraint.
Handlers run in extension load order at every event, so a snapshot taken before a later extension's handler for the same event misses what that handler registers.
Loaded last, the probe sees every tool at `agent_start` and `agent_end`; loaded first, only `agent_end` sees `late_tool`.

Consequence for R3:
`pi-gate` loads the harness last and takes the inventory at `agent_end` (R3.4); a tool an artifact registers inside its own `agent_end` handler is still not guaranteed to be observed, and the report says so.
Tier 1 therefore runs a minimal faux turn (one scripted text reply) to reach `agent_end`; that turn needs no model and no network (S1, S2).
Tools carry `sourceInfo` (`path`, `origin`, `scope`), so R3.8.4's provenance check extends to tools: an explicitly loaded file reports its absolute path with `origin: "top-level"`, `scope: "temporary"`; built-in tools report `builtin:<name>`, which R3.8.5 uses to tell built-ins from the target.
`grep`, `find`, `ls`, and `powershell` are registered `direct` but not active under default settings, so "active" (R3.8.3) must be checked against `getActiveTools()`, not inferred from exposure.
`getMcpServers()` returns `[]` with built-in MCP disabled; it does not throw.

## RPC helper used by S4–S6

`rpc_probe.py` starts `pi --mode rpc`, sends JSONL commands, prints every line until each command has a response, then closes stdin.
In every run below Pi exited on its own when stdin closed (no "killed" line).

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Spike helper: start `pi --mode rpc`, send JSONL commands, print every line received.

Usage: rpc_probe.py '<json command>' [...] -- <pi arguments>
"""

import json
import select
import subprocess
import sys
import time


def main() -> int:
    sep = sys.argv.index("--")
    commands, pi_args = sys.argv[1:sep], sys.argv[sep + 1 :]
    proc = subprocess.Popen(
        ["pi", "--mode", "rpc", *pi_args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdin is not None and proc.stdout is not None and proc.stderr is not None
    for command in commands:
        proc.stdin.write(command + "\n")
        proc.stdin.flush()
    responses, deadline = 0, time.monotonic() + 30
    while responses < len(commands) and time.monotonic() < deadline:
        ready, _, _ = select.select([proc.stdout], [], [], 0.5)
        if not ready:
            continue
        line = proc.stdout.readline()
        if not line:
            break
        print(line, end="")
        if json.loads(line).get("type") == "response":
            responses += 1
    proc.stdin.close()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("# pi did not exit within 5s of stdin closing; killed", file=sys.stderr)
    sys.stderr.write(proc.stderr.read())
    print(f"# exit={proc.returncode} responses={responses}/{len(commands)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## S4 — invalid themes without the TUI

Question: does Pi report an invalid theme in a non-interactive run, and does the installed schema catch what Pi does not?

Themes (built from the installed `dark.json`; its first color key is `accent`):

```bash
T=$P/dist/modes/interactive/theme
jq '.name="gate-good"' $T/dark.json > $S/themes/gate-good.json
jq '.name="gate-bad-ref" | .colors |= (to_entries | .[0].value = "no-such-var" | from_entries)' $T/dark.json > $S/themes/gate-bad-ref.json
jq '.name="gate-bad-missing" | .colors |= (to_entries | .[1:] | from_entries)' $T/dark.json > $S/themes/gate-bad-missing.json
```

Commands, per theme `$t`:

```bash
uv run --script $S/rpc_probe.py '{"id":"1","type":"get_state"}' -- \
  -ne -ns -np --no-themes -nc --no-session --theme $S/themes/$t.json --use-theme $t
pi -ne -ns -np --no-themes -nc --no-session -e $S/faux-probe.ts -e $P/examples/extensions/hello.ts \
  --theme $S/themes/$t.json --use-theme $t --provider gate-faux --model scripted --mode json "greet gate" < /dev/null
uvx --from check-jsonschema check-jsonschema --schemafile $T/theme-schema.json $S/themes/*.json
```

Observed (all Pi runs under the S2 environment):

```text
RPC get_state:  gate-good, gate-bad-ref, gate-bad-missing -> success:true, no other lines, exit 0
JSON mode:      gate-good exit=0 stderr_bytes=0 error/warn events=0
                gate-bad-ref exit=0 stderr_bytes=0 error/warn events=0
                gate-bad-missing exit=0 stderr_bytes=0 error/warn events=0
schema:         gate-bad-missing.json::$.colors: 'accent' is a required property
                (gate-good and gate-bad-ref pass the schema)
```

Verdict: partial.
Pi reports neither invalid theme outside the TUI; the installed schema catches a missing required color but not an unresolvable variable reference.

Consequence for R3: Theme Tier 1 is structural only — validate against the installed `theme-schema.json` — and the gate report marks variable resolution and rendering unchecked.

## S5 — project trust without a prompt

Question: does a `.pi/` project resource load non-interactively only with `--approve`, without writing a trust decision, and is a skip detectable?

Setup and commands (`-np` deliberately omitted so the prompt loads through discovery):

```bash
mkdir -p $S/proj/.pi/prompts
printf -- '---\ndescription: spike prompt\n---\nSay spike.\n' > $S/proj/.pi/prompts/spike-prompt.md
cd $S/proj
uv run --script $S/rpc_probe.py '{"id":"1","type":"get_commands"}' -- -ne -ns --no-themes -nc --no-session
uv run --script $S/rpc_probe.py '{"id":"1","type":"get_commands"}' -- -ne -ns --no-themes -nc --no-session --approve
```

Observed (real agent directory hashed before and after, as in S2):

```text
without --approve: commands = []   (no other events, nothing on stderr)
with --approve:
{"name":"spike-prompt","source":"prompt","sourceInfo":{"path":"$S/proj/.pi/prompts/spike-prompt.md","source":"auto","scope":"project","origin":"top-level","baseDir":"$S/proj/.pi"}}
REAL AGENT DIR UNCHANGED
throwaway agent directory afterwards: auth.json, models-store.json (no trust.json)
```

Verdict: confirmed.
A skipped project resource is not signalled; it is simply absent.

Consequence for R3: R3.2 as written works (`--approve`, process-only).
Because Pi does not signal the skip, a project artifact run without `--approve` is caught only by its declared resource being missing (R3.8.2), which the self-test's trust-skipped fixture (R3.12) must exercise.

## S6 — a package loaded with `-e`

Question: does `pi -e <package dir>` expose the package's resources with package provenance, without writing settings?

Setup and commands:

```bash
mkdir -p $S/pkg/prompts $S/pkg/extensions
printf '{"name":"gate-spike-package","version":"0.0.0","keywords":["pi-package"]}\n' > $S/pkg/package.json
printf -- '---\ndescription: package prompt\n---\nSay package.\n' > $S/pkg/prompts/pkg-prompt.md
cp $P/examples/extensions/hello.ts $S/pkg/extensions/hello.ts
cd $S/work
uv run --script $S/rpc_probe.py '{"id":"1","type":"get_commands"}' -- \
  -ne -ns -np --no-themes -nc --no-session -e $S/pkg
pi -ne -ns -np --no-themes -nc --no-session -e $S/faux-probe.ts -e $S/pkg -e $S/inventory-probe.ts \
  --provider gate-faux --model scripted --mode json "greet gate" < /dev/null
```

Observed:

```text
{"name":"pkg-prompt","source":"prompt","sourceInfo":{"path":"$S/pkg/prompts/pkg-prompt.md","source":"$S/pkg","scope":"temporary","origin":"package","baseDir":"$S/pkg"}}
json run exit=0; hello tool sourceInfo at agent_start:
{"path":"$S/pkg/extensions/hello.ts","source":"cli","scope":"temporary","origin":"top-level"}
{"toolName":"hello","isError":false}
{"pending":0,"state":{"callCount":2,"deferredFetchCount":0,"cancelledDeferred":[]}}
throwaway agent directory afterwards: auth.json, models-store.json (no settings.json)
```

Follow-up (review finding: commands and skills were not exercised).
Added to the package: a skill and an extension that registers a command.

```bash
mkdir -p $S/pkg/skills/pkg-skill
printf -- '---\nname: pkg-skill\ndescription: Spike skill shipped in a package.\n---\n\n# pkg-skill\n\nSay package skill.\n' \
  > $S/pkg/skills/pkg-skill/SKILL.md
```

`pkg/extensions/pkg-command.ts`:

```typescript
// Follow-up to S6: an extension command shipped in a package.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("pkg-command", {
		description: "Spike command shipped in a package",
		handler: async () => {},
	});
}
```

Same `get_commands` command as above; observed (exit 0, output file `s6b-rpc.txt`):

```text
{"name":"pkg-command","source":"extension","sourceInfo":{"path":"$S/pkg/extensions/pkg-command.ts","source":"cli","scope":"temporary","origin":"top-level"}}
{"name":"pkg-prompt","source":"prompt","sourceInfo":{"path":"$S/pkg/prompts/pkg-prompt.md","source":"$S/pkg","scope":"temporary","origin":"package","baseDir":"$S/pkg"}}
{"name":"skill:pkg-skill","source":"skill","sourceInfo":{"path":"$S/pkg/skills/pkg-skill/SKILL.md","source":"cli","scope":"temporary","origin":"top-level"}}
```

Verdict: partial after follow-up.
Only prompt templates report package provenance (`origin: "package"`, `baseDir`); extension tools, extension commands, and skills from the same package report `origin: "top-level"`, `source: "cli"`, and no `baseDir`.
No settings file is written.

Consequence for R3: R3.1's `-e <package dir>` works.
R3.8.4's package check is a path check for every kind: each declared resource's `sourceInfo.path` must lie under the package directory; `origin: "package"` is an extra check for prompts only.
