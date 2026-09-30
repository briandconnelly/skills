# gate.json recipes

One `gate.json` per surface, each copied from a fixture that `tests/test_pi_gate.py` runs against the installed Pi; `tests/test_gate_recipes.py` fails if a recipe and its fixture differ.
Put the file next to the artifact: `<name>.gate.json` beside a file, or `gate.json` inside a directory.

## Fields

- `kind`: `extension`, `package`, `skill`, `prompt`, `theme`, or `mcp-config`.
- `scope`: `temporary` (default) or `project` for an artifact under `.pi/`.
- `expect`: resources Tier 1 must find — `tools` (name, or `{name, exposure}`), `commands`, `skills`, `prompts`, `models` (`provider/id`), `mcpServers`, `flags`, `themes`, and `unobservable` (things only the TUI exercises, reported UNCHECKED).
- `tier2.prompts`: what is sent to Pi, in order; a `/name` prompt runs a command, skill, or template.
- `tier2.steps`: the faux model's scripted replies, each a `text` or a `toolCall`, optionally with `provider` and `expectTranscript` (text that must be in the transcript the model receives).
- `tier2.model` and `tier2.providers`: select a model, and add faux providers that stand in for physical ones.
- `tier2.assistantModels`: the `provider/model` that must answer each turn (default: the gate's own faux model).
- `tier2.expect`: `toolResults` (`toolName`, `isError`, `contains`, matched against the result's text) and `events` (each an object, naming at least `type`, that some RPC record must contain); `expectTranscript` matches only what Pi and the artifact sent, never a scripted reply.
- `tier2.model` must be a faux model or appear in `expect.models`; the gate refuses to select any other model, and Pi's own HTTP requests during a gate run go to a dead proxy (the artifact's code is not sandboxed).
- Tier 2 fails when it runs no model turn and declares no `toolResults` or `events`, and when a tool fails without a `toolResults` entry that expects `isError: true`.

## Extension tool

A scripted call must return the expected result.

Fixture: `tests/fixtures/gate/tool/word-count.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "tools": [
      {
        "name": "word_count",
        "exposure": "direct"
      }
    ]
  },
  "tier2": {
    "prompts": [
      "count the words in 'one two three'"
    ],
    "steps": [
      {
        "toolCall": {
          "name": "word_count",
          "arguments": {
            "text": "one two three"
          }
        }
      },
      {
        "text": "three words"
      }
    ],
    "expect": {
      "toolResults": [
        {
          "toolName": "word_count",
          "isError": false,
          "contains": "3 words"
        }
      ]
    }
  }
}
```

## Extension command

`/note` runs through RPC; its effect is a custom message event.

Fixture: `tests/fixtures/gate/command/note.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "commands": [
      "note"
    ]
  },
  "tier2": {
    "prompts": [
      "/note remember the gate"
    ],
    "expect": {
      "events": [
        {
          "type": "message_end",
          "message": {
            "customType": "note",
            "content": "note: remember the gate"
          }
        }
      ]
    }
  }
}
```

## Event hook

The hook's effect is asserted inside the faux model: `expectTranscript` must reach the transcript the model receives. A hook with no observable effect gets no Tier 2 and is reported UNCHECKED.

Fixture: `tests/fixtures/gate/hook/system-marker.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "commands": [
      "marker-status"
    ]
  },
  "tier2": {
    "prompts": [
      "hello"
    ],
    "steps": [
      {
        "expectTranscript": "SYSTEM-MARKER-7F3A",
        "text": "hi"
      }
    ]
  }
}
```

## Skill

`/skill:<name>` must expand into the model's transcript.

Fixture: `tests/fixtures/gate/skill/gate-skill/gate.json`

```json
{
  "kind": "skill",
  "expect": {
    "skills": [
      "gate-skill"
    ]
  },
  "tier2": {
    "prompts": [
      "/skill:gate-skill"
    ],
    "steps": [
      {
        "expectTranscript": "SKILL-MARKER-2C9D",
        "text": "ok"
      }
    ]
  }
}
```

## Prompt template

`/<name>` must expand into the model's transcript.

Fixture: `tests/fixtures/gate/prompt/gate-prompt.gate.json`

```json
{
  "kind": "prompt",
  "expect": {
    "prompts": [
      "gate-prompt"
    ]
  },
  "tier2": {
    "prompts": [
      "/gate-prompt"
    ],
    "steps": [
      {
        "expectTranscript": "PROMPT-MARKER-5E1B",
        "text": "ok"
      }
    ]
  }
}
```

## Project-scoped resource

`"scope": "project"` loads the artifact through discovery in a throwaway trusted project.

Fixture: `tests/fixtures/gate/project/.pi/prompts/project-prompt.gate.json`

```json
{
  "kind": "prompt",
  "scope": "project",
  "expect": {
    "prompts": [
      "project-prompt"
    ]
  },
  "tier2": {
    "prompts": [
      "/project-prompt"
    ],
    "steps": [
      {
        "expectTranscript": "PROJECT-MARKER-3D8E",
        "text": "ok"
      }
    ]
  }
}
```

## Pi package

Every contained resource must come from under the package directory; themes are checked against the installed schema.

Fixture: `tests/fixtures/gate/package/team-kit/gate.json`

```json
{
  "kind": "package",
  "expect": {
    "tools": [
      {
        "name": "word_count",
        "exposure": "direct"
      }
    ],
    "skills": [
      "kit-skill"
    ],
    "prompts": [
      "kit-prompt"
    ],
    "themes": [
      "kit-theme"
    ]
  },
  "tier2": {
    "prompts": [
      "/kit-prompt"
    ],
    "steps": [
      {
        "expectTranscript": "KIT-MARKER-9A4C",
        "text": "ok"
      }
    ]
  }
}
```

## Provider or virtual model

`tier2.providers` stands faux models in for the physical ones; `assistantModels` lists which one must answer each turn.

Fixture: `tests/fixtures/gate/virtual-model/router.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "models": [
      "router/auto"
    ]
  },
  "tier2": {
    "providers": [
      {
        "provider": "llama.cpp",
        "models": [
          "qwen"
        ]
      },
      {
        "provider": "anthropic",
        "models": [
          "claude-sonnet-4-5"
        ]
      }
    ],
    "model": "router/auto",
    "prompts": [
      "hi",
      "Please review this long request in detail, covering the design, the tests, the failure modes, the migration path, and every open question the team raised in the last planning meeting."
    ],
    "steps": [
      {
        "provider": "llama.cpp",
        "text": "short answer"
      },
      {
        "provider": "anthropic",
        "text": "long answer"
      }
    ],
    "assistantModels": [
      "llama.cpp/qwen",
      "anthropic/claude-sonnet-4-5"
    ]
  }
}
```

## Extension flag

Tier 1 only: the flag must appear in `pi --help`.

Fixture: `tests/fixtures/gate/flag/verbose.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "flags": [
      "gate-verbose"
    ]
  }
}
```

## TUI renderer or shortcut

Nothing is observable outside the TUI; `unobservable` names what the report lists as UNCHECKED.

Fixture: `tests/fixtures/gate/tui/shortcut.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "unobservable": [
      "shortcut ctrl+alt+g",
      "message renderer gate-status"
    ]
  }
}
```

## Extension-registered MCP server

Registration only; connection is UNCHECKED.

Fixture: `tests/fixtures/gate/mcp/register.gate.json`

```json
{
  "kind": "extension",
  "expect": {
    "mcpServers": [
      "gate-docs"
    ]
  }
}
```

## MCP servers in `mcp.json`

Validated by `pi mcp list` with every server disabled, so nothing connects.

Fixture: `tests/fixtures/gate/mcp-config/mcp.gate.json`

```json
{
  "kind": "mcp-config",
  "expect": {
    "mcpServers": [
      "filesystem",
      "docs"
    ]
  }
}
```

## Theme

Schema only; loading and rendering are UNCHECKED.

Fixture: `tests/fixtures/gate/theme/gate-theme.gate.json`

```json
{
  "kind": "theme",
  "expect": {
    "themes": [
      "gate-theme"
    ]
  }
}
```
