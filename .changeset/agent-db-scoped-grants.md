---
"livekit-api": patch
"livekit-protocol": patch
---

Scope agent database access to a thread or a database: `AgentThreadGrants` gains `sql`, the new `agentDatabase` claim (`AgentDatabaseGrants`, `with_agent_database_grants`) grants `read`, `write` and `delete` on listed databases plus project-wide `create` and `list`, and `AgentGrants.database_admin` is removed.
