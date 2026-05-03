# MCP Server Examples

Worked examples for a fictional MCP server, `slack-mcp`, that exposes Slack messaging, channels, and users to an agent. Every example is tagged with the [contract-checklist.md](contract-checklist.md) section(s) it demonstrates; decorative examples are not allowed. Use these as concrete shapes to mimic — not as schemas to copy verbatim.

## 1. Namespaced tool schema

Tool definition for `slack_send_message`. *Demonstrates §3 tool-shape rules.*

```json
{
  "name": "slack_send_message",
  "description": "Post a message to a Slack channel or DM.\n\nWhen to use: any time the agent has composed a message and a destination (channel id, user id, or thread ts) and wants to deliver it. Prefer this over `slack_create_channel` + post when the channel already exists.\n\nUsage notes:\n- DMs to users require a `user_id`, not a channel name; resolve via `slack_lookup_user` first.\n- Threaded replies require both `channel_id` and `thread_ts`; omitting `thread_ts` posts a new top-level message.\n\nFor the failure modes this tool can return (channel archived, not found, rate limited, etc.), see the `errors` field below — do not infer error semantics from this description.\n\nExample: {\"channel_id\": \"C0123ABCD\", \"text\": \"Deploy finished.\"}",
  "inputSchema": {
    "type": "object",
    "required": ["channel_id", "text"],
    "properties": {
      "channel_id": {
        "type": "string",
        "pattern": "^[CDG][A-Z0-9]{8,}$",
        "description": "Slack channel id (C…), DM id (D…), or group id (G…). Not a channel name."
      },
      "text": {
        "type": "string",
        "minLength": 1,
        "maxLength": 40000,
        "description": "Message body. Markdown subset per Slack mrkdwn rules."
      },
      "thread_ts": {
        "type": "string",
        "pattern": "^[0-9]+\\.[0-9]+$",
        "description": "Parent message timestamp; if set, this becomes a threaded reply."
      },
      "broadcast_to_channel": {
        "type": "boolean",
        "default": false,
        "description": "If `thread_ts` is set, also surface this reply in the main channel."
      }
    },
    "additionalProperties": false
  },
  "annotations": {
    "readOnlyHint": false,
    "destructiveHint": false,
    "idempotentHint": false,
    "openWorldHint": true
  },
  "errors": [
    {"code": "channel_archived", "temporary": false, "description": "Channel was archived; unarchive via slack_unarchive_channel before retrying."},
    {"code": "channel_not_found", "temporary": false, "description": "channel_id does not match any channel the bot can see."},
    {"code": "rate_limited", "temporary": true, "description": "Slack rate limit hit; honour `retry_after_ms` from the error payload."},
    {"code": "msg_too_long", "temporary": false, "description": "`text` exceeded 40000 characters; split into multiple messages."}
  ]
}
```

What to notice: the description orients the agent (when-to-use, usage notes, example invocation) but does **not** carry failure semantics — those live in the structured `errors` array, where each code has a `temporary` flag and a concrete repair direction. Parameter names are disambiguated (`channel_id`, `thread_ts`); `required` lists only what's truly necessary; annotations are honest — `idempotentHint: false` because re-sending creates a duplicate post, not a no-op. (`errors` is a convention extension on top of MCP; see §3 contract-checklist rule that side effects, idempotency, and rate limits are first-class contract, not prose.)

## 2. Structured tool response

Two responses from `slack_list_messages` showing the concise vs detailed result pattern: a structured concise default with an opt-in detail mode. *Demonstrates §3 output rules and §7 token efficiency together.*

Concise (default, `detail: "summary"`):

```json
{
  "messages": [
    {
      "ts": "1714600000.001200",
      "channel": "#deploys",
      "author": "alice",
      "preview": "Deploy started for api@v2.4.1"
    },
    {
      "ts": "1714600055.001300",
      "channel": "#deploys",
      "author": "deploy-bot",
      "preview": "All services green."
    }
  ],
  "has_more": true,
  "next_cursor": "eyJ0cyI6IjE3MTQ2MDAwNTUuMDAxMzAwIn0",
  "estimated_total": 47,
  "truncated": true,
  "truncation_hint": "hit cap of 50; narrow with `since=` or `query=`"
}
```

Detail (`detail: "full"`):

