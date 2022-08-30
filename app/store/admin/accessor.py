import typing

from sqlalchemy import select, insert

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):

    async def connect(self, app: "Application"):
        await super().connect(app)
        # Раскомментировать для включения создания дефолтного админа при старте приложения
        '''default_admin = await self.get_by_email(self.app.config.admin.email)
        if not default_admin:
            created = await self.create_admin(email=self.app.config.admin.email, password=self.app.config.admin.password)
            print('created:', created)'''

    async def get_by_email(self, email: str) -> typing.Optional[Admin]:
        query = select(AdminModel).where(AdminModel.email == email)
        response = await self.app.database.orm_request(query)
        result = response.scalar()
        if result:
            return Admin(id=result.id, email=result.email, password=result.password)

    async def create_admin(self, email: str, password: str) -> Admin:
        print('Creating an admin...')
        '''query = insert(AdminModel).values(email=email, password=Admin.passhash(password))  #.returning(AdminModel)
        await self.app.database.make_request(query, commit=True)
        new_admin = await self.get_by_email(email)
        return Admin(id=new_admin.id, email=email, password=new_admin.password)'''
        admin = AdminModel(email=email, password=Admin.passhash(password))
        await self.app.database.orm_add(admin)
        return Admin(id=admin.id, email=email, password=admin.password)

    async def list_admins(self) -> list:
        query = select(AdminModel)
        response = await self.app.database.orm_request(query)
        result = response.scalars()
        return [Admin(id=admin.id, email=admin.email) for admin in result]
