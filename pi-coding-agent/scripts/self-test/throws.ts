// pi-gate self-test control: a tool whose execute() throws must fail Tier 2.
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerTool(
		defineTool({
			name: "boom",
			label: "Boom",
			description: "Always throws",
			parameters: Type.Object({}),
			async execute() {
				throw new Error("boom exploded");
			},
		}),
	);
}
