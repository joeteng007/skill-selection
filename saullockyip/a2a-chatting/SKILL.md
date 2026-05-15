---
name: A2A Chatting
description: Chat with other OpenClaw agents via the a2a-chatting.sh CLI. Use when: (1) User asks you to talk to another agent, (2) You need to query another agent's capabilities or get information from them, (3) You need to coordinate with another agent, (4) User wants agent-to-agent communication.
version: 0.2.1
---

# A2A Chatting

Chat with other OpenClaw agents using the `a2a-chatting.sh` CLI.

## Prerequisites

Before using, configure the OpenClaw directory:
```bash
a2a-chatting.sh config <openclaw_dir>
# Example: a2a-chatting.sh config /Users/roco/.openclaw
```

## Commands

| Command | Description |
|---------|-------------|
| `config <path> [--force]` | Configure OpenClaw directory. Use `--force` to overwrite existing config. |
| `get-agents` | List all available agents with their IDs and workspaces. |
| `new-session <agent_id> <topic>` | Create a new session with an agent. Returns a session ID. |
| `message <session_id> <message>` | Send a message to an existing session. Supports multi-turn conversations. |
| `list-sessions` | List all sessions with their IDs, agents, topics, and creation dates. |
| `get-session <session_id>` | Show the full conversation history of a session. |
| `delete-session <session_id>` | Delete a session and its conversation history. |

## Workflow

### First Time Setup
```bash
a2a-chatting.sh config /path/to/openclaw
a2a-chatting.sh get-agents  # Find the agent ID you want to chat with
```

### Start a New Conversation
```bash
# Create a new session with a topic
a2a-chatting.sh new-session <agent_id> "Discuss project structure"

# The command returns a session_id. Use it for subsequent messages.
```

### Continue a Conversation
```bash
# Send messages to the same session (multi-turn chat)
a2a-chatting.sh message <session_id> "Can you elaborate on that?"

# View the conversation so far
a2a-chatting.sh get-session <session_id>
```

### Manage Sessions
```bash
# See all your A2A sessions
a2a-chatting.sh list-sessions

# Resume a previous conversation
a2a-chatting.sh get-session <session_id>  # Review context
a2a-chatting.sh message <session_id> "Let's continue from before..."

# Delete old sessions
a2a-chatting.sh delete-session <session_id>
```

## Storage

Sessions are stored in `<openclaw_dir>/a2a-sessions/`:
- `sessions.jsonl` — Index of all sessions (sessionId, agentId, topic, createdAt)
- `<session_id>.jsonl` — Individual session conversations (timestamp, toMessage, incomingMessage)

## Tips

- **Session Reuse**: Unlike the old single-shot approach, you can send multiple messages to the same session. The agent maintains context.
- **Topic Naming**: Use descriptive topics so you can find sessions later with `list-sessions`.
- **Session Recovery**: If OpenClaw restarts, sessions remain in the JSONL files. Use `list-sessions` to find them.
- **Resume Old Chats**: Use `get-session` to review context before continuing with `message`.
