"""
database.py - Async PostgreSQL with SQLAlchemy
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.future import select

Base = declarative_base()

class Owner(Base):
    __tablename__ = "owners"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True)
    business_name = Column(String)
    logo_file_id = Column(String, nullable=True)
    category = Column(String)
    bio = Column(Text)
    subscription_plan = Column(String)
    trial_ends = Column(DateTime, nullable=True)
    subscribed = Column(Boolean, default=False)
    bot_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class MessageLog(Base):
    __tablename__ = "message_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    owner_id = Column(Integer, ForeignKey("owners.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=func.now())

engine = None
SessionLocal = None

async def init_db(db_url: str):
    global engine, SessionLocal
    engine = create_async_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_owner_by_telegram_id(telegram_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Owner).where(Owner.telegram_id == telegram_id)
        )
        return result.scalars().first()

async def get_messages_for_owner(owner_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(MessageLog).where(MessageLog.owner_id == owner_id)
        )
        return result.scalars().all()
        