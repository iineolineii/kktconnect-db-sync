from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..strings import normalize_cyrillic
from .models import Employee, User

T = TypeVar("T", bound=AsyncSession)


class SessionFactory(Generic[T], async_sessionmaker[T]):
    def __init__(
        self,
        bind: AsyncEngine | AsyncConnection | None = None,
        *,
        class_: type[T] = AsyncSession,
        autoflush: bool = True,
        expire_on_commit: bool = False,
        info: dict[Any, Any] | None = None,
        **kw: Any
    ):
        super().__init__(
            bind,
            class_=class_,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            info=info,
            **kw
        )


    async def get_all_models[Model: User | Employee](self, model_class: type[Model]) -> dict[str, Model]:
        async with self() as session:
            statement = select(model_class)
            result = await session.exec(statement)

            return {
                normalize_cyrillic(model.name): model
                for model in result
            }


    async def update_model(self, model: User | Employee):
        async with self() as session:
            model = await session.merge(model)
            await session.commit()
            await session.refresh(model)


__all__ = ["SessionFactory"]
