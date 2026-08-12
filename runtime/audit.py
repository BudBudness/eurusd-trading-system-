from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json

@dataclass(frozen=True)
class AuditEvent:
    event: str
    timestamp: str
    payload: dict

class AuditLog:
    def __init__(self): self.events=[]
    def record(self, event: str, payload: dict):
        self.events.append(AuditEvent(event, datetime.now(timezone.utc).isoformat(), payload))
    def export_json(self) -> str:
        return json.dumps([asdict(e) for e in self.events], indent=2)
