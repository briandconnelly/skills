// Gate wrapper: the production extension against a fixture bot-env, so the
// pi-coding-agent gate exercises real routing without credentials.
import { fileURLToPath } from "node:url"

import { createAgentBotIdentity } from "../../scripts/pi/agent-bot-identity"

export default createAgentBotIdentity({ botEnv: fileURLToPath(new URL("./bot-env-fixture", import.meta.url)) })
