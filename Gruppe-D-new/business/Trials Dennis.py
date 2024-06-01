import sys
from pathlib import Path
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, select

from business.DBaseManager import BaseManager
from data_access.data_base import init_db
from data_models.models import Hotel, Address, Room

class HotelManager(BaseManager):

    def delete_hotel(self, hotel_id):
        hotel = self._session.query(Hotel).filter(Hotel.id == hotel_id).first()
        if hotel:
            print(f"Hotel Details:\nID: {hotel.id}\nName: {hotel.name}\nStars: {hotel.stars}\nAddress: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
            confirmation = input("Are you sure you want to delete this hotel? (yes/no): ").strip().lower()
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
            address=Address(street=street,
                            zip=zip,
                            city=city),
            rooms=rooms
        )

        self._session.add(hotel)
        self._session.commit()

        query = select(Hotel).where(Hotel.name == hotel_name)
        result = self._session.execute(query).scalars().all()
        print(result)

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
            if user_input >= min and user_input <= max:
                return user_input
            else: print(error_msg)

    def update_hotel(self):
        hotel_id = input("Enter the Hotel ID to update: ")
        hotel = self._session.query(Hotel).filter(Hotel.id == hotel_id).first()
        if not hotel:
            print("No hotel found with that ID.")
            return

        print("Which attribute would you like to update?")
        print("1. Hotel Name")
        print("2. Hotel Stars")
        print("3. Hotel Address")
        print("4. Room Details")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print(f"Current Hotel Name: {hotel.name}")
            new_name = input("Enter the new name for the hotel: ")
            hotel.name = new_name
            print(f"New Hotel Name: {hotel.name}")

        elif choice == '2':
            new_stars = input("Enter the new star rating (1-5): ")
            try:
                hotel.stars = int(new_stars)
            except ValueError:
                print("Invalid input. Stars must be an integer.")
                return

        elif choice == '3':
            new_street = input("Enter the new street: ")
            new_zip = input("Enter the new zip code: ")
            new_city = input("Enter the new city: ")
            if not hotel.address:
                hotel.address = Address()
            hotel.address.street = new_street
            hotel.address.zip = new_zip
            hotel.address.city = new_city

        elif choice == '4':
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

        else:
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
        print("4. Exit Manager")
        user_choice = input("Please select an option (1-4): ")

        if user_choice == '1':
            hotel_name_input = manager.validate("Hotel Name: ", "Invalid Hotel Name!", str)
            hotel_stars_input = manager.validate_in_range("Hotel Stars: ", "Invalid Stars!", int, 0, 5)
            street_input = manager.validate("Street: ", "Invalid Street!", str)
            zip_input = manager.validate("Zip Code: ", "Invalid Zip Code!", str)
            city_input = manager.validate("City: ", "Invalid City!", str)

            room_number_input = manager.validate_in_range("Room number: ", "Invalid Room Number!", int, 1, sys.maxsize)
            room_type_input = manager.validate("Enter room type: ", "Invalid Room Type!", str)
            room_max_guests_input = manager.validate_in_range("Room max. guests: ", "Invalid Guest Number!", int, 1,
                                                              sys.maxsize)
            room_description_input = manager.validate("Room description: ", "Invalid Room Description!", str)
            room_amenities_input = manager.validate("Amenities: ", "Invalid Amenities!", str)
            room_price_input = manager.validate_in_range("Price: ", "Invalid Price!", float, 0, sys.maxsize)

            rooms = [Room(number=room_number_input,
                          type=room_type_input,
                          max_guests=room_max_guests_input,
                          description=room_description_input,
                          amenities=room_amenities_input,
                          price=room_price_input)]

            manager.add_hotel(hotel_name_input, hotel_stars_input, street_input, zip_input, city_input, rooms)

        elif user_choice == '2':
            try:
                hotel_id_input = int(input("Please enter the Hotel ID to delete: "))
                manager.delete_hotel(hotel_id_input)
            except ValueError:
                print("Invalid input. Please enter a valid integer for the Hotel ID.")

        elif user_choice == '3':
            manager.update_hotel()

        elif user_choice == '4':
            print("Exiting the program.")
            break

        else:
            print("Invalid option selected. Please try again.")
