from sqlalchemy import select, create_engine
from sqlalchemy.orm import joinedload
from data_models.models import Hotel, Room, Booking, Address
from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker

class SearchManager:
    def __init__(self, db_path):
        self.__engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_hotels(self, name=None, city=None, stars=None):
        query = select(Hotel)
        if name:
            query = query.where(Hotel.name.ilike(f"%{name}%"))
        if city:
            query = query.join(Hotel.address).where(Address.city.ilike(f"%{city}%"))
        if stars:
            query = query.where(Hotel.stars == stars)
        return self.__session.execute(query).scalars().all()

    def get_all_rooms(self, hotel_id, start_date=None, end_date=None):
        query = select(Room).where(Room.hotel_id == hotel_id)
        rooms = self.__session.execute(query).scalars().all()
        available_rooms = []

        for room in rooms:
            if start_date and end_date:
                booked_rooms = self.get_booked_rooms(hotel_id, start_date, end_date)
                if room.number not in [br.number for br in booked_rooms]:
                    available_rooms.append(room)
            else:
                available_rooms.append(room)
        return available_rooms

    def get_available_rooms(self, hotel_id, start_date, end_date, number_of_guests=None, exclude_booking_id=None):
        start_date = start_date if isinstance(start_date, datetime) else datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = end_date if isinstance(end_date, datetime) else datetime.strptime(end_date, '%Y-%m-%d').date()

        booked_rooms_subquery = (
            select(Room.number)
            .join(Booking)
            .where(Booking.room_hotel_id == hotel_id)
            .where((Booking.start_date <= end_date) & (Booking.end_date >= start_date))
            .where(Booking.id != exclude_booking_id)  # Exclude the current booking if editing
        )
        query = select(Room).where(Room.hotel_id == hotel_id).where(Room.number.not_in(booked_rooms_subquery))
        if number_of_guests:
            query = query.where(Room.max_guests >= number_of_guests)
        return self.__session.execute(query).scalars().all()

    def get_booked_rooms(self, hotel_id, start_date, end_date):
        start_date = start_date if isinstance(start_date, datetime) else datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = end_date if isinstance(end_date, datetime) else datetime.strptime(end_date, '%Y-%m-%d').date()

        query = (
            select(Room)
            .join(Booking)
            .where(Booking.room_hotel_id == hotel_id)
            .where((Booking.start_date <= end_date) & (Booking.end_date >= start_date))
        )
        return self.__session.execute(query).scalars().all()
