from dataclasses import dataclass
from typing import Any
from .skills import SkillRegistry


@dataclass
class Agent:
    name: str
    skills: SkillRegistry

    def execute(self, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.skills.run(skill, payload)
