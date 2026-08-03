import os
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./frameworkfit.db")

# Render's PostgreSQL returns postgres:// but SQLAlchemy 2.0+ requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def reconcile_database_schema(engine, metadata):
    """
    Checks existing database tables and automatically adds any missing columns defined in SQLALchemy models.
    Prevents UndefinedColumn errors when new columns are added without Alembic migrations.
    """
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table_name, table in metadata.tables.items():
            if not inspector.has_table(table_name):
                continue
            existing_cols = {col["name"] for col in inspector.get_columns(table_name)}
            for col in table.columns:
                if col.name not in existing_cols:
                    col_type = col.type.compile(engine.dialect)
                    logger.info(f"[Schema] Adding missing column {table_name}.{col.name} ({col_type})")
                    try:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}"))
                    except Exception as e:
                        logger.warning(f"[Schema] Note adding column {table_name}.{col.name}: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
