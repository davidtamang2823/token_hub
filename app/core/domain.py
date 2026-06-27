from pydantic import BaseModel

# core/domain.py
from pydantic import BaseModel, ConfigDict, Field
from core.events import BaseEvent


class DomainModel(BaseModel):
    """Base for all domain models — no event tracking.
    Use for value objects, read models, or anything that
    doesn't independently raise domain events."""
    model_config = ConfigDict(str_strip_whitespace=True)


class AggregateRoot(DomainModel):
    """Base for aggregate roots / entities that raise domain events."""
    events: list[BaseEvent] = Field(default_factory=list)

    def pull_events(self) -> list[BaseEvent]:
        events, self.events = self.events, []
        return events