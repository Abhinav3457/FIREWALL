import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rule import Rule


class DetectionResult:
    def __init__(self, matched: bool, rule_name: str = "", severity: str = "low") -> None:
        self.matched = matched
        self.rule_name = rule_name
        self.severity = severity


def detect_attack(raw_data: str, db: Session) -> DetectionResult:
    rules = db.scalars(select(Rule).where(Rule.enabled == True)).all()
    for rule in rules:
        if rule.pattern and re.search(rule.pattern, raw_data):
            return DetectionResult(
                matched=True,
                rule_name=rule.name,
                severity=rule.severity,
            )
    return DetectionResult(matched=False)
