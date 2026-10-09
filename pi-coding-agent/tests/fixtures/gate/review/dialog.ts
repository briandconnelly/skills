// pi-gate review fixture: a command that opens a confirm dialog, which RPC must answer.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("ask", {
		description: "Ask before noting",
		handler: async (_args, ctx) => {
			const ok = await ctx.ui.confirm("Proceed?", "Add the note?");
			pi.sendMessage({ customType: "asked", content: `confirmed=${ok}`, display: true });
		},
	});
}
