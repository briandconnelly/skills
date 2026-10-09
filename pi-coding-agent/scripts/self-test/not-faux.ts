// pi-gate self-test control: a provider that is not the faux model; Tier 2 must fail on it.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerProvider("not-faux", {
		baseUrl: "http://127.0.0.1:9/v1",
		apiKey: "unused",
		api: "openai-completions",
		models: [
			{
				id: "m",
				name: "not faux",
				reasoning: false,
				input: ["text"],
				cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
				contextWindow: 1000,
				maxTokens: 100,
			},
		],
	});
}
