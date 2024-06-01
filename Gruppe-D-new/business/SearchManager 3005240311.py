import os
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *
from datetime import datetime

class SearchManager(object):
    def __init__(self) -> None:
        self.__load_db()

    def __load_db(self):
        if not os.environ.get("DB_FILE"):
            raise ValueError("You have to define the environment variable 'DB_FILE'")
        self.__db_filepath = Path(os.environ.get("DB_FILE"))

        if not self.__db_filepath.is_file():
            init_db(str(self.__db_filepath), generate_example_data=True)

        self._engine = create_engine(f'sqlite:///{self.__db_filepath}')
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def get_hotels(self, name: str = "", city: str = "", stars: int = None):
        query = select(Hotel)
        if name != "":
            query = query.where(Hotel.name.like(f'%{name}%'))
        if city != "":
            query = query.join(Address).where(Address.city.like(f"%{city}%"))
        if stars is not None:
            query = query.where(Hotel.stars == stars)
        return self._session.execute(query).scalars().all()

    def get_hotels_by_name(self, name: str = ""):
        query = select(Hotel)
        if name != "":
            query = query.where(Hotel.name.like(f'%{name}%'))
        return self._session.execute(query).scalars().all()

    def get_hotels_by_city(self, city: str = ""):
        query = select(Hotel)
        if city != "":
            query = query.join(Address).where(Address.city.like(f"%{city}%"))
        return self._session.execute(query).scalars().all()

    def get_available_rooms(self, hotel_id: int, start_date: datetime.date, end_date: datetime.date):
        if start_date is None or end_date is None:
            return []

        booked_rooms_subquery = (
            select(Booking.room_number)
            .where(Booking.room_hotel_id == hotel_id)
            .where(
                (Booking.start_date <= end_date) &
                (Booking.end_date >= start_date)
            )
        )

        query = (
            select(Room)
            .where(Room.hotel_id == hotel_id)
            .where(Room.number.not_in(booked_rooms_subquery))
        )

        return self._session.execute(query).scalars().all()

    def get_all_rooms(self, hotel_id: int, start_date: datetime.date, end_date: datetime.date):
        booked_rooms = self.get_available_rooms(hotel_id, start_date, end_date)
        all_rooms = self._session.query(Room).filter(Room.hotel_id == hotel_id).all()

        room_info = []
        for room in all_rooms:
            availability = "Available" if room in booked_rooms else "Not Available"
            room_info.append((room, availability))

        return room_info

def show(hotels, search_manager, start_date, end_date):
    for hotel in hotels:
        print("-------------------------------------------------------")
        print(f"Hotel ID: {hotel.id}")
        print(f"Hotel Name: {hotel.name}")
        print(f"Stars: {hotel.stars}")
        print(f"Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
        room_info = search_manager.get_all_rooms(hotel.id, start_date, end_date)
        for room, availability in room_info:
            print(f"Room ID: {room.number}, Type: {room.type}, Price: {room.price}, Availability: {availability}")
        print("-------------------------------------------------------")
