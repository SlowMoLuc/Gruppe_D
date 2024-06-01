from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import Booking, Room, Guest, Address

class ReservationManager:
    def __init__(self, db_path: Path):
        self.__engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def book_room_registered(self, user_id: int, room_number: str, hotel_id: int, start_date, end_date, number_of_guests: int):
        room = self.__session.query(Room).filter(Room.hotel_id == hotel_id, Room.number == room_number).first()
        if not room:
            raise ValueError(f"Room {room_number} in hotel {hotel_id} not found.")

        booking = Booking(
            guest_id=user_id,
            room_hotel_id=hotel_id,
            room_number=room_number,
            start_date=start_date,
            end_date=end_date,
            number_of_guests=number_of_guests
        )
        self.__session.add(booking)
        self.__session.commit()
        return booking

    def book_room_guest(self, firstname: str, lastname: str, email: str, street: str, zip_code: str, city: str, room_number: str, hotel_id: int, start_date, end_date, number_of_guests: int):
        address = Address(street=street, zip=zip_code, city=city)
        guest = Guest(firstname=firstname, lastname=lastname, email=email, address=address)

        self.__session.add(address)
        self.__session.add(guest)
        self.__session.commit()

        room = self.__session.query(Room).filter(Room.hotel_id == hotel_id, Room.number == room_number).first()
        if not room:
            raise ValueError(f"Room {room_number} in hotel {hotel_id} not found.")

        booking = Booking(
            guest_id=guest.id,
            room_hotel_id=hotel_id,
            room_number=room_number,
            start_date=start_date,
            end_date=end_date,
            number_of_guests=number_of_guests
        )
        self.__session.add(booking)
        self.__session.commit()
        return booking
