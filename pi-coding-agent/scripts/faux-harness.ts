// pi-gate harness, loaded last by pi_gate.py. It registers scripted faux providers so a
// gate run needs no model or network, and it registers /pi-gate-inventory, which pi_gate.py
// sends after every run settles: the inventory then sees resources that other extensions
// register in any handler of that run (decisions/001-gate-spike.md, S3).
import { readFileSync, writeFileSync } from "node:fs";
import {
	type AssistantMessage,
	type FauxProviderHandle,
	type FauxResponseStep,
	fauxAssistantMessage,
	fauxProvider,
	fauxText,
	fauxToolCall,
} from "@earendil-works/pi-ai";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

interface Step {
	provider: string;
	text?: string;
	toolCall?: { name: string; arguments: Record<string, unknown> };
	expectTranscript?: string;
}

// Every string inside a value, so a marker is matched as text, not in its JSON-escaped form.
function strings(value: unknown): string[] {
	if (typeof value === "string") return [value];
	if (Array.isArray(value)) return value.flatMap(strings);
	if (value && typeof value === "object") return Object.values(value).flatMap(strings);
	return [];
}

interface HarnessSpec {
	inventoryPath: string;
	providers: { provider: string; models: string[] }[];
	steps: Step[];
}

function reply(step: Step): AssistantMessage {
	if (step.toolCall) {
		return fauxAssistantMessage(fauxToolCall(step.toolCall.name, step.toolCall.arguments), {
			stopReason: "toolUse",
		});
	}
	return fauxAssistantMessage(fauxText(step.text ?? "pi-gate"));
}

export default function (pi: ExtensionAPI) {
	const specPath = process.env.PI_GATE_SPEC;
	if (!specPath) throw new Error("PI_GATE_SPEC is not set; faux-harness.ts is loaded only by pi_gate.py");
	const spec = JSON.parse(readFileSync(specPath, "utf8")) as HarnessSpec;

	const handles = new Map<string, FauxProviderHandle>();
	for (const { provider, models } of spec.providers) {
		const handle = fauxProvider({ provider, models: models.map((id) => ({ id })) });
		handles.set(provider, handle);
		pi.registerProvider(handle.provider);
	}

	const transcriptMisses: string[] = [];
	const queues = new Map<string, FauxResponseStep[]>();
	for (const step of spec.steps) {
		const expected = step.expectTranscript;
		const entry: FauxResponseStep = expected
			? (context) => {
					// Scripted assistant replies are the gate's own text; only what Pi and the artifact
					// sent (system, user, and tool messages) can satisfy the expectation.
					const sent = context.messages.filter((m) => m.role !== "assistant");
					if (!strings(sent).some((text) => text.includes(expected))) transcriptMisses.push(expected);
					return reply(step);
				}
			: reply(step);
		queues.set(step.provider, [...(queues.get(step.provider) ?? []), entry]);
	}
	for (const [provider, steps] of queues) {
		const handle = handles.get(provider);
		if (!handle) throw new Error(`a scripted step names provider ${provider}, which is not registered`);
		handle.setResponses(steps);
	}

	pi.registerCommand("pi-gate-inventory", {
		description: "pi-gate: write what this run loaded",
		handler: async () => {
			writeFileSync(
				spec.inventoryPath,
				JSON.stringify({
					tools: pi.getAllTools().map((t) => ({ name: t.name, exposure: t.exposure, sourceInfo: t.sourceInfo })),
					activeTools: pi.getActiveTools(),
					mcpServers: pi.getMcpServers().map((s) => ({ name: s.name, extensionPath: s.extensionPath })),
					faux: [...handles].map(([provider, handle]) => ({
						provider,
						pending: handle.getPendingResponseCount(),
						callCount: handle.state.callCount,
					})),
					transcriptMisses,
				}),
			);
		},
	});
}
