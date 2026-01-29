# Экспорт всех моделей для удобного импорта
from src.models.countries import CountriesOrm
from src.models.cities import CitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm
from src.models.images import ImagesOrm, hotels_images

__all__ = [
    "CountriesOrm",
    "CitiesOrm",
    "HotelsOrm",
    "RoomsOrm",
    "UsersOrm",
    "BookingsOrm",
    "FacilitiesOrm",
    "ImagesOrm",
    "hotels_images"
]

