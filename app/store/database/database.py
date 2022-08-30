from typing import Optional, TYPE_CHECKING

from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    @property
    def url(self) -> str:
        db_keys = self.app.config.database
        return f'postgresql+asyncpg://{db_keys.user}:{db_keys.password}@{db_keys.host}/{db_keys.database}'

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(self.url, future=True)
        self.session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()

    async def orm_request(self, query, commit: bool = False) -> ChunkedIteratorResult:
        async with self.session() as session:
            result: ChunkedIteratorResult = await session.execute(query)
            if commit:
                await session.commit()
            return result

    async def orm_add(self, obj: db):
        async with self.session() as session:
            session.add(obj)
            await session.commit()
