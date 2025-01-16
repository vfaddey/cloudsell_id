import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, String, VARCHAR, DateTime, Boolean, Enum

from src.db.database import Base


class AccountType(enum.Enum):
    PHYSICAL = 'physical'
    COMPANY = 'company'


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(VARCHAR(70), unique=True, nullable=False)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    account_type = Column(Enum(AccountType), default=AccountType.PHYSICAL, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
