
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# Tạo URL kết nối MySQL
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME
)


# Khởi tạo SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "init_command": "SET SESSION time_zone = '+00:00'"
    }
)


# Khởi tạo Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base dùng chung cho các Model
Base = declarative_base()


# Dependency cung cấp Database Session
def get_db():

    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# Kiểm tra kết nối MySQL
def test_connection():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
