# Architecture

## Folder-over-agents model

The repository is organized around persistent folders and explicit contracts. Agents are workers; they do not own state or policy.

```text
Work Unit
  -> Tasks
  -> Skills
  -> Agents
  -> Connectors
  -> State / Events / Evidence
  -> Outputs / Audit
```

### Responsibilities

- **Work unit:** bounded objective and lifecycle.
- **Task:** discrete operation with inputs, skills, outputs and validation.
- **Skill:** reusable capability.
- **Agent:** worker that executes tasks.
- **Workflow:** controls ordering and transitions.
- **Policy:** hard constraints.
- **Schema:** machine-readable contract.
- **State:** current and historical lifecycle information.
- **Evidence:** raw observations supporting decisions.
- **Audit:** provenance of actions and decisions.
- **Observability:** runtime health and performance.

## Trading boundary

EUR/USD is the only supported instrument in the initial system. The reference broker/platform is Pepperstone + cTrader. Live execution remains disabled in the initial repository population.
