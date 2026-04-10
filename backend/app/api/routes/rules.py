from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.rule import Rule
from app.schemas.rule import RuleOut, RuleToggleRequest

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db), _: dict = Depends(get_current_user)) -> list[RuleOut]:
    rules = db.scalars(select(Rule).order_by(Rule.id)).all()
    return [RuleOut.from_orm(rule) for rule in rules]


@router.patch("/{rule_id}", response_model=RuleOut)
def toggle_rule(
    rule_id: int,
    payload: RuleToggleRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
) -> RuleOut:
    rule = db.scalar(select(Rule).where(Rule.id == rule_id))
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.enabled = payload.enabled
    db.commit()
    db.refresh(rule)
    return RuleOut.from_orm(rule)
