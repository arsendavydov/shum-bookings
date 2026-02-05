"""
Сервис для работы с пользователями.

Содержит бизнес-логику создания, обновления и удаления пользователей.
"""

from typing import Any

from src.exceptions.domain import EntityAlreadyExistsError, EntityNotFoundError
from src.schemas.users import SchemaUser, UserRegister
from src.services.base import BaseService


class UsersService(BaseService):
    """
    Сервис для работы с пользователями.

    Инкапсулирует бизнес-логику:
    - Проверка уникальности email
    - Обновление пользователей
    """

    async def register_user(self, user_data: UserRegister) -> SchemaUser:
        """
        Зарегистрировать нового пользователя.

        Args:
            user_data: Данные пользователя (с захешированным паролем)

        Returns:
            Созданный пользователь (Pydantic схема)

        Raises:
            EntityAlreadyExistsError: Если пользователь с таким email уже существует
        """
        # Проверяем уникальность email
        if await self.users_repo.exists_by_email(user_data.email):
            raise EntityAlreadyExistsError("Пользователь", "email", user_data.email)

        # Создаем пользователя
        user_dict = user_data.model_dump(exclude_none=True)
        return await self.users_repo.create(**user_dict)

    async def update_user(self, user_id: int, user_data: UserRegister) -> SchemaUser:
        """
        Полностью обновить пользователя.

        Args:
            user_id: ID пользователя для обновления
            user_data: Данные для обновления

        Returns:
            Обновленный пользователь (Pydantic схема)

        Raises:
            EntityNotFoundError: Если пользователь не найден
            EntityAlreadyExistsError: Если email уже занят
        """
        # Проверяем существование пользователя
        existing_user = await self.users_repo.get_by_id(user_id)
        if existing_user is None:
            raise EntityNotFoundError("Пользователь", entity_id=user_id)

        # Проверяем уникальность email, если он изменяется
        user_dict = user_data.model_dump(exclude_none=True)
        if "email" in user_dict and user_dict["email"] != existing_user.email:
            if await self.users_repo.exists_by_email(user_dict["email"]):
                raise EntityAlreadyExistsError("Пользователь", "email", user_dict["email"])

        # Обновляем пользователя
        updated_user = await self.users_repo.edit(id=user_id, **user_dict)
        if updated_user is None:
            raise EntityNotFoundError("Пользователь", entity_id=user_id)

        return updated_user

    async def partial_update_user(self, user_id: int, user_data: dict[str, Any]) -> SchemaUser:
        """
        Частично обновить пользователя.

        Args:
            user_id: ID пользователя для обновления
            user_data: Данные для обновления (только изменяемые поля)

        Returns:
            Обновленный пользователь (Pydantic схема)

        Raises:
            EntityNotFoundError: Если пользователь не найден
            EntityAlreadyExistsError: Если email уже занят
        """
        # Проверяем существование пользователя
        existing_user = await self.users_repo.get_by_id(user_id)
        if existing_user is None:
            raise EntityNotFoundError("Пользователь", entity_id=user_id)

        # Проверяем уникальность email, если он изменяется
        if "email" in user_data and user_data["email"] != existing_user.email:
            if await self.users_repo.exists_by_email(user_data["email"]):
                raise EntityAlreadyExistsError("Пользователь", "email", user_data["email"])

        # Обновляем пользователя
        updated_user = await self.users_repo.update(id=user_id, **user_data)
        if updated_user is None:
            raise EntityNotFoundError("Пользователь", entity_id=user_id)

        return updated_user

    async def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя.

        Args:
            user_id: ID пользователя для удаления

        Returns:
            True если пользователь удален, False если не найден
        """
        deleted = await self.users_repo.delete(user_id)
        return deleted
