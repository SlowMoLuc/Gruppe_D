from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db

class BaseManager:
    def __init__(self, db_file: str):
        self._db_filepath = Path(db_file)
        if not self._db_filepath.is_file():
            init_db(str(self._db_filepath), generate_example_data=True)

        self._engine = create_engine(f"sqlite:///{self._db_filepath}")
        self._session = scoped_session(sessionmaker(bind=self._engine))
