# Plan

- [ ] Create `config/mcp-standard.json` to record the repo MCP baseline (standard version, source, evidence URLs, and owner).
- [ ] Re-scan repo configuration and source code for MCP touchpoints and dependency declarations.
- [ ] Add explicit migration notes for any MCP assets discovered (client settings, tool registration, transport handlers, or SDK usage).
- [ ] Implement protocol-alignment updates for any MCP code/config found in scope:
  - enforce 2026-07-28 request/response structure assumptions
  - update version negotiation behavior where applicable
  - adjust discovery, header routing, and auth handling for the 2026-07-28 model
- [ ] Add a Conductor checklist entry for known unsupported breaking points and unblocker items.
- [ ] Produce a concise alignment note in this track indicating what changed, what remains blocked, and why.
