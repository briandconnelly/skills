// pi-gate fixture: a shortcut and a message renderer, which only the TUI exercises.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerShortcut("ctrl+alt+g", { description: "Gate shortcut", handler: () => {} });
	pi.registerMessageRenderer("gate-status", () => undefined);
}
