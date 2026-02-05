"""
Базовый класс для всех сервисов.

Предоставляет общую функциональность для работы с репозиториями и транзакциями.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.bookings import BookingsRepository
from src.repositories.cities import CitiesRepository
from src.repositories.countries import CountriesRepository
from src.repositories.facilities import FacilitiesRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.images import ImagesRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository
from src.utils.db_manager import DBManager


class BaseService:
    """
    Базовый класс для всех сервисов.

    Предоставляет доступ к репозиториям через DBManager
    и общие методы для работы с транзакциями.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация сервиса.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    @property
    def hotels_repo(self) -> HotelsRepository:
        """Получить репозиторий отелей."""
        return DBManager.get_hotels_repository(self.session)

    @property
    def rooms_repo(self) -> RoomsRepository:
        """Получить репозиторий номеров."""
        return DBManager.get_rooms_repository(self.session)

    @property
    def bookings_repo(self) -> BookingsRepository:
        """Получить репозиторий бронирований."""
        return DBManager.get_bookings_repository(self.session)

    @property
    def users_repo(self) -> UsersRepository:
        """Получить репозиторий пользователей."""
        return DBManager.get_users_repository(self.session)

    @property
    def countries_repo(self) -> CountriesRepository:
        """Получить репозиторий стран."""
        return DBManager.get_countries_repository(self.session)

    @property
    def cities_repo(self) -> CitiesRepository:
        """Получить репозиторий городов."""
        return DBManager.get_cities_repository(self.session)

    @property
    def facilities_repo(self) -> FacilitiesRepository:
        """Получить репозиторий удобств."""
        return DBManager.get_facilities_repository(self.session)

    @property
    def images_repo(self) -> ImagesRepository:
        """Получить репозиторий изображений."""
        return DBManager.get_images_repository(self.session)
