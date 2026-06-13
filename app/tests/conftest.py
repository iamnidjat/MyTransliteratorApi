from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.auth.dependencies import get_optional_current_user, get_current_user
from app.core.database import Base, get_db
from app.core.models.user_model import User
from app.main import app

import os
from dotenv import load_dotenv

load_dotenv()

# not to use the real db
TEST_DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_TEST_NAME')}"

# creates connection to the test database
engine = create_engine(TEST_DATABASE_URL)

# factory that creates new DB sessions for tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine) # creates tables  
    yield # pauses function here → tests run
    Base.metadata.drop_all(bind=engine) # cleanups after tests


@pytest.fixture(scope="function")
def db():
    connection = engine.connect() # starts connection
    transaction = connection.begin() # opens transaction
    session = TestingSessionLocal(bind=connection) # binds the session to the connection

    try:
        yield session # gives session to test
    finally:
        session.close() # closes session
        transaction.rollback() # undos all changes
        connection.close() # closes connection


@pytest.fixture(scope="function") 
def test_client(db: Session): 
    # to replace real DB dependency with test DB session
    def override_get_db():
        yield db 

    # to inject override into FastAPI app
    app.dependency_overrides[get_db] = override_get_db 

    try:
        # creates test client for API requests
        with TestClient(app) as test_client: 
            yield test_client 
    finally:
        # removes override after test 
        # app.dependency_overrides.clear()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def test_user():
    return User(
        id=1,
        name="Test User",
        email="testuser@example.com",
        hashed_password="fakehashedpassword"
    )


@pytest.fixture(scope="function")
def override_get_optional_current_user(test_user):
    def _override():
        return test_user

    app.dependency_overrides[get_optional_current_user] = _override

    yield

    app.dependency_overrides.pop(get_optional_current_user, None) # removing only this specific override, not all overrides


@pytest.fixture(scope="function")
def override_get_current_user(test_user):
    def _override():
        return test_user

    app.dependency_overrides[get_current_user] = _override

    yield

    app.dependency_overrides.pop(get_current_user, None)