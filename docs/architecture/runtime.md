# Runtime

The runtime enforces the folder-over-agents model.

```text
Work Unit
  -> Task
  -> Skill
  -> Agent
  -> State/Event
  -> Output/Evidence
```

## Rules

1. Work units define bounded objectives.
2. Tasks define discrete work.
3. Skills are reusable capabilities and are independent of agents.
4. Agents are thin workers that invoke skills.
5. Policies are authoritative constraints.
6. State transitions are explicit and validated.
7. Events provide an audit trail.
8. Live broker execution is disabled by default.

## Execution boundary

Strategy proposes. Risk validates. Only a separately controlled execution component may submit an order. The current runtime contains no live broker connector and therefore cannot place a real order.
