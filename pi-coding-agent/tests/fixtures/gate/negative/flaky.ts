// pi-gate negative fixture: a tool that fails when asked to, for tool-result matching.
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerTool(
		defineTool({
			name: "flaky",
			label: "Flaky",
			description: "Fails when fail is true",
			parameters: Type.Object({ fail: Type.Boolean() }),
			async execute(_id, params) {
				if (params.fail) throw new Error("flaky failed");
				return { content: [{ type: "text", text: "flaky ok" }], details: {} };
			},
		}),
	);
}
