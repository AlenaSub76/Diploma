from dotenv import dotenv_values

# Читаем .env один раз при импорте модуля — возвращает словарь {ключ: значение}
env: dict[str, str | None] = dotenv_values(".env")


def _get(key: str, default: str = "") -> str:
    """Возвращает значение из .env или default, если ключа нет/он пуст."""
    value = env.get(key)
    return value if value else default


#  только для headless: если не используется - в .env -> HEADLESS=False
def _get_bool(key: str, default: bool = False) -> bool:
    """Приводит строку из .env к bool: '1', 'true', 'yes', 'on' → True."""
    value = env.get(key)
    if value is None or value == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Config:
    """
    Типизированный снимок настроек из .env.
    Значения доступны только для чтения : не менять после создания.
    """

    def __init__(self) -> None:
        # ---------- URLs ----------
        self.base_url: str = _get("BASE_URL", "https://ru.yougile.com/")
        self.login_url: str = _get("LOGIN_URL", self.base_url + "team/")
        self.settings_url: str = _get(
            "SETTINGS_URL", self.base_url + "team/settings-account")
        self.projects_url: str = _get(
            "PROJECTS_URL", self.base_url + "team/projects")
        self.project_url: str = _get("PROJECT_URL")
        self.api_base_url: str = _get("API_BASE_URL")

        # ---------- Учётные данные ----------
        self.user_email: str = _get("USER_EMAIL")
        self.user_password: str = _get("USER_PASSWORD")
        self.user_name: str = _get("USER_NAME")

        # ---------- API ----------
        self.api_token: str = _get("YOUGILE_TOKEN")
        self.api_user_id: str = _get("YOUGILE_USER_ID")

        # ---------- UI ----------
        self.browser: str = _get("BROWSER", "chrome").lower()
        self.headless: bool = _get_bool("HEADLESS", True)

        # -----Тестовые данные--------
        self.invite_email: str = _get("INVITE_EMAIL", "user1@mail.ru")
        self.assignee_name: str = _get("ASSIGNEE_NAME", "")


config = Config()
