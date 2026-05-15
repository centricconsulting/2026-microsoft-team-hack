---
description: Design a Clean Architecture interface seam for the DCI Triage Assistant — define the interface, contract, and two concrete adapter names
argument-hint: "Describe the capability to abstract, e.g. 'AI triage classification' or 'helpdesk ticket creation'"
agent: agent
---

Design an interface seam for the DCI Triage Assistant using Clean Architecture.

Ground the design in:
- [data/glossary.md](../../data/glossary.md) — all names must come from DCI's ubiquitous language
- [.github/instructions/python.instructions.md](../instructions/python.instructions.md)
- Use `microsoftdocs/mcp/microsoft_docs_search` to look up any SDK or API patterns before designing

## Output Format

### Interface Definition
```python
# application/interfaces.py
from typing import Protocol
from triage_assistant.domain.models import HelpRequest, TriageResult

class I<Name>(Protocol):
    async def <method>(self, ...) -> <return_type>: ...
```

### Contract Rules
- What the caller can assume (pre-conditions)
- What the implementer must guarantee (post-conditions)
- What exceptions / error signals are permitted

### Concrete Adapters
Name and briefly describe two implementations:
1. **Production adapter** — real external system (e.g. `MafTriageAgent`)
2. **Test / stub adapter** — in-memory or file-based (e.g. `StubTriageAgent`)

### DI Registration Sketch
```python
# api/dependencies.py
def get_triage_agent(settings: TriageSettings = Depends(get_settings)) -> I<Name>:
    return MafTriageAgent(settings=settings, system_prompt=SYSTEM_PROMPT)
```

### Seam Justification
Confirm: _"If I can imagine two implementations, the seam is real."_ State both.

## Capability to Abstract

{{input}}
