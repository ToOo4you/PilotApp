import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def _normalize_database_url(raw_url: str) -> str:
    database_url = raw_url.strip()

    # Some providers still emit postgres:// which SQLAlchemy 2 rejects.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url.startswith("postgresql://"):
        parsed = urlparse(database_url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))

        # Hosted Postgres providers often require TLS.
        if "sslmode" not in query:
            query["sslmode"] = "require"

        parsed = parsed._replace(query=urlencode(query))
        return urlunparse(parsed)

    return database_url


DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///pilot.db"))

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
