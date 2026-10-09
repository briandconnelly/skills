// pi-gate review fixture: a tool whose result text has a newline, quotes, and non-ASCII.
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerTool(
		defineTool({
			name: "two_lines",
			label: "Two Lines",
			description: "Returns two lines",
			parameters: Type.Object({}),
			async execute() {
				return { content: [{ type: "text", text: 'first "line"\nsecond line, café' }], details: {} };
			},
		}),
	);
}