```json
{
  "messages": [
    {
      "ts": "1714600000.001200",
      "channel_id": "C0123ABCD",
      "channel": "#deploys",
      "author_id": "U07ALICE",
      "author": "alice",
      "text": "Deploy started for api@v2.4.1",
      "blocks": [{"type": "rich_text", "elements": [/* … */]}],
      "reactions": [],
      "thread_ts": null,
      "edited": null,
      "client_msg_id": "8f4c6e1a-7b22-4d6a-91a1-3aa72c4e9b07",
      "permalink": "https://slack.com/archives/C0123ABCD/p1714600000001200"
    }
  ],
  "has_more": true,
  "next_cursor": "eyJ0cyI6IjE3MTQ2MDAwNTUuMDAxMzAwIn0",
  "estimated_total": 47,
  "truncated": true,
  "truncation_hint": "hit cap of 50; narrow with `since=` or `query=`"
}
```

What to notice: concise mode uses semantic identifiers (`alice`, `#deploys`) and a `preview` string; detail mode adds the raw IDs (`channel_id`, `author_id`, `client_msg_id`), the full `text` and `blocks`, plus null-valued fields. The truncation signal carries explicit repair guidance (`since=` or `query=`) — the agent doesn't have to guess what to do next. Pagination is cursor-based with `has_more` and `estimated_total`.

## 3. Resource index entry

A single entry from a `slack://channels/C0123ABCD/messages` index listing. *Demonstrates §4 resource indexing.*

```json
{
  "uri": "slack://channels/C0123ABCD/messages/1714600000.001200",
  "title": "Deploy started for api@v2.4.1",
  "summary": "Alice announces the start of the v2.4.1 API deploy; thread contains 12 follow-up replies including the green-light from deploy-bot.",
  "size": 8421,
  "last_modified": "2026-05-01T18:14:32Z",
  "content_type": "application/vnd.slack.message+json"
}
```

What to notice: `uri` is hierarchical and stable (channel id + message ts); `title` and `summary` together let the agent decide whether to fetch the body without reading it; `size` lets the agent estimate token cost; `last_modified` lets the agent skip a re-fetch if it already cached this version; `content_type` tells the agent which parser to use.

## 4. Resource body with chunking

The body fetched at `slack://channels/C0123ABCD/messages/1714600000.001200`, chunked because the thread is long. *Demonstrates §4 chunking with stable identifiers.*

Index entry that points at it:

```json
{
  "uri": "slack://channels/C0123ABCD/messages/1714600000.001200",
  "title": "Deploy started for api@v2.4.1",
  "summary": "Deploy thread; 12 replies across 3 chunks.",
  "size": 8421,
  "last_modified": "2026-05-01T18:14:32Z",
  "content_type": "application/vnd.slack.thread+json",
  "chunks": [
    {"id": "thread:1714600000.001200#root", "size": 412},
    {"id": "thread:1714600000.001200#replies-1-6", "size": 3902},
    {"id": "thread:1714600000.001200#replies-7-12", "size": 4107}
  ]
}
```

Body fragment for chunk `thread:1714600000.001200#replies-1-6`:

```json
{
  "resource_uri": "slack://channels/C0123ABCD/messages/1714600000.001200",
  "chunk_id": "thread:1714600000.001200#replies-1-6",
  "version": "2026-05-01T18:14:32Z",
  "content": [
    {"ts": "1714600012.001210", "author": "bob", "text": "Watching dashboards."},
    {"ts": "1714600025.001220", "author": "carol", "text": "Cache warming queued."},
    {"ts": "1714600040.001230", "author": "deploy-bot", "text": "Stage 1/3 complete."}
  ],
  "next_chunk_id": "thread:1714600000.001200#replies-7-12"
}
```

What to notice: chunk ids are semantic and human-readable (`#replies-1-6`), not opaque offsets; `version` matches the index's `last_modified` so the agent can detect stale chunk references; `next_chunk_id` lets the agent paginate without re-fetching the index. The agent can quote `chunk_id` back to a tool that asks "where did you read that?"

## 5. Prompt scaffold

A prompt that orchestrates posting a release announcement across multiple channels. *Demonstrates §5 prompt scaffolding.*

