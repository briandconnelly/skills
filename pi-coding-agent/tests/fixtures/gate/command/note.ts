// pi-gate fixture: an extension command whose effect is a custom message.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("note", {
		description: "Add a note to the session",
		handler: async (args) => {
			pi.sendMessage({ customType: "note", content: `note: ${args}`, display: true });
		},
	});
}
