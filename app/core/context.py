from datetime import datetime
from uuid import UUID
from dataclasses import dataclass

@dataclass
class CurrentUser:
    id: UUID
    is_active: bool
    is_staff: bool
    permissions: list[str]
    role_id: UUID | None = None
    tenant_id: UUID | None = None
    verified_at: datetime | None = None