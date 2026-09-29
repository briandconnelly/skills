# 001 — Gate spike results

Date: 2026-09-29 (all runs on this date)
Pi: 0.99.1 at `/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent`, macOS (Darwin 27.0.0)
Spec: `docs/superpowers/specs/2026-09-29-pi-coding-agent-design.md`, section Spike (local planning file, not tracked).

Each item states the question, the exact command, the observed output (trimmed, not paraphrased), a verdict (confirmed / refuted / partial), and the consequence for the gate requirements (R3).
Probes ran from untracked scratch (`.eval-tmp/pi-spike/`); their sources are reproduced here so the runs can be repeated.
Every Pi run redirected stdin from `/dev/null`.

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
REAL AGENT DIR UNCHANGED   (38 files hashed)
files Pi wrote into the throwaway agent directory:
  auth.json
  models-store.json
{"pending":0,"state":{"callCount":2,"deferredFetchCount":0,"cancelledDeferred":[]}}
{"toolName":"hello","isError":false}
```

Verdict: confirmed.

Consequence for R3: R3.1's environment is sufficient for isolation; the gate can hash the real agent directory before and after each run (R3.2) with the command above, and a scripted turn needs no network.

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
# first: -e inventory-probe.ts -e faux-probe.ts -e hello.ts -e dynamic-tools.ts
# last:  -e faux-probe.ts -e hello.ts -e dynamic-tools.ts -e inventory-probe.ts
PI_CODING_AGENT_DIR=$S/agent PI_OFFLINE=1 PI_SKIP_VERSION_CHECK=1 \
  PI_SPIKE_FAUX_OUT=$S/s3-faux-$order.json PI_SPIKE_INVENTORY_OUT=$S/s3-inventory-$order.json \
  pi -ne -ns -np --no-themes -nc --no-session <extensions in that order> \
  --provider gate-faux --model scripted --mode json "greet gate" < /dev/null
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

Verdict: confirmed, with a timing constraint.
At `session_start` the inventory depends on load order: loaded first, the probe misses `echo_session`.
At `agent_start` both orders see every tool.

Consequence for R3:
The harness's inventory point is `agent_start` (R3.4), so even Tier 1 runs a minimal faux turn (one scripted text reply) to reach it; that turn needs no model and no network (S1, S2).
Tools carry `sourceInfo` (`path`, `origin`, `scope`), so R3.8.4's provenance check extends to tools: an explicitly loaded file reports its absolute path with `origin: "top-level"`, `scope: "temporary"`; built-in tools report `builtin:<name>`, which R3.8.5 uses to tell built-ins from the target.
`grep`, `find`, `ls`, and `powershell` are registered `direct` but not active under default settings, so "active" (R3.8.3) must be checked against `getActiveTools()`, not inferred from exposure.
`getMcpServers()` returns `[]` with built-in MCP disabled; it does not throw.
