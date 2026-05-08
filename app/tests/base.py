import asyncio
import os

# Должно стоять до любых импортов app.* — иначе get_settings() прочитает прод-конфиг.
os.environ["STATAPI_CONFIG"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config.test.yaml",
)
os.environ["STATAPI_LOGGING"] = os.environ.get("STATAPI_LOGGING", "0")

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import load_settings
from app.database import create_async_engine, async_sessionmaker
from app.factory import AppFactory
from app.tests.hooks import TestHooks
from app.tests.init_db import init_test_database

settings = load_settings()

# ── Тестовая БД: новый engine + session_maker, не общий с прод-кодом ─────────

db_path = settings.sqlalchemy_database_url.path.removeprefix("/")
try:
    os.remove(db_path)
except FileNotFoundError:
    pass

test_engine = create_async_engine(str(settings.sqlalchemy_database_url), future=True)
test_session_maker = async_sessionmaker(
    autoflush=True,
    autocommit=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

app = AppFactory(TestHooks(test_session_maker))(settings)

asyncio.run(init_test_database(test_engine, test_session_maker, app))

client = TestClient(app)
