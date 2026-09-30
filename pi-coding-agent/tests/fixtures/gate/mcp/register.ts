// pi-gate fixture: an extension-registered MCP server, disabled so the gate spawns nothing.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
	pi.registerMcpServer("gate-docs", { command: "gate-docs-server", enabled: false });
}
