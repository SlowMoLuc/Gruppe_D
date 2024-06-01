import sys
from pathlib import Path
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload
from sqlalchemy import create_engine, select

from business.BaseManager import BaseManager
from data_access.data_base import init_db
from data_models.models import Hotel, Address, Room

class HotelManager(BaseManager):

    def delete_hotel(self, hotel_id):
        hotel = self._session.query(Hotel).filter(Hotel.id == hotel_id).first()
        if hotel:
            print(f"Hotel Details:\nID: {hotel.id}\nName: {hotel.name}\nStars: {hotel.stars}\nAddress: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
            confirmation = self.validate_yes_no("Are you sure you want to delete this hotel? (yes/no): ")
            if confirmation == 'yes':
                for room in hotel.rooms:
                    self._session.delete(room)
                self._session.delete(hotel)
                self._session.commit()
                print(f"'{hotel.name}' with ID {hotel_id} has been deleted. There are now {self._session.query(Hotel).count()} hotel(s) left in the database.")
            else:
                print("Deletion cancelled.")
        else:
            print(f"No hotel found with ID {hotel_id}.")

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

    def list_hotels(self):
        hotels = self._session.query(Hotel).all()
        if hotels:
            for hotel in hotels:
                print(f"ID: {hotel.id}, Name: {hotel.name}, Stars: {hotel.stars}, Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
        else:
            print("No hotels found.")

    def list_hotel_rooms(self, hotel_id):
        hotel = self._session.query(Hotel).filter(Hotel.id == hotel_id).first()
        if hotel:
            if hotel.rooms:
                print(f"Rooms for Hotel ID {hotel_id} - {hotel.name}:")
                for room in hotel.rooms:
                    print(f"Room Number: {room.number}, Type: {room.type}, Max Guests: {room.max_guests}, Description: {room.description}, Amenities: {room.amenities}, Price: {room.price}")
            else:
                print(f"No rooms found for Hotel ID {hotel_id}.")
        else:
            print(f"No hotel found with ID {hotel_id}.")

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

    def update_hotel(self):
        hotel_id = input("Enter the Hotel ID to update: ")
        hotel = self._session.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            print("No hotel found with that ID.")
            return
        print(
            f"Hotel Details:\nID: {hotel.id}\nName: {hotel.name}\nStars: {hotel.stars}\nAddress: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
        print("Which attribute would you like to update?")
        print("1. Hotel Name")
        print("2. Hotel Stars")
        print("3. Hotel Address")
        print("4. Room Details")
        choice = input("Enter your choice (1-4): ")

        match choice:
            case '1':
                print(f"Current Hotel Name: {hotel.name}")
                new_name = input("Enter the new name for the hotel: ")
                hotel.name = new_name
                print(f"New Hotel Name: {hotel.name}")

            case '2':
                new_stars = input("Enter the new star rating (1-5): ")
                try:
                    hotel.stars = int(new_stars)
                except ValueError:
                    print("Invalid input. Stars must be an integer.")
                    return

            case '3':
                new_street = input("Enter the new street: ")
                new_zip = input("Enter the new zip code: ")
                new_city = input("Enter the new city: ")
                if not hotel.address:
                    hotel.address = Address()
                hotel.address.street = new_street
                hotel.address.zip = new_zip
                hotel.address.city = new_city

            case '4':
                room_number = input("Enter the room number to update: ")
                room = next((r for r in hotel.rooms if str(r.number) == room_number), None)
                if not room:
                    print("No room found with that number.")
                    return
                new_type = input("Enter the new room type: ")
                new_price = input("Enter the new price: ")
                try:
                    room.type = new_type
                    room.price = float(new_price)
                except ValueError:
                    print("Invalid price. Please enter a valid number.")
                    return

            case _:
                print("Invalid choice.")
                return

        self._session.commit()
        print("Update successful!")


def validate(ask_input, error_msg, type):
    while True:
        user_input = input(ask_input)
        try:
            user_input = type(user_input)
            return user_input
        except ValueError:
            print(error_msg)

def validate_in_range(ask_input, error_msg, type, min, max):
    while True:
        user_input = validate(ask_input, error_msg, type)
        if user_input >= min and user_input <= max:
            return user_input
        else: print(error_msg)


if __name__ == "__main__":
    manager = HotelManager("../data/hotel_reservation.db")

    while True:
        print("\nOptions:")
        print("1. Add a new hotel")
        print("2. Delete an existing hotel")
        print("3. Update an existing hotel")
        print("4. List all hotels")
        print("5. List all rooms for a specific hotel")
        print("6. Exit Manager")
        user_choice = input("Please select an option (1-6): ")

        match user_choice:
            case '1':
                hotel_name_input = manager.validate("Hotel Name: ", "Invalid Hotel Name!", str)
                hotel_stars_input = manager.validate_in_range("Hotel Stars: ", "Invalid Stars!", int, 0, 5)
                street_input = manager.validate("Street: ", "Invalid Street!", str)
                zip_input = manager.validate("Zip Code: ", "Invalid Zip Code!", str)
                city_input = manager.validate("City: ", "Invalid City!", str)

                rooms = []

                while True:
                    while True:
                        room_number_input = manager.validate_in_range("Room number: ", "Invalid Room Number!", int, 1,
                                                                      sys.maxsize)
                        if manager.room_number_exists(room_number_input, rooms):
                            print(
                                f"Room number {room_number_input} already exists for this hotel. Please enter a different room number.")
                        else:
                            break

                    room_type_input = manager.validate("Enter room type: ", "Invalid Room Type!", str)
                    room_max_guests_input = manager.validate_in_range("Room max. guests: ", "Invalid Guest Number!", int, 1,
                                                                      sys.maxsize)
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

            case '2':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to delete: "))
                    manager.delete_hotel(hotel_id_input)
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the Hotel ID.")

            case '3':
                manager.update_hotel()

            case '4':
                manager.list_hotels()

            case '5':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to list rooms: "))
                    manager.list_hotel_rooms(hotel_id_input)
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the Hotel ID.")

            case '6':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")



--------------------------------------------

Main user mng Backup

import os
from business.UserManager import UserManager

def validate(ask_input, error_msg, type, allow_back=False):
    while True:
        user_input = input(ask_input)
        if allow_back and user_input.lower() == 'back':
            return 'back'
        try:
            user_input = type(user_input)
            return user_input
        except ValueError:
            print(error_msg)

def validate_yes_no(ask_input, allow_back=False):
    while True:
        user_input = input(ask_input).strip().lower()
        if allow_back and user_input == 'back':
            return 'back'
        if user_input in ['yes', 'no']:
            return user_input
        else:
            print("Please answer with 'yes' or 'no'.")

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "data/hotel_reservation.db")
    manager = UserManager(db_path)

    while True:
        print("\nOptions:")
        print("1. Add a new user")
        print("2. Authenticate a user")
        print("3. View booking history")
        print("4. Change a booking")
        print("5. Exit User Manager")
        user_choice = input("Please select an option (1-5): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                username = validate("Enter username: ", "Invalid username!", str, allow_back=True)
                if username == 'back':
                    continue

                password = validate("Enter password: ", "Invalid password!", str, allow_back=True)
                if password == 'back':
                    continue

                role_id = validate("Enter Role ID: ", "Invalid Role ID!", int, allow_back=True)
                if role_id == 'back':
                    continue

                try:
                    user_id = manager.add_user(username, password, role_id)
                    print(f"User '{username}' with ID {user_id} has been added.")
                except ValueError as e:
                    print(e)

            case '2':
                username = input("Enter username: ")
                password = input("Enter password: ")
                result = manager.authenticate_user(username, password)
                if not result:
                    print("Wrong Username or Password.")
                else:
                    print(f"Welcome {result.username}!")

            case '3':
                user_id = validate("Enter user ID: ", "Invalid user ID!", int, allow_back=True)
                if user_id == 'back':
                    continue

                history = manager.get_booking_history(user_id)
                if history:
                    for booking in history:
                        print(f"Booking ID: {booking.id}, Hotel ID: {booking.room.hotel_id}, Room Number: {booking.room_number}, Start Date: {booking.start_date}, End Date: {booking.end_date}, Comment: {booking.comment}")
                else:
                    print("No booking history found.")

            case '4':
                booking_id = validate("Enter booking ID: ", "Invalid booking ID!", int, allow_back=True)
                if booking_id == 'back':
                    continue

                new_details = {}
                new_date = input("Enter new start date (YYYY-MM-DD) (or leave empty to skip): ")
                if new_date:
                    new_details['start_date'] = new_date
                new_end_date = input("Enter new end date (YYYY-MM-DD) (or leave empty to skip): ")
                if new_end_date:
                    new_details['end_date'] = new_end_date
                new_room_id = input("Enter new room ID (or leave empty to skip): ")
                if new_room_id:
                    new_details['room_number'] = new_room_id
                new_hotel_id = input("Enter new hotel ID (or leave empty to skip): ")
                if new_hotel_id:
                    new_details['room_hotel_id'] = new_hotel_id

                if not new_details:
                    print("No changes provided.")
                    continue

                success = manager.change_booking(booking_id, new_details)
                if success:
                    print("Booking updated successfully.")
                else:
                    print("Failed to update the booking.")

            case '5':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")






-------------------------------


UserManager Backup



from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from pathlib import Path
from data_access.data_base import init_db
from data_models.models import Login, Booking, Role
import os

class UserManager:
    def __init__(self, db_path) -> None:
        self.__load_db(db_path)

    def __load_db(self, db_path):
        self.__db_filepath = Path(db_path)

        if not self.__db_filepath.is_file():
            init_db(str(self.__db_filepath), generate_example_data=True)

        self._engine = create_engine(f"sqlite:///{self.__db_filepath}")
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def add_user(self, username, password, role_id):
        # Prüfen, ob der Benutzername bereits existiert
        existing_user = self._session.query(Login).filter_by(username=username).first()
        if existing_user:
            raise ValueError(f"Username '{username}' already exists.")

        # Prüfen, ob die Rolle existiert
        role = self._session.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role with ID {role_id} does not exist.")

        new_user = Login(username=username, password=password, role_id=role_id)
        self._session.add(new_user)
        self._session.commit()
        return new_user.id

    def authenticate_user(self, username, password):
        query = select(Login).where(Login.username == username).where(Login.password == password)
        result = self._session.execute(query).scalars().one_or_none()
        return result

    def get_booking_history(self, user_id):
        query = select(Booking).where(Booking.guest_id == user_id)
        result = self._session.execute(query).scalars().all()
        return result

    def change_booking(self, booking_id, new_details):
        booking = self._session.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            for key, value in new_details.items():
                setattr(booking, key, value)
            self._session.commit()
            return True
        return False


-----------------------------

Main combined




import os
from business.UserManager import UserManager
from business.HotelManager import HotelManager
from data_models.models import Hotel, Room, Address


def validate(ask_input, error_msg, type, allow_back=False):
    while True:
        user_input = input(ask_input)
        if allow_back and user_input.lower() == 'back':
            return 'back'
        try:
            user_input = type(user_input)
            return user_input
        except ValueError:
            print(error_msg)


def validate_yes_no(ask_input, allow_back=False):
    while True:
        user_input = input(ask_input).strip().lower()
        if allow_back and user_input == 'back':
            return 'back'
        if user_input in ['yes', 'no']:
            return user_input
        else:
            print("Please answer with 'yes' or 'no'.")


def admin_menu(hotel_manager):
    while True:
        print("\nAdmin Options:")
        print("1. Add a new hotel")
        print("2. Delete an existing hotel")
        print("3. Update an existing hotel")
        print("4. List all hotels")
        print("5. List all rooms for a specific hotel")
        print("6. Exit Admin Manager")
        user_choice = input("Please select an option (1-6): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                hotel_name_input = validate("Hotel Name: ", "Invalid Hotel Name!", str, allow_back=True)
                if hotel_name_input == 'back':
                    continue

                hotel_stars_input = validate("Hotel Stars: ", "Invalid Stars!", int, allow_back=True)
                if hotel_stars_input == 'back':
                    continue

                street_input = validate("Street: ", "Invalid Street!", str, allow_back=True)
                if street_input == 'back':
                    continue

                zip_input = validate("Zip Code: ", "Invalid Zip Code!", str, allow_back=True)
                if zip_input == 'back':
                    continue

                city_input = validate("City: ", "Invalid City!", str, allow_back=True)
                if city_input == 'back':
                    continue

                rooms = []

                while True:
                    room_number_input = validate("Room number: ", "Invalid Room Number!", int, allow_back=True)
                    if room_number_input == 'back':
                        break

                    room_type_input = validate("Enter room type: ", "Invalid Room Type!", str, allow_back=True)
                    if room_type_input == 'back':
                        break

                    room_max_guests_input = validate("Room max. guests: ", "Invalid Guest Number!", int,
                                                     allow_back=True)
                    if room_max_guests_input == 'back':
                        break

                    room_description_input = validate("Room description: ", "Invalid Room Description!", str,
                                                      allow_back=True)
                    if room_description_input == 'back':
                        break

                    room_amenities_input = validate("Amenities: ", "Invalid Amenities!", str, allow_back=True)
                    if room_amenities_input == 'back':
                        break

                    room_price_input = validate("Price: ", "Invalid Price!", float, allow_back=True)
                    if room_price_input == 'back':
                        break

                    rooms.append(Room(number=room_number_input, type=room_type_input, max_guests=room_max_guests_input,
                                      description=room_description_input, amenities=room_amenities_input,
                                      price=room_price_input))

                    add_another = validate_yes_no("Would you like to add another room? (yes/no): ", allow_back=True)
                    if add_another == 'back' or add_another == 'no':
                        break

                new_hotel = hotel_manager.add_hotel(hotel_name_input, hotel_stars_input, street_input, zip_input,
                                                    city_input, rooms)
                print(f"Hotel '{new_hotel.name}' with ID {new_hotel.id} has been added.")

            case '2':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to delete: "))
                    success = hotel_manager.delete_hotel(hotel_id_input)
                    if success:
                        print(f"Hotel with ID {hotel_id_input} has been deleted.")
                    else:
                        print("No hotel found with that ID.")
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the Hotel ID.")

            case '3':
                hotel_id = input("Enter the Hotel ID to update: ")
                hotel = hotel_manager._session.query(Hotel).filter(Hotel.id == hotel_id).first()
                if not hotel:
                    print("No hotel found with that ID.")
                    continue

                print(
                    f"Hotel Details:\nID: {hotel.id}\nName: {hotel.name}\nStars: {hotel.stars}\nAddress: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
                print("Which attribute would you like to update?")
                print("1. Hotel Name")
                print("2. Hotel Stars")
                print("3. Hotel Address")
                print("4. Room Details")
                choice = input("Enter your choice (1-4): ")

                match choice:
                    case '1':
                        new_name = input("Enter the new name for the hotel: ")
                        success = hotel_manager.update_hotel_name(hotel_id, new_name)
                        if success:
                            print(f"New Hotel Name: {new_name}")
                        else:
                            print("Failed to update the hotel name.")

                    case '2':
                        new_stars = validate("Enter the new star rating (1-5): ",
                                             "Invalid input. Stars must be between 1 and 5.", int, allow_back=True)
                        if new_stars == 'back':
                            continue
                        success = hotel_manager.update_hotel_stars(hotel_id, new_stars)
                        if success:
                            print(f"New Hotel Stars: {new_stars}")
                        else:
                            print("Failed to update the hotel stars.")

                    case '3':
                        new_street = input("Enter the new street: ")
                        new_zip = input("Enter the new zip code: ")
                        new_city = input("Enter the new city: ")
                        success = hotel_manager.update_hotel_address(hotel_id, new_street, new_zip, new_city)
                        if success:
                            print("Hotel address updated successfully.")
                        else:
                            print("Failed to update the hotel address.")

                    case '4':
                        room_number = input("Enter the room number to update: ")
                        new_type = input("Enter the new room type: ")
                        new_price = validate("Enter the new price: ", "Invalid price. Please enter a valid number.",
                                             float, allow_back=True)
                        if new_price == 'back':
                            continue
                        success = hotel_manager.update_room(hotel_id, room_number, new_type, new_price)
                        if success:
                            print("Room updated successfully.")
                        else:
                            print("Failed to update the room.")

                    case _:
                        print("Invalid choice.")

            case '4':
                hotels = hotel_manager.list_hotels()
                if hotels:
                    for hotel in hotels:
                        print(
                            f"ID: {hotel.id}, Name: {hotel.name}, Stars: {hotel.stars}, Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
                else:
                    print("No hotels found.")

            case '5':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to list rooms: "))
                    rooms = hotel_manager.list_hotel_rooms(hotel_id_input)
                    if rooms:
                        for room in rooms:
                            print(
                                f"Room Number: {room.number}, Type: {room.type}, Max Guests: {room.max_guests}, Description: {room.description}, Amenities: {room.amenities}, Price: {room.price}")
                    else:
                        print("No rooms found or no hotel found with that ID.")
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the Hotel ID.")

            case '6':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")


def user_menu(user_id, user_manager):
    while True:
        print("\nUser Options:")
        print("1. View booking history")
        print("2. Change a booking")
        print("3. Exit User Manager")
        user_choice = input("Please select an option (1-3): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                history = user_manager.get_booking_history(user_id)
                if history:
                    for booking in history:
                        print(
                            f"Booking ID: {booking.id}, Hotel ID: {booking.room.hotel_id}, Room Number: {booking.room_number}, Start Date: {booking.start_date}, End Date: {booking.end_date}, Comment: {booking.comment}")
                else:
                    print("No booking history found.")

            case '2':
                booking_id = validate("Enter booking ID: ", "Invalid booking ID!", int, allow_back=True)
                if booking_id == 'back':
                    continue

                new_details = {}
                new_date = input("Enter new start date (YYYY-MM-DD) (or leave empty to skip): ")
                if new_date:
                    new_details['start_date'] = new_date
                new_end_date = input("Enter new end date (YYYY-MM-DD) (or leave empty to skip): ")
                if new_end_date:
                    new_details['end_date'] = new_end_date
                new_room_id = input("Enter new room ID (or leave empty to skip): ")
                if new_room_id:
                    new_details['room_number'] = new_room_id
                new_hotel_id = input("Enter new hotel ID (or leave empty to skip): ")
                if new_hotel_id:
                    new_details['room_hotel_id'] = new_hotel_id

                if not new_details:
                    print("No changes provided.")
                    continue

                success = user_manager.change_booking(booking_id, new_details)
                if success:
                    print("Booking updated successfully.")
                else:
                    print("Failed to update the booking.")

            case '3':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")


if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "data/hotel_reservation.db")
    user_manager = UserManager(db_path)
    hotel_manager = HotelManager(db_path)

    while True:
        print("\nOptions:")
        print("1. Add a new user")
        print("2. Authenticate a user")
        print("3. Exit User Manager")
        user_choice = input("Please select an option (1-3): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                username = validate("Enter username: ", "Invalid username!", str, allow_back=True)
                if username == 'back':
                    continue

                password = validate("Enter password: ", "Invalid password!", str, allow_back=True)
                if password == 'back':
                    continue

                role_id = validate("Enter Role ID: ", "Invalid Role ID!", int, allow_back=True)
                if role_id == 'back':
                    continue

                try:
                    user_id = user_manager.add_user(username, password, role_id)
                    print(f"User '{username}' with ID {user_id} has been added.")
                except ValueError as e:
                    print(e)

            case '2':
                username = input("Enter username: ")
                password = input("Enter password: ")
                result = user_manager.authenticate_user(username, password)
                if not result:
                    print("Wrong Username or Password.")
                else:
                    role = user_manager.get_user_role(result.id)
                    if role.name == 'administrator':
                        admin_menu(hotel_manager)
                    elif role.name == 'registered_user':
                        user_menu(result.id, user_manager)
                    else:
                        print("Unrecognized role.")

            case '3':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")



--------------------------

Backup SearchManager 30.05.01:02

import os
from pathlib import Path

from data_access.data_base import init_db
from sqlalchemy import select, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from data_models.models import *


class SearchManager(object):
    # "->" attaches meta-data to objects and functions (describing their parameters and return values)
    def __init__(self) -> None:
        self.__load_db()

    def __load_db(self):
        # Ensure the environment Variable is set
        if not os.environ.get("DB_FILE"):  # DB_FILE = environment variable
            raise ValueError("You have to define the environment variable 'DB_FILE'")
        self.__db_filepath = Path(os.environ.get("DB_FILE"))

        # Ensure the db file exists, if not initialize a new db with or without example data
        # You have to delete the db file, if you need a new fresh db.
        if not self.__db_filepath.is_file():
            init_db(str(self.__db_filepath), generate_example_data=True)

        self._engine = create_engine(f'sqlite:///{self.__db_filepath}')
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def get_hotels(self, name: str = "", city: str = ""):
        query = select(Hotel)
        if name != "":
            query = query.where(Hotel.name.like(f'%{name}%'))
        if city != "":
            query = query.join(Address).where(Address.city.like(f"%{city}%"))
        print(query)
        return self._session.execute(query).scalars().all()

    def get_hotels_by_name(self, name: str = ""):
        query = select(Hotel)
        if name != "":
            query = query.where(Hotel.name.like(f'%{name}'))
        print(query)
        return self._session.execute(query).scalars().all()

    def get_hotels_by_city(self, city: str = ""):
        query = select(Hotel)
        if city != "":
            query = query.join(Address).where(Address.city.like(f"%{city}%"))
        print(query)
        return self._session.execute(query).scalars().all()


# shows result of search
def show(hotels):
    for hotel in hotels:
        print("-------------------------------------------------------")
        print(hotel)
        print("-------------------------------------------------------")


if __name__ == '__main__':
    # This is only for testing without Application

    # You should set the variable in the run configuration
    # Because we are executing this file in the folder ./business/
    # we need to relatively navigate first one folder up and therefore,
    # use ../data in the path instead of ./data
    # if the environment variable is not set, set it to a default
    if not os.environ.get('DB_FILE'):
        os.environ['DB_FILE'] = '../data/test.db'
    search_manager = SearchManager()
    all_hotels = search_manager.get_hotels()
    for hotel in all_hotels:
        print(hotel)

# if __name__ == '__main__':
#     # DB_FILE = ("../data/hotel_reservation.db")
#     if not os.environ.get("DB_FILE"):
#         os.environ["DB_FILE"] = input("Enter relative Path to db file: ")
#         while not Path(os.environ.get("DB_FILE")).parent.is_dir():
#             os.environ["DB_FILE"] = input("Enter relative Path to db file: ")
#     search_manager = SearchManager()
#     all_hotels = search_manager.get_hotels()
#     show(all_hotels)
#     all_hotels = search_manager.get_hotels()
#     input("Press Enter to continue...")
#
#     city_in = input('City: ')
#     hotels_by_city = search_manager.get_hotels_by_city(city_in)
#     show(hotels_by_city)
#     input("Press Enter to continue...")
#
#     name_in = input('Name: ')
#     city_in = input('City: ')
#     found_hotels = search_manager.get_hotels(name_in, city_in)
#     show(found_hotels)
#     input("Press Enter to continue...")



---------

Backup ReservationManager 30.05. 01:02

from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import Guest, Address, Booking, Room, Hotel, Login, RegisteredGuest
import os

class ReservationManager(object):
    def __init__(self, database_path: Path):
        self.__engine = create_engine(f'sqlite:///{database_path}', echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_all_hotels(self) -> None:
        query = select(Hotel)
        all_hotels = self.__session.execute(query).scalars().all()
        self.show_hotels(all_hotels)

    def show_hotels(self, hotels: list[Hotel]) -> None:
        for hotel in hotels:
            print(f'Name: {hotel.name}, Location: {hotel.address.city}')

    def get_all_rooms(self) -> list[Room]:
        query = select(Room)
        result = self.__session.execute(query).scalars().all()
        return result

    def check_login(self, username: str, password: str):
        query = select(Login).where(Login.username == username).where(Login.password == password)
        result = self.__session.execute(query).scalars().first()
        return result

    def book_room(self, firstname, lastname, email, room_id, hotel_id, start_date, end_date):
        guest = Guest(firstname=firstname, lastname=lastname, email=email, address=Address(street="", zip="", city=""))
        self.__session.add(guest)
        self.__session.commit()

        room = self.__session.query(Room).filter_by(hotel_id=hotel_id, number=room_id).first()
        if not room:
            raise ValueError("Room not found")

        booking = Booking(room=room, guest=guest, number_of_guests=1, start_date=start_date, end_date=end_date)
        self.__session.add(booking)
        self.__session.commit()

        return booking

    def generate_reservation_text(self, booking_id):
        booking = self.__session.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            raise ValueError("Booking not found")

        text_content = (
            f"Reservation Details for Booking ID: {booking.id}\n"
            f"Guest: {booking.guest.firstname} {booking.guest.lastname}\n"
            f"Email: {booking.guest.email}\n"
            f"Hotel: {booking.room.hotel.name}\n"
            f"Room: {booking.room.number}\n"
            f"Check-in Date: {booking.start_date}\n"
            f"Check-out Date: {booking.end_date}\n"
        )

        text_file_path = f"reservation_{booking.id}.txt"
        with open(text_file_path, 'w') as file:
            file.write(text_content)

        return text_file_path

    def book_room_user(self, user_id: int, room_id: int):
        room = self.__session.query(Room).filter_by(number=room_id).first()
        if not room:
            return f"Room {room_id} does not exist."

        if room.is_booked:
            return f"Room {room_id} is already booked."

        booking = Booking(guest_id=user_id, room_hotel_id=room.hotel_id, room_number=room_id)
        room.is_booked = True
        self.__session.add(booking)
        self.__session.commit()
        return f"Room {room_id} has been successfully booked."

    def cancel_reservation(self, booking_id: int):
        booking = self.__session.query(Booking).filter_by(id=booking_id).first()
        if not booking:
            return f"No reservation found for Booking ID {booking_id}."

        room = self.__session.query(Room).filter_by(hotel_id=booking.room_hotel_id, number=booking.room_number).first()
        if not room:
            return f"Room {booking.room_number} does not exist."

        self.__session.delete(booking)
        room.is_booked = False
        self.__session.commit()
        return f"Reservation for Booking ID {booking_id} has been cancelled."


---------------------

Backup UserManager 30.05. 01:02


from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from pathlib import Path
from data_access.data_base import init_db
from data_models.models import Login, Booking, Role
import os

class UserManager:
    def __init__(self, db_path) -> None:
        self.__load_db(db_path)

    def __load_db(self, db_path):
        self.__db_filepath = Path(db_path)

        if not self.__db_filepath.is_file():
            init_db(str(self.__db_filepath), generate_example_data=True)

        self._engine = create_engine(f"sqlite:///{self.__db_filepath}")
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def add_user(self, username, password, role_id):
        # Prüfen, ob der Benutzername bereits existiert
        existing_user = self._session.query(Login).filter_by(username=username).first()
        if existing_user:
            raise ValueError(f"Username '{username}' already exists.")

        # Prüfen, ob die Rolle existiert
        role = self._session.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role with ID {role_id} does not exist.")

        new_user = Login(username=username, password=password, role_id=role_id)
        self._session.add(new_user)
        self._session.commit()
        return new_user.id

    def authenticate_user(self, username, password):
        query = select(Login).where(Login.username == username).where(Login.password == password)
        result = self._session.execute(query).scalars().one_or_none()
        return result

    def get_user_role(self, user_id):
        query = select(Role).join(Login).where(Login.id == user_id)
        result = self._session.execute(query).scalars().one_or_none()
        return result

    def get_booking_history(self, user_id):
        query = select(Booking).where(Booking.guest_id == user_id)
        result = self._session.execute(query).scalars().all()
        return result

    def change_booking(self, booking_id, new_details):
        booking = self._session.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            for key, value in new_details.items():
                setattr(booking, key, value)
            self._session.commit()
            return True
        return False


--------------


Backup

