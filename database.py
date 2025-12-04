"""
database.py
Async PostgreSQL connection using SQLAlchemy
Manages:
- Users
- Owners
- Subscription records
- Messages (deleted after 72 days)
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from config import settings

Base = declarative_base()

# TABLE — Owners
class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True)
    business_name = Column(String)
    logo_file_id = Column(String)
    category = Column(String)
    bio = Column(Text)
    subscription_plan = Column(String)  # basic, premium, lifetime_basic, lifetime_premium
    trial_ends = Column(DateTime)
    subscribed = Column(Boolean, default=False)
    bot_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())


# TABLE — Normal Users messaging Owners
class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    owner_id = Column(Integer, ForeignKey("owners.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())


# Async DB
engine = None
SessionLocal = None


async def init_db(db_url: str):
    global engine, SessionLocal
    engine = create_async_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def close_db():
    global engine
    if engine:
        await engine.dispose()