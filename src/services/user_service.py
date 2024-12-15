from uuid import UUID

from jose import JWTError
from pydantic import EmailStr

from src.core.config import settings, email_settings
from src.core.jwt_provider import JWTProvider
from src.core.security import verify_password, hash_password
from src.exceptions.token import InvalidToken
from src.exceptions.user import (UserNotFound,
                                 AuthenticationException,
                                 AuthorizationException,
                                 UserAlreadyExists, AlreadyConfirmed)
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.token import FullToken, Token
from src.schemas.user import UserCreate, UserOut
from src.services.email_service import EmailService


class UserService:
    def __init__(self,
                 repository: UserRepository,
                 email_service: EmailService):
        self.__repository = repository
        self.__email_service = email_service

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
        try:
            user_out = UserOut.from_orm(inserted_user)
            await self.send_confirmation_email(user_out)
        except Exception as e:
            print(e)
        finally:
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
            payload = self.__get_token_payload(token)
            user_id = payload.get('sub')
            user = await self.__repository.get(user_id)
            if not user:
                raise UserNotFound(f'No user with such id: {user_id}')
            return UserOut.from_orm(user)
        except InvalidToken as e:
            raise AuthorizationException(str(e))

    def __get_token_payload(self, token: str) -> dict:
        try:
            payload = JWTProvider.decode(token)
            return payload
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

    async def send_confirmation_email(self,
                                      user: UserOut):
        if user.email_confirmed:
            raise AlreadyConfirmed('This email already confirmed')
        token = self.__generate_confirmation_token(user)
        data = {
            'user_id': user.id,
            'email': user.email,
            'type': 'email',
            'extra_data':{
                'token': token,
                'name': user.name,
            }
        }
        result = await self.__email_service.send_email(email_settings.CONFIRMATION_EMAIL_TEMPLATE, data)

    async def send_password_reset_email(self, email: str):
        user = await self.__repository.get_by_email(email)
        if not user:
            raise UserNotFound(f'No user with such email: {email}')
        user_out = UserOut.from_orm(user)
        token = self.__generate_confirmation_token(user_out)
        data = {
            'user_id': user.id,
            'email': user.email,
            'type': 'email',
            'extra_data': {
                'name': user.name,
                'token': token,
            }
        }
        result = await self.__email_service.send_email(email_settings.RESET_PASSWORD_EMAIL_TEMPLATE, data)

    def __generate_confirmation_token(self, user: UserOut) -> str:
        try:
            payload = {
                'sub': str(user.id),
                'email': user.email,
                'confirmation': True,
            }
            token = JWTProvider.encode_refresh_token(payload, expires_delta=settings.CONFIRMATION_TOKEN_LIFETIME)
            return token
        except JWTError:
            raise AuthorizationException('Failed to create token')

    async def confirm_email(self, token: str) -> UserOut:
        try:
            payload = self.__get_token_payload(token)
            if not payload.get('confirmation'):
                raise AuthorizationException('No confirmation token')
            user_id = payload.get('sub')
            user = await self.__repository.get(user_id)
            if not user:
                raise UserNotFound(f'No user with such id: {user_id}')
        except InvalidToken as e:
            raise AuthorizationException(str(e))
        user.email_confirmed = True
        result = await self.__repository.update(user.id, user)
        if not result:
            raise UserNotFound(f'No user with such id: {user.id}')
        return UserOut.from_orm(result)
