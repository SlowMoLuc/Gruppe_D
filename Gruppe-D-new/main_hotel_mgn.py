import sys
from business.HotelManager import HotelManager
from data_models.models import Hotel, Room, Address


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
        if min <= user_input <= max:
            return user_input
        else:
            print(error_msg)


def validate_yes_no(ask_input):
    while True:
        user_input = input(ask_input).strip().lower()
        if user_input in ['yes', 'no']:
            return user_input
        else:
            print("Please answer with 'yes' or 'no'.")


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
                hotel_name_input = validate("Hotel Name: ", "Invalid Hotel Name!", str)
                hotel_stars_input = validate_in_range("Hotel Stars: ", "Invalid Stars!", int, 0, 5)
                street_input = validate("Street: ", "Invalid Street!", str)
                zip_input = validate("Zip Code: ", "Invalid Zip Code!", str)
                city_input = validate("City: ", "Invalid City!", str)

                rooms = []

                while True:
                    room_number_input = validate_in_range("Room number: ", "Invalid Room Number!", int, 1, sys.maxsize)
                    if manager.room_number_exists(room_number_input, rooms):
                        print(
                            f"Room number {room_number_input} already exists for this hotel. Please enter a different room number.")
                    else:
                        room_type_input = validate("Enter room type: ", "Invalid Room Type!", str)
                        room_max_guests_input = validate_in_range("Room max. guests: ", "Invalid Guest Number!", int, 1,
                                                                  sys.maxsize)
                        room_description_input = validate("Room description: ", "Invalid Room Description!", str)
                        room_amenities_input = validate("Amenities: ", "Invalid Amenities!", str)
                        room_price_input = validate_in_range("Price: ", "Invalid Price!", float, 0, sys.maxsize)

                        rooms.append(
                            Room(number=room_number_input, type=room_type_input, max_guests=room_max_guests_input,
                                 description=room_description_input, amenities=room_amenities_input,
                                 price=room_price_input))

                        add_another = validate_yes_no("Would you like to add another room? (yes/no): ")
                        if add_another != 'yes':
                            break

                new_hotel = manager.add_hotel(hotel_name_input, hotel_stars_input, street_input, zip_input, city_input,
                                              rooms)
                print(f"Hotel '{new_hotel.name}' with ID {new_hotel.id} has been added.")

            case '2':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to delete: "))
                    success = manager.delete_hotel(hotel_id_input)
                    if success:
                        print(f"Hotel with ID {hotel_id_input} has been deleted.")
                    else:
                        print("No hotel found with that ID.")
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the Hotel ID.")

            case '3':
                hotel_id = input("Enter the Hotel ID to update: ")
                hotel = manager._session.query(Hotel).filter(Hotel.id == hotel_id).first()
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
                        success = manager.update_hotel_name(hotel_id, new_name)
                        if success:
                            print(f"New Hotel Name: {new_name}")
                        else:
                            print("Failed to update the hotel name.")

                    case '2':
                        new_stars = input("Enter the new star rating (1-5): ")
                        try:
                            new_stars = int(new_stars)
                            success = manager.update_hotel_stars(hotel_id, new_stars)
                            if success:
                                print(f"New Hotel Stars: {new_stars}")
                            else:
                                print("Failed to update the hotel stars.")
                        except ValueError:
                            print("Invalid input. Stars must be an integer.")

                    case '3':
                        new_street = input("Enter the new street: ")
                        new_zip = input("Enter the new zip code: ")
                        new_city = input("Enter the new city: ")
                        success = manager.update_hotel_address(hotel_id, new_street, new_zip, new_city)
                        if success:
                            print("Hotel address updated successfully.")
                        else:
                            print("Failed to update the hotel address.")

                    case '4':
                        room_number = input("Enter the room number to update: ")
                        new_type = input("Enter the new room type: ")
                        new_price = input("Enter the new price: ")
                        try:
                            new_price = float(new_price)
                            success = manager.update_room(hotel_id, room_number, new_type, new_price)
                            if success:
                                print("Room updated successfully.")
                            else:
                                print("Failed to update the room.")
                        except ValueError:
                            print("Invalid price. Please enter a valid number.")

                    case _:
                        print("Invalid choice.")

            case '4':
                hotels = manager.list_hotels()
                if hotels:
                    for hotel in hotels:
                        print(
                            f"ID: {hotel.id}, Name: {hotel.name}, Stars: {hotel.stars}, Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
                else:
                    print("No hotels found.")

            case '5':
                try:
                    hotel_id_input = int(input("Please enter the Hotel ID to list rooms: "))
                    rooms = manager.list_hotel_rooms(hotel_id_input)
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
