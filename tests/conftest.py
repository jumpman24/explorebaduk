import pytest
from sqlalchemy import create_engine

from config import TEST_DATABASE_URI
from explorebaduk.database import BaseModel
from scripts.database import (
    make_user,
    make_token,
    populate_database_with_data,
)
from explorebaduk.server import db


@pytest.fixture(scope="session", autouse=True)
def db_session():
    engine = create_engine(TEST_DATABASE_URI)
    db.bind = engine
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    populate_database_with_data(db, 20)

    return db


@pytest.fixture(scope="session")
def user1(db_session):
    user = make_user(1)

    db_session.save(user)

    return user


@pytest.fixture(scope="session")
def token1(db_session, user1):
    token = make_token(user1.user_id, user1.user_id, 60)

    db_session.save(token)

    return token


@pytest.fixture(scope="session")
def token_expired(db_session, user1):
    token = make_token(666, user1.user_id, 0)

    db_session.save(token)

    return token
