// pi-gate negative fixture: an extension whose factory never finishes loading.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default async function (pi: ExtensionAPI) {
	pi.registerFlag("hang-flag", { type: "boolean", description: "Registered before hanging" });
	await new Promise((resolve) => setTimeout(resolve, 1e9));
}
