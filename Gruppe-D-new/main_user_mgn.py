import os
from business.UserManager import UserManager
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


def validate_yes_no(ask_input):
    while True:
        user_input = input(ask_input).strip().lower()
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

        match user_choice:
            case '1':
                hotel_name_input = validate("Hotel Name: ", "Invalid Hotel Name!", str)

                hotel_stars_input = validate("Hotel Stars: ", "Invalid Stars!", int)

                street_input = validate("Street: ", "Invalid Street!", str)

                zip_input = validate("Zip Code: ", "Invalid Zip Code!", str)

                city_input = validate("City: ", "Invalid City!", str)

                rooms = []

                while True:
                    room_number_input = validate("Room number: ", "Invalid Room Number!", int)

                    room_type_input = validate("Enter room type: ", "Invalid Room Type!", str)

                    room_max_guests_input = validate("Room max. guests: ", "Invalid Guest Number!", int)

                    room_description_input = validate("Room description: ", "Invalid Room Description!", str)

                    room_amenities_input = validate("Amenities: ", "Invalid Amenities!", str)

                    room_price_input = validate("Price: ", "Invalid Price!", float)

                    rooms.append(Room(number=room_number_input, type=room_type_input, max_guests=room_max_guests_input,
                                      description=room_description_input, amenities=room_amenities_input,
                                      price=room_price_input))

                    add_another = validate_yes_no("Would you like to add another room? (yes/no): ")
                    if add_another == 'no':
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
                                             "Invalid input. Stars must be between 1 and 5.", int)
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
                                             float)
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
                booking_id = validate("Enter booking ID: ", "Invalid booking ID!", int)

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

        match user_choice:
            case '1':
                username = validate("Enter username: ", "Invalid username!", str)

                password = validate("Enter password: ", "Invalid password!", str)

                role_id = validate("Enter Role ID: ", "Invalid Role ID!", int)

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
