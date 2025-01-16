from sqlalchemy import select, delete

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.models.user import User
from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user):
        raise NotImplementedError

    @abstractmethod
    async def get(self, user_id: int | UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str):
        raise NotImplementedError

    @abstractmethod
    async def update(self, user_id: int | UUID, data):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: int | UUID):
        raise NotImplementedError


class SqlaUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create(self, user: User) -> User:
        try:
            self.__session.add(user)
            await self.__session.commit()
            await self.__session.refresh(user)
            return user
        except:
            await self.__session.rollback()
            raise

    async def get(self, user_id: UUID) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.__session.execute(stmt)
        return result.unique().scalars().first()

    async def get_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        result = await self.__session.execute(stmt)
        return result.unique().scalars().first()

    async def update(self, user_id: UUID, user: User) -> User:
        try:
            self.__session.add(user)
            await self.__session.commit()
            await self.__session.refresh(user)
            return user
        except:
            await self.__session.rollback()
            raise

    async def delete(self, user_id: UUID) -> User:
        stmt = delete(User).where(User.id == user_id).returning(User)
        try:
            result = await self.__session.execute(stmt)
            await self.__session.commit()
            return result.scalars().first()
        except:
            await self.__session.rollback()
            raise
