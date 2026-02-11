from typing import TypeVar, Protocol, Generic, Any, List

from internal.pkg.errors import ParamEmptyError

ID = TypeVar("ID")


class DomainEvent(Protocol):
    pass


class BaseEntity(Generic[ID]):
    def __init__(self, domain_id: ID):
        if domain_id is None:
            raise ParamEmptyError(param='domain_id')
        self._id = domain_id

    @property
    def id(self) -> ID:
        return self._id

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other.id

    def __hash__(self) -> int:
        return hash(self._id)


class BaseAggregate(BaseEntity[ID]):
    def __init__(self, domain_id: ID):
        super().__init__(domain_id)
        self._domain_events: List[DomainEvent] = []

    @property
    def domain_events(self) -> List[DomainEvent]:
        return list(self._domain_events)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def raise_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
