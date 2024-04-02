import collections.abc
import dataclasses
import typing

from .. import common_types, permissions, repositories, validators


class BaseHooksMixin(typing.Generic[repositories.APIModelT]):
    """Mixin to add hooks logic."""

    async def _pre_create_hook(
        self,
        not_saved_instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Run pre-create logic.

        Runs before instance creation.

        """
        return not_saved_instance

    async def _post_create_hook(
        self,
        instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Run post-create logic.

        Runs after instance creation and reload from db.

        """
        return instance

    async def _pre_update_hook(
        self,
        instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Run pre-update logic.

        Runs before instance update.

        """
        return instance

    async def _post_update_hook(
        self,
        instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Run post-update logic.

        Runs after instance update and reload from db.

        """
        return instance

    async def _pre_delete_hook(
        self,
        instance: repositories.APIModelT,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Run pre-delete logic.

        Runs before instance deletion.

        """
        return instance

    async def _post_delete_hook(
        self,
        deleted_instance: repositories.APIModelT,
        context: common_types.ContextType,
    ) -> None:
        """Run post-delete logic.

        Runs after instance deletion.

        """


@dataclasses.dataclass
class M2MCreateUpdateConfig:
    """Configuration for m2m creating updating m2m fields."""

    m2m_repository_class: type[repositories.AnyApiRepositoryProtocol]
    m2m_repository_model: type[repositories.APIModel] | None
    instance_m2m_field: str
    link_field: str
    instance_m2m_relationship_field: str
    instance_m2m_relationship_pk_field: str
    m2m_interactor_class: type["AnyApiDataInteractor"] | None = None


class ApiDataInteractor(
    BaseHooksMixin[repositories.APIModelT],
    typing.Generic[
        permissions.UserT,
        repositories.SelectStatementT,
        repositories.ApiRepositoryProtocolT,
        repositories.APIModelT,
    ],
):
    """Interact with api data (create, update, delete from db)."""

    model: type[repositories.APIModelT]
    m2m_create_update_config: typing.ClassVar[
        dict[str, M2MCreateUpdateConfig]
    ] = {}

    def __init__(
        self,
        repository: repositories.ApiRepositoryProtocolT,
        user: permissions.UserT,
        instance: repositories.APIModelT | None = None,
    ) -> None:
        self.repository = repository
        self.instance = instance
        self.user = user

    def init_other(
        self,
        interactor_class: type["ApiDataInteractorT"],
        repository_class: type[repositories.AnyApiRepositoryProtocol],
    ) -> "ApiDataInteractorT":
        """Init other data interactor from current."""
        other_repository = self.repository.init_other(
            repository_class=repository_class,
        )
        return interactor_class(
            repository=other_repository,
            user=self.user,
        )

    def _prepare_instance_from_api(
        self,
        data: validators.ApiDataType,
    ) -> repositories.APIModelT:
        """Prepare instance from API."""
        if self.instance:
            for field, value in data.items():
                setattr(self.instance, field, value)
            return self.instance
        else:
            return self.repository.model(**data)  # type: ignore

    async def _prepare_instance_create(
        self,
        instance: repositories.APIModelT,
    ) -> repositories.APIModelT:
        """Perform extra logic before creating object."""
        return instance

    async def _prepare_instance_update(
        self,
        instance: repositories.APIModelT,
    ) -> repositories.APIModelT:
        """Perform extra logic before updating object."""
        return instance

    async def _reload_instance(
        self,
        instance: repositories.APIModelT,
        reload_fetch_statement: repositories.SelectStatementT | None = None,
    ) -> repositories.APIModelT | None:
        """Reload instance from database."""
        pk_field_to_value = {
            self.model.pk_field: getattr(instance, self.model.pk_field),
        }
        self.repository.expire(instance)
        return await self.repository.fetch_first(
            statement=reload_fetch_statement,
            **pk_field_to_value,
        )

    async def save(
        self,
        data: validators.ApiDataType,
        context: common_types.ContextType,
        refresh: bool = False,
        reload_fetch_statement: repositories.SelectStatementT | None = None,
    ) -> repositories.APIModelT | None:
        """Save instance from api data into database."""
        is_update = getattr(self.instance, self.model.pk_field, None)

        if is_update:
            saved_instance = await self.update(
                data=data,
                context=context,
                refresh=refresh,
            )
        else:
            saved_instance = await self.create(
                data=data,
                context=context,
                refresh=refresh,
            )
        reloaded_instance = await self._reload_instance(
            instance=saved_instance,
            reload_fetch_statement=reload_fetch_statement,
        )
        if not reloaded_instance:
            return reloaded_instance
        if is_update:
            await self._post_update_hook(
                instance=reloaded_instance,
                data=data,
                context=context,
            )
        else:
            await self._post_create_hook(
                instance=reloaded_instance,
                data=data,
                context=context,
            )
        return reloaded_instance

    async def create(
        self,
        data: validators.ApiDataType,
        context: common_types.ContextType,
        refresh: bool = False,
    ) -> repositories.APIModelT:
        """Create instance from api data."""
        m2m_data = []
        for field, m2m_config in self.m2m_create_update_config.items():
            if field not in data:
                continue
            m2m_data.append((m2m_config, data.pop(field)))
        instance = self._prepare_instance_from_api(data=data)
        instance = await self._prepare_instance_create(instance=instance)
        await self._pre_create_hook(
            not_saved_instance=instance,
            data=data,
            context=context,
        )
        await self._save_object_in_db(
            instance=instance,
            refresh=refresh,
        )
        for m2m_config, values in m2m_data:
            await self.create_m2m(
                instance=instance,
                m2m_config=m2m_config,
                link_values=values,
                context=context,
            )
        return instance

    async def update(
        self,
        data: validators.ApiDataType,
        context: common_types.ContextType,
        refresh: bool = False,
    ) -> repositories.APIModelT:
        """Update instance from api data."""
        m2m_data = []
        for field, m2m_config in self.m2m_create_update_config.items():
            if field not in data:
                continue
            m2m_data.append((m2m_config, data.pop(field)))
        instance = self._prepare_instance_from_api(data=data)
        instance = await self._prepare_instance_update(instance=instance)
        await self._pre_update_hook(
            instance=instance,
            data=data,
            context=context,
        )
        await self._save_object_in_db(
            instance=instance,
            refresh=refresh,
        )
        for m2m_config, values in m2m_data:
            await self.update_m2m(
                instance=instance,
                m2m_config=m2m_config,
                link_values=values,
                context=context,
            )
        return instance

    async def delete(
        self,
        instance: repositories.APIModelT,
        context: common_types.ContextType,
    ) -> None:
        """Delete instance from db."""
        instance = await self._pre_delete_hook(
            instance=instance,
            context=context,
        )
        await self.repository.delete(instance=instance)
        await self._post_delete_hook(
            deleted_instance=instance,
            context=context,
        )

    async def create_batch(
        self,
        data: collections.abc.Sequence[validators.ApiDataType],
        context: common_types.ContextType,
    ) -> list[repositories.APIModelT]:
        """Perform bulk create."""
        return await self._create_batch_in_db(
            objects=tuple(map(self._prepare_instance_from_api, data)),
        )

    async def update_batch(
        self,
        data: collections.abc.Sequence[validators.ApiDataType],
        context: common_types.ContextType,
    ) -> None:
        """Perform bulk update."""
        await self._update_batch_in_db(
            objects=tuple(map(self._prepare_instance_from_api, data)),
        )

    async def _save_object_in_db(
        self,
        instance: repositories.APIModelT,
        refresh: bool = False,
    ) -> repositories.APIModelT:
        """Save instance into database."""
        await self.repository.save(instance=instance, refresh=refresh)
        return instance

    async def _create_batch_in_db(
        self,
        objects: collections.abc.Sequence[repositories.APIModelT],
    ) -> list[repositories.APIModelT]:
        """Create batch of objects into database."""
        return await self.repository.insert_batch(objects=objects)

    async def _update_batch_in_db(
        self,
        objects: collections.abc.Sequence[repositories.APIModelT],
    ) -> None:
        """Update batch of objects into database."""
        await self.repository.update_batch(objects)

    def _init_m2m_interactor(
        self,
        m2m_config: M2MCreateUpdateConfig,
    ) -> "AnyApiDataInteractor":
        """Init data interactor for m2m operations."""
        if m2m_config.m2m_interactor_class:
            return self.init_other(
                interactor_class=m2m_config.m2m_interactor_class,
                repository_class=m2m_config.m2m_repository_class,
            )
        elif not m2m_config.m2m_repository_model:
            raise ValueError(  # pragma: no cover
                "m2m_repository_model or m2m_interactor_class"
                "must be specified in m2m config.",
            )
        else:
            return self.init_other(
                interactor_class=ApiDataInteractor[
                    permissions.UserT,
                    repositories.SelectStatementT,
                    m2m_config.m2m_repository_class,  # type: ignore
                    m2m_config.m2m_repository_model,  # type: ignore
                ],
                repository_class=m2m_config.m2m_repository_class,
            )

    async def create_m2m(
        self,
        instance: repositories.APIModelT,
        m2m_config: M2MCreateUpdateConfig,
        link_values: list[str | int],
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Create m2m connection for new instance."""
        interactor = self._init_m2m_interactor(m2m_config=m2m_config)
        # Create m2m links
        await interactor.create_batch(
            data=[
                {
                    m2m_config.instance_m2m_field: getattr(
                        instance,
                        instance.pk_field,
                    ),
                    m2m_config.link_field: link_field_value,
                }
                for link_field_value in set(link_values)
            ],
            context=context,
        )
        return instance

    async def update_m2m(
        self,
        instance: repositories.APIModelT,
        m2m_config: M2MCreateUpdateConfig,
        link_values: list[str | int],
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Update m2m connection for updated instance."""
        interactor = self._init_m2m_interactor(m2m_config=m2m_config)
        if not self.instance:
            raise ValueError(  # pragma: no cover
                "Instance is `None` in update action",
            )
        ids_from_db = {
            getattr(supervisor, m2m_config.instance_m2m_relationship_pk_field)
            for supervisor in getattr(
                self.instance,
                m2m_config.instance_m2m_relationship_field,
            )
        }
        # Delete m2m links that are not present in request
        await interactor.repository.delete_batch(
            where=[
                getattr(
                    interactor.repository.model,
                    m2m_config.link_field,
                ).in_(
                    ids_from_db - set(link_values),
                ),
            ],
            **{
                m2m_config.instance_m2m_field: getattr(
                    instance,
                    instance.pk_field,
                ),
            },
        )
        # Create m2m links that are not in db, but in requests
        await interactor.create_batch(
            data=[
                {
                    m2m_config.instance_m2m_field: getattr(
                        instance,
                        instance.pk_field,
                    ),
                    m2m_config.link_field: link_field_value,
                }
                for link_field_value in set(link_values) - ids_from_db
            ],
            context=context,
        )
        return instance


AnyApiDataInteractor = ApiDataInteractor[
    typing.Any,
    typing.Any,
    typing.Any,
    typing.Any,
]
ApiDataInteractorT = typing.TypeVar(
    "ApiDataInteractorT",
    bound=AnyApiDataInteractor,
)
