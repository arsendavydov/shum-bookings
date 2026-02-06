from locust import HttpUser, between, task


class ApiUser(HttpUser):
    """
    Базовый пользователь для нагрузочного тестирования API.

    По умолчанию использует BASE_URL, который задается самим Locust.
    """

    wait_time = between(0.5, 2.0)

    @task(3)
    def health(self) -> None:
        self.client.get("/health")

    @task(5)
    def list_hotels(self) -> None:
        self.client.get("/hotels?page=1&per_page=20")

    @task(2)
    def list_rooms_for_hotel(self) -> None:
        """
        Запрашивает список номеров для одного из существующих отелей.

        1. Получаем первую страницу отелей.
        2. Берем id первого отеля.
        3. Запрашиваем /rooms для этого отеля с пагинацией.
        """
        hotels_resp = self.client.get("/hotels?page=1&per_page=1")
        if hotels_resp.status_code != 200:
            return

        try:
            hotels = hotels_resp.json()
        except Exception:
            return

        if not hotels:
            return

        hotel_id = hotels[0].get("id")
        if not hotel_id:
            return

        self.client.get(f"/rooms?hotel_id={hotel_id}&page=1&per_page=20")

    @task(1)
    def metrics(self) -> None:
        self.client.get("/metrics")


