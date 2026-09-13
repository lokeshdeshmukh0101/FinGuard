from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.domain import AuditLog, User, UserRole
from app.schemas.domain import AuditLogResponse
from app.api.deps import require_roles

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    action_filter: Optional[str] = Query(None, alias="action"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ANALYST, UserRole.ADMIN]))
):
    """
    Query audit trail entries (Analyst and Admin access only).
    """
    query = db.query(AuditLog)
    if action_filter:
        query = query.filter(AuditLog.action == action_filter.upper())

    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return logs
