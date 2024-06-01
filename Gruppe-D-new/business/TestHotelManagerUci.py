import sys
from pathlib import Path
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload
from sqlalchemy import create_engine, select

from business.BaseManager import BaseManager
from data_access.data_base import init_db
from data_models.models import Hotel, Address, Room

class HotelManager(BaseManager):

    def add_hotel(self, hotel_name, hotel_stars, street, zip, city, rooms):
        hotel = Hotel(
            name=hotel_name,
            stars=hotel_stars,
            address=Address(
                street=street,
                zip=zip,
                city=city),
                rooms=rooms
        )

        self._session.add(hotel)
        self._session.commit()

        query = select(Hotel).where(Hotel.name == hotel_name).options(joinedload(Hotel.rooms))
        result = self._session.execute(query).unique().scalars().all()
        print(result)

    def delete_hotel(self):
        pass

    def update_informations(self):
        pass

    def validate(self, ask_input, error_msg, type):
        while True:
            user_input = input(ask_input)
            try:
                user_input = type(user_input)
                return user_input
            except ValueError:
                print(error_msg)

    def validate_in_range(self, ask_input, error_msg, type, min, max):
        while True:
            user_input = self.validate(ask_input, error_msg, type)
            if min <= user_input <= max:
                return user_input
            else:
                print(error_msg)

    def room_number_exists(self, room_number, rooms):
        return any(room.number == room_number for room in rooms)

    def validate_yes_no(self, ask_input):
        while True:
            user_input = input(ask_input).strip().lower()
            if user_input in ['yes', 'no']:
                return user_input
            else:
                print("Please answer with 'yes' or 'no'.")

if __name__ == "__main__":
    manager = HotelManager("../data/hotel_reservation.db")

    hotel_name_input = manager.validate("Hotel Name: ", "Invalid Hotel Name!", str)
    hotel_stars_input = manager.validate_in_range("Hotel Stars: ", "Invalid Stars!", int, 0, 5)
    street_input = manager.validate("Street: ", "Invalid Street!", str)
    zip_input = manager.validate("Zip Code: ", "Invalid Zip Code!", str)
    city_input = manager.validate("City: ", "Invalid City!", str)

    rooms = []

    while True:
        while True:
            room_number_input = manager.validate_in_range("Room number: ", "Invalid Room Number!", int, 1, sys.maxsize)
            if manager.room_number_exists(room_number_input, rooms):
                print(f"Room number {room_number_input} already exists for this hotel. Please enter a different room number.")
            else:
                break

        room_type_input = manager.validate("Enter room type: ", "Invalid Room Type!", str)
        room_max_guests_input = manager.validate_in_range("Room max. guests: ", "Invalid Guest Number!", int, 1, sys.maxsize)
        room_description_input = manager.validate("Room description: ", "Invalid Room Description!", str)
        room_amenities_input = manager.validate("Amenities: ", "Invalid Amenities!", str)
        room_price_input = manager.validate_in_range("Price: ", "Invalid Price!", float, 0, sys.maxsize)

        rooms.append(Room(number=room_number_input,
                          type=room_type_input,
                          max_guests=room_max_guests_input,
                          description=room_description_input,
                          amenities=room_amenities_input,
                          price=room_price_input))

        add_another = manager.validate_yes_no("Would you like to add another room? (yes/no): ")
        if add_another != 'yes':
            break

    manager.add_hotel(hotel_name_input, hotel_stars_input, street_input, zip_input, city_input, rooms)
    print(rooms)
