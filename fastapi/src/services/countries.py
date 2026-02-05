"""
Сервис для работы со странами.

Содержит бизнес-логику создания, обновления и удаления стран.
"""

from src.exceptions.domain import EntityAlreadyExistsError, EntityNotFoundError
from src.schemas.countries import SchemaCountry
from src.services.base import BaseService


class CountriesService(BaseService):
    """
    Сервис для работы со странами.

    Инкапсулирует бизнес-логику:
    - Проверка уникальности названия страны
    - Проверка уникальности ISO кода
    """

    async def create_country(self, name: str, iso_code: str) -> SchemaCountry:
        """
        Создать страну с полной валидацией.

        Args:
            name: Название страны
            iso_code: ISO код страны (2 буквы)

        Returns:
            Созданная страна (Pydantic схема)

        Raises:
            EntityAlreadyExistsError: Если страна с таким названием или ISO кодом уже существует
        """
        # Проверяем уникальность name
        existing_by_name = await self.countries_repo.get_by_name_case_insensitive(name)
        if existing_by_name is not None:
            raise EntityAlreadyExistsError("Страна", "название", name)

        # Проверяем уникальность iso_code
        existing_by_iso = await self.countries_repo.get_by_iso_code(iso_code)
        if existing_by_iso is not None:
            raise EntityAlreadyExistsError("Страна", "ISO код", iso_code.upper())

        # Создаем страну
        return await self.countries_repo.create(name=name, iso_code=iso_code.upper())

    async def update_country(self, country_id: int, name: str, iso_code: str) -> SchemaCountry:
        """
        Обновить страну с полной валидацией.

        Args:
            country_id: ID страны для обновления
            name: Новое название страны
            iso_code: Новый ISO код страны (2 буквы)

        Returns:
            Обновленная страна (Pydantic схема)

        Raises:
            EntityNotFoundError: Если страна не найдена
            EntityAlreadyExistsError: Если страна с таким названием/ISO кодом уже существует
        """
        # Проверяем существование страны
        existing_country = await self.countries_repo._get_one_by_id_exact(country_id)
        if existing_country is None:
            raise EntityNotFoundError("Страна", entity_id=country_id)

        # Проверяем уникальность name, если он изменяется
        if name != existing_country.name:
            existing_by_name = await self.countries_repo.get_by_name_case_insensitive(name)
            if existing_by_name is not None:
                raise EntityAlreadyExistsError("Страна", "название", name)

        # Проверяем уникальность iso_code, если он изменяется
        iso_code_upper = iso_code.upper()
        if iso_code_upper != existing_country.iso_code:
            existing_by_iso = await self.countries_repo.get_by_iso_code(iso_code)
            if existing_by_iso is not None:
                raise EntityAlreadyExistsError("Страна", "ISO код", iso_code_upper)

        # Обновляем страну
        updated_country = await self.countries_repo.edit(id=country_id, name=name, iso_code=iso_code_upper)

        if updated_country is None:
            raise EntityNotFoundError("Страна", entity_id=country_id)

        return updated_country

    async def partial_update_country(
        self, country_id: int, name: str | None = None, iso_code: str | None = None
    ) -> SchemaCountry:
        """
        Частично обновить страну с валидацией.

        Args:
            country_id: ID страны для обновления
            name: Новое название страны (опционально)
            iso_code: Новый ISO код страны (опционально, 2 буквы)

        Returns:
            Обновленная страна (Pydantic схема)

        Raises:
            EntityNotFoundError: Если страна не найдена
            EntityAlreadyExistsError: Если страна с таким названием/ISO кодом уже существует
        """
        # Проверяем существование страны
        existing_country = await self.countries_repo._get_one_by_id_exact(country_id)
        if existing_country is None:
            raise EntityNotFoundError("Страна", entity_id=country_id)

        from typing import Any

        update_data: dict[str, Any] = {}

        # Проверяем и добавляем name, если указан
        if name is not None:
            if name != existing_country.name:
                existing_by_name = await self.countries_repo.get_by_name_case_insensitive(name)
                if existing_by_name is not None:
                    raise EntityAlreadyExistsError("Страна", "название", name)
            update_data["name"] = name

        # Проверяем и добавляем iso_code, если указан
        if iso_code is not None:
            iso_code_upper = iso_code.upper()
            if iso_code_upper != existing_country.iso_code:
                existing_by_iso = await self.countries_repo.get_by_iso_code(iso_code)
                if existing_by_iso is not None:
                    raise EntityAlreadyExistsError("Страна", "ISO код", iso_code_upper)
            update_data["iso_code"] = iso_code_upper

        if not update_data:
            return self.countries_repo._to_schema(existing_country)

        # Обновляем страну
        updated_country = await self.countries_repo.edit(id=country_id, **update_data)

        if updated_country is None:
            raise EntityNotFoundError("Страна", entity_id=country_id)

        return updated_country
