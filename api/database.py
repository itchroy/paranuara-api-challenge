from contextlib import contextmanager
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Database(object):
    """
    Simple handle to a SQLite back-end.
    Initalises DB schema for SQLAlchemy.

    Args:
        file_name: local filename of SQLite DB
    """
    def __init__(self, file_name):
        if os.path.exists(file_name):
            print("database file '{}' already exists. Removing...".format(file_name))
            os.remove(file_name)

        self.engine = create_engine('sqlite:///{}'.format(file_name), convert_unicode=True)
        self.session_factory = scoped_session(sessionmaker(autocommit=False,
                                                           autoflush=False,
                                                           bind=self.engine))

        Base.metadata.create_all(bind=self.engine)
        Base.query = self.session_factory.query_property()


@contextmanager
def write_scope(db):
    """
    Provide a transactional scope around a series of write operations.
    On exception, transaction is rolled back.

    Args:
        db: db instance
    """
    session = db.session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def read_scope(db):
    """
    Provide a transactional scope around a series of read operations
    On exception, transaction is rolled back.

    Args:
        db: db instance
    """
    session = db.session_factory()
    try:
        yield session
    except:
        raise
    finally:
        session.close()
