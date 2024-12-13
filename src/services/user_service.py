from uuid import UUID

from jose import JWTError
from pydantic import EmailStr

from src.core.jwt_provider import JWTProvider
from src.core.security import verify_password, hash_password
from src.exceptions.token import InvalidToken
from src.exceptions.user import (UserNotFound,
                                 AuthenticationException,
                                 AuthorizationException,
                                 UserAlreadyExists)
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.token import FullToken, Token
from src.schemas.user import UserCreate, UserOut


class UserService:
    def __init__(self, repository: UserRepository):
        self.__repository = repository

    async def create(self, user: UserCreate) -> Token:
        existing_user = await self.__repository.get_by_email(user.email)
        if existing_user:
            raise UserAlreadyExists('User with such email already exists')
        user_model = User(**user.dict())
        hashed_password = hash_password(user_model.password)
        user_model.password = hashed_password
        inserted_user = await self.__repository.create(user_model)
        if not inserted_user:
            raise Exception('Failed to create user')
        token = self.__create_token(user_model.id, user_model.email, full_token=True)
        return token

    async def get(self, user_id: UUID | int) -> UserOut:
        user = await self.__repository.get(user_id)
        if not user:
            raise UserNotFound(f'No user with such id: {user_id}')
        return UserOut.from_orm(user)

    async def delete(self, user_id: UUID | int) -> UserOut:
        result = await self.__repository.delete(user_id)
        if not result:
            raise UserNotFound(f'No user with such id: {user_id}')
        return UserOut.from_orm(result)

    async def verify_credentials(self, token: str) -> UserOut:
        try:
            payload = JWTProvider.decode(token)
            user_id = payload.get('sub')
            user = await self.__repository.get(user_id)
            if not user:
                raise UserNotFound(f'No user with such id: {user_id}')
            return UserOut.from_orm(user)
        except InvalidToken as e:
            raise AuthorizationException(str(e))

    def __create_token(self, user_id: UUID, email: EmailStr, full_token=False) -> Token:
        payload = {
            'sub': str(user_id),
            'email': email
        }
        try:
            access_token = JWTProvider.encode_access_token(payload)
            token_type = JWTProvider.token_type
            if full_token:
                refresh_token = JWTProvider.encode_refresh_token(payload)
                return FullToken(access_token=access_token, refresh_token=refresh_token, token_type=token_type)
            return Token(access_token=access_token, token_type=token_type)
        except JWTError as e:
            raise AuthenticationException('Failed to create token')

    async def authorize_user(self, email: str, password: str) -> UserOut:
        user = await self.__repository.get_by_email(email)
        if not user:
            raise UserNotFound(f'No user with such email: {email}')
        if not verify_password(password, user.password):
            raise AuthenticationException('Incorrect password')
        return UserOut.from_orm(user)

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.authorize_user(email, password)
        return self.__create_token(user.id, email, full_token=True)

    async def refresh_token(self, token: str) -> Token:
        user = await self.verify_credentials(token)
        new_access_token = self.__create_token(user.id, user.email)
        return new_access_token

