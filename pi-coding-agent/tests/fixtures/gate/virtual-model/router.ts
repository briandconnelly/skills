// pi-gate fixture: a virtual model routing short prompts to a local model, the rest to Claude.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const SHORT = 200;

export default function (pi: ExtensionAPI) {
	pi.registerVirtualModel({
		provider: "router",
		id: "auto",
		name: "Auto",
		route(request, ctx) {
			const last = JSON.stringify(request.messages.at(-1) ?? "");
			const [provider, id] = last.length < SHORT ? ["llama.cpp", "qwen"] : ["anthropic", "claude-sonnet-4-5"];
			const model = ctx.modelRegistry.find(provider, id);
			if (!model) throw new Error(`physical model ${provider}/${id} is not available`);
			return { model, thinkingLevel: "off" };
		},
	});
}
