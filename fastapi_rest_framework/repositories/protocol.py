import collections.abc
import typing

SelectStatementT = typing.TypeVar(
    "SelectStatementT",
    bound=typing.Any,
)
WhereFilterT = typing.TypeVar(
    "WhereFilterT",
    bound=typing.Any,
)
OrderingClauseT = typing.TypeVar(
    "OrderingClauseT",
    bound=typing.Any,
)
AnnotationT = typing.TypeVar(
    "AnnotationT",
    bound=typing.Any,
)
LazyLoadedT = typing.TypeVar(
    "LazyLoadedT",
    bound=typing.Any,
)


class APIModel(typing.Protocol):
    """Protocol for connecting api and data model."""

    pk_field: str


APIModelT = typing.TypeVar(
    "APIModelT",
    bound=APIModel,
)


class ApiRepositoryProtocol(  # type: ignore
    typing.Protocol[
        APIModelT,
        SelectStatementT,
        WhereFilterT,
        OrderingClauseT,
        AnnotationT,
        LazyLoadedT,
    ],
):
    """Protocol for connecting api and data source."""

    model: type[APIModel]

    def init_other(
        self,
        repository_class: type["ApiRepositoryProtocolT"],
    ) -> "ApiRepositoryProtocolT":
        """Init other repo from current."""
        ...

    def expire(self, instance: APIModelT) -> None:
        """Expire instance."""

    async def save(
        self,
        instance: APIModelT,
        refresh: bool = False,
        attribute_names: collections.abc.Sequence[str] | None = None,
    ) -> APIModelT:
        """Save model instance."""
        ...

    async def delete(self, instance: APIModelT) -> None:
        """Delete model instance."""

    async def insert_batch(
        self,
        objects: collections.abc.Sequence[APIModelT],
        exclude_fields: collections.abc.Sequence[str] = (),
    ) -> list[APIModelT]:
        """Create batch of objects."""
        ...

    async def update_batch(
        self,
        objects: collections.abc.Sequence[APIModelT],
        exclude_fields: collections.abc.Sequence[str] = (),
    ) -> None:
        """Update batch of objects."""

    def get_fetch_statement(
        self,
        statement: SelectStatementT | None = None,
        unique: bool = True,
        offset: int | None = None,
        limit: int | None = None,
        joined_load: collections.abc.Sequence[LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[LazyLoadedT] = (),
        annotations: collections.abc.Sequence[AnnotationT] = (),
        ordering_clauses: collections.abc.Sequence[OrderingClauseT] = (),
        where: collections.abc.Sequence[WhereFilterT] = (),
        **filters_by: typing.Any,
    ) -> SelectStatementT:
        """Prepare statement for fetching."""
        ...

    async def fetch_all(
        self,
        statement: SelectStatementT | None = None,
        unique: bool = True,
        offset: int | None = None,
        limit: int | None = None,
        joined_load: collections.abc.Sequence[LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[LazyLoadedT] = (),
        annotations: collections.abc.Sequence[AnnotationT] = (),
        ordering_clauses: collections.abc.Sequence[OrderingClauseT] = (),
        where: collections.abc.Sequence[WhereFilterT] = (),
        **filters_by: typing.Any,
    ) -> collections.abc.Sequence[APIModelT]:
        """Fetch entries."""
        ...

    async def fetch_first(
        self,
        statement: SelectStatementT | None = None,
        unique: bool = True,
        offset: int | None = None,
        limit: int | None = None,
        joined_load: collections.abc.Sequence[LazyLoadedT] = (),
        select_in_load: collections.abc.Sequence[LazyLoadedT] = (),
        annotations: collections.abc.Sequence[AnnotationT] = (),
        ordering_clauses: collections.abc.Sequence[OrderingClauseT] = (),
        where: collections.abc.Sequence[WhereFilterT] = (),
        **filters_by: typing.Any,
    ) -> APIModelT | None:
        """Fetch first matching entry."""
        ...

    async def count(
        self,
        where: collections.abc.Sequence[WhereFilterT] = (),
        **filters_by: typing.Any,
    ) -> int:
        """Get count of entries."""
        ...

    async def exists(
        self,
        where: collections.abc.Sequence[WhereFilterT] = (),
        **filters_by: typing.Any,
    ) -> bool:
        """Check existence of entries."""
        ...


AnyApiRepositoryProtocol = ApiRepositoryProtocol[
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
]
ApiRepositoryProtocolT = typing.TypeVar(
    "ApiRepositoryProtocolT",
    bound=AnyApiRepositoryProtocol,
)
