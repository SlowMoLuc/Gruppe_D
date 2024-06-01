from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from data_access.data_base import init_db


class BaseManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self._engine = create_engine(f'sqlite:///{database_file}', echo=False)
        self._session = scoped_session(sessionmaker(bind=self._engine))