from src.core.config import settings
from datetime import datetime, timedelta
from jose import jwt, JWTError
from src.core.exceptions import InvalidTokenException


class JWTProvider:
    token_type = 'Bearer'
    @staticmethod
    def encode_refresh_token(payload: dict,
                             expires_delta=settings.REFRESH_TOKEN_LIFETIME,
                             algorithm=settings.JWT_ALGORITHM,
                             key=settings.JWT_PRIVATE_KEY):
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(days=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
        return encoded_jwt

    @staticmethod
    def encode_access_token(payload: dict,
                            expires_delta=settings.ACCESS_TOKEN_LIFETIME,
                            algorithm=settings.JWT_ALGORITHM,
                            key=settings.JWT_PRIVATE_KEY):
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(minutes=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, key, algorithm=algorithm)
        return encoded_jwt

    @staticmethod
    def decode(token,
               public_key=settings.JWT_PUBLIC_KEY,
               algorithm=settings.JWT_ALGORITHM) -> dict:
        try:
            payload = jwt.decode(token, public_key, algorithms=[algorithm])
            return payload
        except JWTError as e:
            raise InvalidTokenException('Token is invalid or expired')

