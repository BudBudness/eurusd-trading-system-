from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Skill:
    name: str
    version: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"skill already registered: {skill.name}")
        self._skills[skill.name] = skill

    def run(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            skill = self._skills[name]
        except KeyError as exc:
            raise KeyError(f"unknown skill: {name}") from exc
        return skill.handler(payload)