```json
{
  "name": "announce_release",
  "description": "Compose and post a release announcement to one or more channels, with optional thread for follow-up Q&A.",
  "when_to_use": "The user has shipped a release (version, summary, optional changelog link) and wants to announce it. Skip if the user only wants to draft text without sending.",
  "prerequisites": {
    "auth": "Slack bot token with `chat:write` and `chat:write.public` scopes.",
    "tools": ["slack_lookup_channel", "slack_send_message", "slack_pin_message"],
    "resources": ["slack://channels"],
    "ambient_state": "SLACK_DEFAULT_ANNOUNCE_CHANNEL env var, if set, is the default channel."
  },
  "arguments": [
    {"name": "version", "type": "string", "required": true},
    {"name": "summary", "type": "string", "required": true},
    {"name": "channels", "type": "array", "items": {"type": "string"}, "required": false},
    {"name": "pin", "type": "boolean", "default": false}
  ],
  "expected_followups": [
    "Call `slack_lookup_channel` for each name in `channels` to resolve to channel ids.",
    "Call `slack_send_message` per resolved channel id with the composed text.",
    "If `pin` is true, call `slack_pin_message` with each returned message ts. (Default is false — skip pinning unless explicitly requested.)",
    "Surface the resulting permalinks back to the user."
  ]
}
```

What to notice: `when_to_use` distinguishes this from "draft a message"; `prerequisites` lists the auth scope, tool names, resource URIs, and ambient state in one place; `expected_followups` names tools by their canonical schema name — the prompt references but does not redefine.

## 6. Actionable error payload

A failure response from `slack_send_message` when the channel is archived. *Demonstrates §6 failure recovery.*

```json
{
  "isError": true,
  "code": "channel_archived",
  "message": "Cannot post to archived channel.",
  "details": {
    "field": "channel_id",
    "value": "C0123ABCD",
    "reason": "Channel was archived on 2026-04-12T09:00:00Z."
  },
  "temporary": false,
  "retry_after_ms": null,
  "repair": {
    "next_step": "unarchive_then_retry",
    "tool": "slack_unarchive_channel",
    "arguments": {"channel_id": "C0123ABCD"},
    "alternative": "Choose a different `channel_id` and re-call `slack_send_message`."
  },
  "request_id": "req_01HXYZ7K3M9ABCDEF",
  "fingerprint": "slack-mcp@1.4.0+s7ab21c"
}
```

What to notice: the `code` is a stable symbolic string the agent can branch on; `details` names the offending field and its value; `temporary: false` with `retry_after_ms: null` tells the agent not to back off and try again — this isn't transient, so don't retry; `repair` points at a real tool name and argument shape — the agent's first repair attempt has everything it needs. `request_id` and `fingerprint` give the agent correlation context. Note that fields beyond `isError` — `code`, `temporary`, `retry_after_ms`, `repair`, `request_id`, `fingerprint` — are a convention extension on top of MCP's error shape; an MCP client that does not share this convention will see `isError: true` plus whatever you put in `content`. Mirror the pattern, but document the envelope your server emits.

## 7. Server capability summary

The one-shot capability summary returned at server initialization. *Demonstrates §1 server-level identity and §2 discovery primitives.*

```json
{
  "server": {
    "name": "slack-mcp",
    "version": "1.4.0",
    "fingerprint": "slack-mcp@1.4.0+s7ab21c",
    "transport": "stdio",
    "summary": "Send and read messages, manage channels and DMs, and look up users in a single Slack workspace."
  },
  "does": [
    "Post messages to channels, DMs, and threads.",
    "List, search, archive, and unarchive channels.",
    "Look up users by id, email, or display name.",
    "Read message history with cursor pagination."
  ],
  "does_not": [
    "Manage workspace settings, billing, or admin operations.",
    "Cross-workspace search or Enterprise Grid org-level operations.",
    "File uploads larger than 5MB (use Slack's web client).",
    "Real-time event subscriptions (this is a request/response server)."
  ],
  "auth": {
    "model": "slack_bot_token",
    "credential_env": "SLACK_BOT_TOKEN",
    "required_scopes": ["chat:write", "channels:read", "users:read"],
    "failure_codes": {
      "missing_credential": "SLACK_BOT_TOKEN not set",
      "invalid_credential": "token rejected by Slack auth.test",
      "insufficient_scope": "token missing one or more required scopes; see `details.required_scopes`"
    }
  },
  "ambient_state": {
    "env": ["SLACK_BOT_TOKEN", "SLACK_DEFAULT_ANNOUNCE_CHANNEL"],
    "config_files": [],
    "session_cache": "user-id and channel-id lookups cached in-process for 5 minutes"
  }
}
```

