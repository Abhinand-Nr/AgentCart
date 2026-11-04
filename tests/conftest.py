from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, DATABASE_URL, get_db
from app.main import app
from app.models import Product

# Same address as the real database, but ending in /agentcart_test
TEST_DATABASE_URL = DATABASE_URL.rsplit("/", 1)[0] + "/agentcart_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    session = TestingSession()
    yield session
    session.close()
    with engine.begin() as conn:
                conn.execute(text("TRUNCATE cart_items, products, users RESTART IDENTITY CASCADE"))


@pytest.fixture
def products(db):
    items = [
        Product(name="Running Shoes", price=Decimal("2399.00"), category="Footwear",
                stock=5, description="Light trail shoes"),
        Product(name="Cotton Socks", price=Decimal("299.00"), category="Sports",
                stock=20, description="Pack of 3"),
        Product(name="Smartwatch", price=Decimal("4999.00"), category="Electronics",
                stock=2, description="Fitness tracker"),
    ]
    db.add_all(items)
    db.commit()
    return items


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()