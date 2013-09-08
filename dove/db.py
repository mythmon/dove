from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dove.config import config


Base = declarative_base()


class Torrent(Base):
    __tablename__ = 'torrent'
    id = Column(Integer, primary_key=True)
    info_hash = Column(String(40), nullable=False)
    state = Column(String(16))


engine = None


def get_session(*args, **kwargs):
    global engine
    if engine is None:
        engine = create_engine(config['db_url'])
    return sessionmaker(bind=engine)(*args, **kwargs)


def get_or_create(session, model, defaults={}, **kwargs):
    """Get an instance of a model based on kwargs. If not found, create it.

    The model is instatiated with `defaults` and `kwargs` (defaults wins ties).

    Returns the created or found model, and a boolean indicating if it was just
    created.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = {k: v for k, v in kwargs.iteritems()}
        params.update(defaults)
        instance = model(**params)
        session.add(instance)
        return instance, True
