// pi-gate fixture: an extension CLI flag.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerFlag("gate-verbose", { type: "boolean", description: "Print more detail" });
}
