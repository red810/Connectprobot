"""
Database models and utilities using SQLAlchemy async.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///connectprobot.db')

# Create SQLAlchemy async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


class Owner(Base):
    """Owner model: represents a business/channel owner."""
    __tablename__ = 'owners'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default='Other')
    bio = Column(Text, default='')
    logo_file_id = Column(String(512), nullable=True)
    plan = Column(String(50), default='basic')
    active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)
    subscription_expires = Column(DateTime, nullable=True)
    mini_bot_token = Column(String(1024), nullable=True)


class User(Base):
    """User model: stores users who message owners."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)


class Conversation(Base):
    """Conversation log model."""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey('owners.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    last_message = Column(Text)
    last_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship('Owner')
    user = relationship('User')


async def init_db():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a new database session."""
    async with AsyncSessionLocal() as session:
        yield session
