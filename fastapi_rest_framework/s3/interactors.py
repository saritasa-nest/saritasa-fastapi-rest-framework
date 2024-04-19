import asyncio
import typing
import urllib.parse

from .. import common_types, interactors, repositories, validators
from . import context_mixins


class S3InteractorMixin(
    context_mixins.S3ContextMixin,
    interactors.BaseHooksMixin[repositories.APIModelT],
    typing.Generic[repositories.APIModelT],
):
    """Add logic related to s3 fields.

    Move files from upload folder on create/update.
    Delete files on delete.

    """

    upload_folder: str
    s3_files_fields: tuple[str, ...]

    async def _post_create_hook(
        self,
        instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Update file urls."""
        for field_name in self.s3_files_fields:
            instance = await self._move_file_for_field(
                instance=instance,
                data=data,
                context=context,
                field_name=field_name,
            )
        return await super()._post_create_hook(instance, data, context)

    async def _post_update_hook(
        self,
        instance: repositories.APIModelT,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Update file urls."""
        for field_name in self.s3_files_fields:
            instance = await self._move_file_for_field(
                instance=instance,
                data=data,
                context=context,
                field_name=field_name,
            )
        return await super()._post_update_hook(instance, data, context)

    async def _post_delete_hook(
        self,
        deleted_instance: repositories.APIModelT,
        context: common_types.ContextType,
    ) -> None:
        """Delete files from s3 for deleted instance."""
        for field_name in self.s3_files_fields:
            await self.delete_files_for_field(
                instance=deleted_instance,
                context=context,
                field_name=field_name,
            )
        await super()._post_delete_hook(deleted_instance, context)

    async def _copy_file_from_temp_folder(
        self,
        temp_file_url: str,
        context: common_types.ContextType,
    ) -> str:
        """Copy file from upload folder."""
        if not temp_file_url.startswith(self.upload_folder):
            return temp_file_url
        s3_client = self.get_s3_client_from_context(context)
        url_to_copy_file: str = (
            urllib.parse.unquote_plus(temp_file_url)
            .replace(f"{self.upload_folder}", "")
            .lstrip("/")
        )
        await s3_client.async_copy_object(
            key=url_to_copy_file,
            source_key=temp_file_url,
        )
        return url_to_copy_file

    async def _move_file_for_field(
        self,
        instance: repositories.APIModelT,
        field_name: str,
        data: validators.ApiDataType,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Move file data from upload folder to private folder."""
        field_value: str | list[str] = data.get(field_name, None)
        if not field_value:
            return instance

        if isinstance(field_value, str):
            setattr(
                instance,
                field_name,
                await self._copy_file_from_temp_folder(
                    temp_file_url=field_value,
                    context=context,
                ),
            )
            return instance
        new_values = await asyncio.gather(
            *[
                self._copy_file_from_temp_folder(
                    temp_file_url=field_value_item,
                    context=context,
                )
                for field_value_item in field_value
            ],
        )
        setattr(instance, field_name, new_values)
        return instance

    async def delete_files_for_field(
        self,
        instance: repositories.APIModelT,
        field_name: str,
        context: common_types.ContextType,
    ) -> repositories.APIModelT:
        """Delete files from s3 for deleted instance."""
        value = getattr(instance, field_name)
        field_value: list[str] = value if isinstance(value, list) else [value]

        await asyncio.gather(
            *[
                self._delete_file(
                    file_url=file_url,
                    context=context,
                )
                for file_url in field_value
            ],
        )
        return instance

    async def _delete_file(
        self,
        file_url: str,
        context: common_types.ContextType,
    ) -> None:
        """Delete file from s3."""
        s3_client = self.get_s3_client_from_context(context)
        if file_url:
            await s3_client.async_delete_object(key=file_url)
