// Validate original entries with the installed Pi before the gate disables servers.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const [modulePath] = process.argv.slice(2);
const { validateMcpServerConfig } = await import(pathToFileURL(modulePath).href);
const config = JSON.parse(readFileSync(0, "utf8"));
const errors = Object.entries(config.mcpServers)
	.map(([name, value]) => validateMcpServerConfig(name, value))
	.filter((result) => typeof result === "string");
console.log(JSON.stringify(errors));
