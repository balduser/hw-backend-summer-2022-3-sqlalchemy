from aiohttp.test_utils import TestClient

from app.store import Store
from app.web.config import Config


class TestAdmin:
    async def test_delete_admins(self, cli: TestClient, config: Config, store: Store):
        """Проверка метода delete_admins()"""
        admin = await store.admins.get_by_email(config.admin.email)
        assert admin
        await store.admins.delete_admins()
        admin = await store.admins.get_by_email(config.admin.email)
        assert not admin

    async def test_wrong_password(self, cli: TestClient, config: Config):
        """Среди имевшихся тестов не была реализована проверка логина с правильным email"""
        resp = await cli.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password + '!',
            },
        )
        assert resp.status == 403
        data = await resp.json()
        assert data["status"] == "forbidden"
