// pi-gate review fixture: a session_start handler that throws.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("start-probe", { description: "Present so the target is observed", handler: async () => {} });
	pi.on("session_start", () => {
		throw new Error("session_start blew up");
	});
}
