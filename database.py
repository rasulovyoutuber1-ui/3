"""Ma'lumotlar bazasi - SQLAlchemy va aiosqlite orqali"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Text, BigInteger
from config import config
import random

engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Anime(Base):
    __tablename__ = "animes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    genres_str: Mapped[str] = mapped_column(String(255), default="")
    poster_url: Mapped[str] = mapped_column(String(500), nullable=True)

    @property
    def genres(self) -> list[str]:
        return [g.strip() for g in self.genres_str.split(",") if g.strip()]

class VipCode(Base):
    __tablename__ = "vip_codes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    is_used: Mapped[int] = mapped_column(Integer, default=0)

class DatabaseManager:
    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_anime_by_code(self, code: str) -> Anime | None:
        async with async_session() as session:
            result = await session.execute(Anime.__table__.select().where(Anime.code == code))
            row = result.fetchone()
            if row:
                return Anime(
                    id=row.id, code=row.code, title=row.title, description=row.description,
                    year=row.year, rating=row.rating, genres_str=row.genres_str, poster_url=row.poster_url
                )
            return None

    async def get_random_anime(self) -> Anime | None:
        async with async_session() as session:
            result = await session.execute(Anime.__table__.select())
            rows = result.fetchall()
            if not rows:
                return None
            row = random.choice(rows)
            return Anime(
                id=row.id, code=row.code, title=row.title, description=row.description,
                year=row.year, rating=row.rating, genres_str=row.genres_str, poster_url=row.poster_url
            )

    async def create_vip_code(self, code: str, duration_days: int):
        async with async_session() as session:
            db_code = VipCode(code=code, duration_days=duration_days, is_used=0)
            session.add(db_code)
            await session.commit()

db_session = DatabaseManager()
init_db = db_session.init_db
