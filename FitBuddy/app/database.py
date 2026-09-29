import os
from contextlib import contextmanager

from sqlalchemy import Column, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(20), nullable=False)
    original_plan = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)


Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def upsert_user(data: dict, plan: str, tip: str | None) -> User:
    """Create the user, or reset an existing user_id with a freshly generated plan."""
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == data["user_id"]).first()
        if user is None:
            user = User(**data)
            db.add(user)
        else:
            for key, value in data.items():
                setattr(user, key, value)
        user.original_plan = plan
        user.updated_plan = None
        user.nutrition_tip = tip
        db.flush()
        return user


def save_updated_plan(user_id: str, updated_plan: str) -> None:
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.updated_plan = updated_plan


def get_user(user_id: str) -> User | None:
    with session_scope() as db:
        return db.query(User).filter(User.user_id == user_id).first()


def get_all_users() -> list[User]:
    with session_scope() as db:
        return db.query(User).order_by(User.id.desc()).all()


def delete_user(user_id: str) -> bool:
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        db.delete(user)
        return True
