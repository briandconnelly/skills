// pi-gate review fixture: an extension given as a directory with index.ts.
import { Type } from "@earendil-works/pi-ai";
import { defineTool, type ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerTool(
		defineTool({
			name: "word_count",
			label: "Word Count",
			description: "Count the words in a text",
			parameters: Type.Object({ text: Type.String() }),
			async execute(_id, params) {
				const words = params.text.split(/\s+/).filter(Boolean).length;
				return { content: [{ type: "text", text: `${words} words` }], details: { words } };
			},
		}),
	);
}