What to notice: an agent reads this once and knows the server's name, scope, negative scope, auth model with three distinct failure paths, and what ambient state matters. The transport choice (`stdio`) is declared. The fingerprint appears here too so agents can short-circuit re-discovery (see §8).

## 8. `search_tools` response shape

Response from `search_tools(query="send message")`. *Demonstrates §2 progressive disclosure.* **One valid pattern; the rule is on-demand definition loading, not this specific shape.**

```json
{
  "results": [
    {
      "name": "slack_send_message",
      "summary": "Post a message to a Slack channel or DM.",
      "namespace": "slack",
      "stability": "stable",
      "score": 0.94
    },
    {
      "name": "slack_send_ephemeral",
      "summary": "Post a message visible only to a single user in a channel.",
      "namespace": "slack",
      "stability": "stable",
      "score": 0.71
    },
    {
      "name": "slack_schedule_message",
      "summary": "Schedule a message for future delivery.",
      "namespace": "slack",
      "stability": "preview",
      "score": 0.62
    }
  ],
  "has_more": false,
  "fingerprint": "slack-mcp@1.4.0+s7ab21c",
  "load_definition_with": "describe_tool"
}
```

What to notice: only summaries come back, not full schemas; the agent calls `describe_tool` to load the definitions it actually needs. `stability` is included so the agent can filter out preview tools. `score` is the search-relevance score for the supplied query, ranked descending. The fingerprint travels with the response so a cached client can detect drift. Other valid shapes: a tool catalog endpoint, a topic-tagged tool index, a paginated `list_tools` with filtering — the rule is on-demand loading, not this exact response envelope.

## 9. Capability fingerprint with deprecation

A fingerprint snapshot showing one tool transitioning from `stable` through `deprecated` to removal. *Demonstrates §8 versioning and compatibility.*

Fingerprint at `slack-mcp@1.3.0`:

```json
{
  "fingerprint": "slack-mcp@1.3.0+a112de9",
  "covers": ["tools", "resources", "prompts", "error_codes", "summary"],
  "tools": [
    {"name": "slack_post", "stability": "stable", "schema_hash": "sha256:9c…"},
    {"name": "slack_list_channels", "stability": "stable", "schema_hash": "sha256:7a…"}
  ]
}
```

Fingerprint at `slack-mcp@1.4.0` — `slack_post` is deprecated, `slack_send_message` replaces it:

```json
{
  "fingerprint": "slack-mcp@1.4.0+s7ab21c",
  "covers": ["tools", "resources", "prompts", "error_codes", "summary"],
  "tools": [
    {
      "name": "slack_post",
      "stability": "deprecated",
      "schema_hash": "sha256:9c…",
      "deprecation": {
        "since": "1.4.0",
        "removal_at_or_after": "2.0.0",
        "replaced_by": "slack_send_message",
        "migration": "Rename `slack_post` to `slack_send_message`. Argument shape is unchanged; the new tool adds an optional `broadcast_to_channel` field."
      }
    },
    {"name": "slack_send_message", "stability": "stable", "schema_hash": "sha256:b4…"},
    {"name": "slack_list_channels", "stability": "stable", "schema_hash": "sha256:7a…"}
  ]
}
```

Fingerprint at `slack-mcp@2.0.0` — `slack_post` removed:

```json
{
  "fingerprint": "slack-mcp@2.0.0+f0e1d2c",
  "covers": ["tools", "resources", "prompts", "error_codes", "summary"],
  "tools": [
    {"name": "slack_send_message", "stability": "stable", "schema_hash": "sha256:b4…"},
    {"name": "slack_list_channels", "stability": "stable", "schema_hash": "sha256:7a…"}
  ],
  "removed_in_this_version": [
    {"name": "slack_post", "deprecated_since": "1.4.0", "replaced_by": "slack_send_message"}
  ]
}
```

