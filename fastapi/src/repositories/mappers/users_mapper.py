from typing import Dict, Any
from src.models.users import UsersOrm
from src.schemas.users import User
from src.repositories.mappers.base import DataMapper


class UsersMapper(DataMapper[UsersOrm, User]):
    """
    Маппер для преобразования UsersOrm в User и обратно.
    """
    
    @staticmethod
    def to_schema(orm_obj: UsersOrm) -> User:
        """
        Преобразовать ORM объект пользователя в Pydantic схему.
        
        Args:
            orm_obj: ORM объект пользователя
            
        Returns:
            Pydantic схема User
        """
        return User(
            id=orm_obj.id,
            email=orm_obj.email,
            hashed_password=orm_obj.hashed_password,
            first_name=orm_obj.first_name,
            last_name=orm_obj.last_name,
            telegram_id=orm_obj.telegram_id,
            pachca_id=orm_obj.pachca_id
        )
    
    @staticmethod
    def from_schema(schema_obj: User, exclude: set[str] | None = None) -> Dict[str, Any]:
        """
        Преобразовать Pydantic схему пользователя в словарь kwargs для создания ORM объекта.
        
        Args:
            schema_obj: Pydantic схема User
            exclude: Множество полей, которые нужно исключить из результата
            
        Returns:
            Словарь kwargs для создания ORM объекта
        """
        exclude = exclude or set()
        exclude.add('id')
        
        data = schema_obj.model_dump(exclude=exclude)
        return data

