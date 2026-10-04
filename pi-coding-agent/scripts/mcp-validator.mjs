// Load original entries with the installed Pi's MCP config loader before the gate disables servers.
// Loading reads files only: no server starts and nothing connects.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const [modulePath, root] = process.argv.slice(2);
const { loadMcpConfig } = await import(pathToFileURL(modulePath).href);
const { config, scope, base } = JSON.parse(readFileSync(0, "utf8"));
const agentDir = join(root, "agent");
const cwd = join(root, "project");
mkdirSync(join(cwd, ".pi"), { recursive: true });
mkdirSync(agentDir, { recursive: true });
const project = scope === "project";
const target = project ? join(cwd, ".pi", "mcp.json") : join(agentDir, "mcp.json");
// A project file loads on top of the user-level file, so project overrides merge as in Pi.
if (project && typeof base === "string") writeFileSync(join(agentDir, "mcp.json"), base);
writeFileSync(target, JSON.stringify(config));
const loaded = loadMcpConfig({ agentDir, cwd, projectTrusted: project });
const prefix = `${target}: `;
console.log(
	JSON.stringify({
		// Errors in the user-level base are not the artifact's; an override of a broken base still fails.
		errors: loaded.errors.filter((error) => error.startsWith(prefix)).map((error) => error.slice(prefix.length)),
		servers: loaded.servers
			.filter((server) => server.source === target || server.override === target)
			.map((server) => ({ name: server.name, override: server.override === target })),
	}),
);