What to notice: the deprecated tool stays discoverable in `1.4.0` with a stability tier change, a `replaced_by` pointer, and concrete migration text — clients that cached the old surface get a discoverable signal, not a silent break. The removal in `2.0.0` is itself recorded under `removed_in_this_version` so a client jumping `1.3.0 → 2.0.0` can still trace what happened. Every fingerprint string changes when any covered surface changes.

## 10. Worked task: API mirroring vs. task completion

The same user task — "schedule a 30-minute meeting with Alice and Bob next Tuesday afternoon and send the invite" — expressed two ways. *Demonstrates §3 tool granularity and §2 discovery impact. The failure mode of (a) is shown via transcript, not narrated.*

### (a) Endpoint-mirroring tools

Available tools (one per REST endpoint):

```json
[
  {"name": "calendar_find_availability", "summary": "Query a user's free/busy windows."},
  {"name": "calendar_create_event", "summary": "Create a calendar event with attendees."},
  {"name": "calendar_get_attendees", "summary": "List attendees on an existing event."},
  {"name": "calendar_add_attendees", "summary": "Add attendees to an existing event."},
  {"name": "calendar_send_invite", "summary": "Send an existing event's invite to its attendees."},
  {"name": "email_send", "summary": "Send an arbitrary email."},
  {"name": "email_send_template", "summary": "Send an email from a saved template."}
]
```

Agent transcript probe:

```
agent: I need to find a 30-min slot. Calling calendar_find_availability for alice@…, bob@…, Tue afternoon.
tool:  {"slots": [{"start": "2026-05-05T13:00Z", "end": "2026-05-05T13:30Z"}, ...]}

agent: Picking 13:00. Now I'll call calendar_create_event.
tool:  {"event_id": "evt_88f1", "attendees": ["alice@…", "bob@…"], "invites_sent": false}

agent: The event exists but invites_sent is false. I see calendar_send_invite and email_send_template — both look plausible for sending the invite. The names overlap. Trying email_send_template since the user asked to "send the invite."
tool:  {"isError": true, "code": "template_not_found", "message": "No template named 'invite' exists."}

agent: Retrying with email_send.
tool:  {"isError": true, "code": "missing_required_field", "details": {"field": "to"}}

agent: Re-reading docs. I think I actually wanted calendar_send_invite. Calling it now.
tool:  {"event_id": "evt_88f1", "invites_sent": true}
```

Five tool calls, two of them wrong, because `email_send` / `email_send_template` / `calendar_send_invite` collide on the same intent ("send the invite") and the agent could not disambiguate from summaries alone.

### (b) Task-completing tool

Available tool:

```json
{
  "name": "calendar_schedule_meeting",
  "summary": "Find a slot, create the event, and send invites in one call.",
  "inputSchema": {
    "type": "object",
    "required": ["attendees", "duration_minutes", "time_window", "subject"],
    "properties": {
      "attendees": {"type": "array", "items": {"type": "string", "format": "email"}},
      "duration_minutes": {"type": "integer", "minimum": 15, "maximum": 480},
      "time_window": {
        "type": "object",
        "required": ["earliest", "latest"],
        "properties": {
          "earliest": {"type": "string", "format": "date-time"},
          "latest": {"type": "string", "format": "date-time"}
        }
      },
      "subject": {"type": "string"},
      "description": {"type": "string"},
      "send_invites": {"type": "boolean", "default": true}
    }
  }
}
```

Agent transcript probe:

```
agent: Calling calendar_schedule_meeting.
tool:  {
  "event_id": "evt_88f1",
  "scheduled_at": "2026-05-05T13:00Z",
  "duration_minutes": 30,
  "attendees": ["alice@…", "bob@…"],
  "invites_sent": true,
  "permalink": "https://cal.example.com/evt_88f1"
}
```

One tool call. The agent never sees a near-name collision because the task is the unit, not the endpoint. Internal steps (find availability, create event, send invites) are hidden behind the task contract.

What to notice: (a) costs five round-trips and two failed attempts because endpoint-mirroring tools force the agent to re-invent the workflow on every task and to disambiguate near-name overlaps from summary text; (b) costs one. The same Slack server with 60 endpoint-mirror tools typically expresses 6–10 actual user tasks (see §3 anti-patterns).
