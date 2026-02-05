"""
Сервис для работы с изображениями.

Содержит бизнес-логику загрузки и удаления изображений отелей.
"""

import os
from pathlib import Path

from src.exceptions.domain import EntityNotFoundError
from src.services.base import BaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Путь к папке с изображениями
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "images"


class ImagesService(BaseService):
    """
    Сервис для работы с изображениями.

    Инкапсулирует бизнес-логику:
    - Проверка существования отеля
    - Валидация файлов изображений
    - Удаление файлов с диска
    """

    async def validate_hotel_exists(self, hotel_id: int) -> None:
        """
        Проверить существование отеля.

        Args:
            hotel_id: ID отеля

        Raises:
            EntityNotFoundError: Если отель не найден
        """
        hotel = await self.hotels_repo.get_by_id(hotel_id)
        if hotel is None:
            raise EntityNotFoundError("Отель", entity_id=hotel_id)

    async def delete_image(self, image_id: int) -> bool:
        """
        Удалить изображение и все его файлы.

        Args:
            image_id: ID изображения для удаления

        Returns:
            True если изображение удалено, False если не найдено
        """
        # Проверяем существование изображения
        image = await self.images_repo.get_by_id(image_id)
        if image is None:
            return False

        # Удаляем файлы ресайзов с диска
        deleted_files = 0
        for width in [200, 500, 1000]:
            # Ищем файлы по паттерну {image_id}_{width}w_*
            pattern = f"{image_id}_{width}w_*"
            for file_path in IMAGES_DIR.glob(pattern):
                try:
                    if file_path.exists():
                        os.remove(file_path)
                        deleted_files += 1
                except Exception as e:
                    # Логируем ошибку, но продолжаем удаление
                    logger.warning(f"Не удалось удалить файл {file_path}: {e}")

        # Удаляем запись из БД
        deleted = await self.images_repo.delete(image_id)
        return deleted
