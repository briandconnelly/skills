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
