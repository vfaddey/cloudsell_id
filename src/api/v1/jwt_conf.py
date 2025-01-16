from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(prefix='/.well-known')


@router.get('/jwks.json')
async def get_jwks():
    return {
      "keys": [
        {
          "kty": "RSA",
          "kid": "1",
          "use": "sig",
          "alg": "RS256",
          "n": settings.JWT_PUBLIC_KEY
        }
      ]
    }