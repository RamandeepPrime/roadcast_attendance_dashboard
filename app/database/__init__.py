from typing import AsyncGenerator
from sqlalchemy import Engine
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, engine

from app.utils.constants import DATABASE_URL
from sqlalchemy.orm import Session, sessionmaker


AsyncEngine = create_async_engine(
	DATABASE_URL, 
	future = True, 
	pool_size = 15, 
	max_overflow = 35, 
	pool_pre_ping = True
)

class SyncSession(Session):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.db_instance = engine._get_sync_engine_or_connection(AsyncEngine)

	def get_bind(self, mapper=None, clause=None, *args, **kwargs):
		return self.db_instance


class RoutingSession(AsyncSession):

	def __init__(self, bind=None, binds=None, sync_session_class=SyncSession, **kw):
		super().__init__(bind = bind, binds = binds, sync_session_class = sync_session_class, **kw)

	async def execute(
		self,
        statement,
        params=None,
        execution_options={'synchronize_session': False},
        bind_arguments=None,
        **kw
	):
		return await super().execute(
			statement=statement,
			params=params, 
			execution_options=execution_options,
			bind_arguments=bind_arguments, 
			**kw
		)

# AsyncSessionFactory = async_sessionmaker(AsyncEngine, expire_on_commit=False)
# AsyncSessionFactory = sessionmaker(AsyncEngine, expire_on_commit=False)
SessionFactory = sessionmaker(class_ = RoutingSession, autoflush = False)

async def get_db_instance() -> AsyncGenerator[AsyncSession, None]:
	async with SessionFactory() as session:
		yield session