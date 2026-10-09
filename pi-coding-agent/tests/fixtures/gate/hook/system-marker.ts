// pi-gate fixture: an event hook whose effect reaches the model's transcript.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerCommand("marker-status", { description: "Show that the marker hook is loaded", handler: async () => {} });
	pi.on("before_agent_start", (event) => ({ systemPrompt: `${event.systemPrompt}\nSYSTEM-MARKER-7F3A` }));
}
