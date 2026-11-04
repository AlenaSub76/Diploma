import requests
import uuid
from typing import Any
from utils.config import config


class YouGileAPI:
    """HTTP-клиент для YouGile API v2."""

    def __init__(self,
                 token: str | None = None,
                 user_id: str | None = None) -> None:
        """
        Args:
            token: Bearer-токен.
            user_id: id пользователя для создания проектов.
            Если не переданы — берутся из .env.
        """
        self.base_url: str = config.api_base_url
        self.token: str = token or config.api_token
        self.user_id: str = user_id or config.api_user_id
        self.last_created_title: str | None = None

        # Одна переиспользуемая сессия на всё время жизни клиента
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        })

    # ---------- CRUD проектов ----------
    def create_project(self, title: str | None = None) -> requests.Response:
        """Создание нового проекта.
        Если title не передан — генерируется уникальный.
        Сгенерированное название сохраняется в self.last_created_title
        (для последующей сверки в тесте).
        """
        url = f"{self.base_url}projects"
        # генерация короткой уникальной строки
        if title is None:
            title = uuid.uuid4().hex[:6]
        payload: dict[str, Any] = {
             "title": title,
             "users": {self.user_id: "admin"}}
        response = self.session.post(url, json=payload)

        # Запоминаем только при успехе
        if response.status_code == 201:
            self.last_created_title = title
        return response

    def get_project(self, project_id: str) -> requests.Response:
        """Получение проекта по ID"""
        url = f"{self.base_url}projects/{project_id}"
        return self.session.get(url)

    def change_project(self, project_id: str, title: Any) -> requests.Response:
        """Обновляет название проекта.
            title: Any — в негативном тесте намеренно передаём int, а не str,
            чтобы проверить реакцию API на неверный тип.
            Any в аннотации означает: «здесь может быть значение любого типа,
            клиент не проверяет его»"""
        url = f"{self.base_url}projects/{project_id}"
        return self.session.put(url, json={"title": title})

    def delete_project(self, project_id: str) -> requests.Response:
        """Мягкое удаление проекта (deleted=True)."""
        url = f"{self.base_url}projects/{project_id}"
        return self.session.put(url, json={"deleted": True})

    def get_all_projects(self) -> requests.Response:
        """Возвращает полный список проектов."""
        url = f"{self.base_url}projects"
        return self.session.get(url)
