from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.adapters.producers.factory import ProducerFactory
from src.adapters.producers.rabbitmq_producer import RabbitMQProducer
from src.core.config import settings
from src.db.database import AsyncSessionFactory
from src.exceptions.user import AuthorizationException
from src.repositories.user_repository import SqlaUserRepository
from src.schemas.user import UserOut
from src.services.email_service import EmailService
from src.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_session() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_user_service(session: AsyncSession = Depends(get_session)):
    repository = SqlaUserRepository(session)
    email_service = get_email_service()
    return UserService(repository, email_service)

def get_email_service():
    return EmailService(producer_factory)

async def get_current_user(token: str = Depends(oauth2_scheme),
                           user_service: UserService = Depends(get_user_service)) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        return await user_service.verify_credentials(token)
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except:
        raise credentials_exception


async def get_current_admin(token: str = Depends(oauth2_scheme),
                            admin_service: UserService = Depends(get_user_service)) -> UserOut:
    user = await get_current_user(token, user_service=admin_service)
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return user

producer_factory = ProducerFactory(RabbitMQProducer,
                                   rabbitmq_url=settings.RABBITMQ_URL,
                                   queue_name=settings.RABBITMQ_QUEUE)