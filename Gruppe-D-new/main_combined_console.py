from datetime import datetime, date
from business.UserManager import UserManager
from business.HotelManager import HotelManager
from business.SearchManager import SearchManager
from business.ReservationManager import ReservationManager
import os
from data_models.models import Room

def validate(ask_input, error_msg, type_=str, min_val=None, max_val=None):
    while True:
        user_input = input(ask_input)
        try:
            user_input = type_(user_input)
            if min_val is not None and user_input < min_val:
                raise ValueError
            if max_val is not None and user_input > max_val:
                raise ValueError
            return user_input
        except ValueError:
            print(error_msg)

def show_hotels(hotels, search_manager, start_date=None, end_date=None, number_of_guests=None):
    for hotel in hotels:
        print(f"Hotel ID: {hotel.id}, Name: {hotel.name}, Stars: {hotel.stars}, Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
        rooms = search_manager.get_all_rooms(hotel.id, start_date, end_date) if start_date and end_date else hotel.rooms
        for room in rooms:
            availability = "Available" if start_date and end_date else "Not checked"
            print(f"Room Number: {room.number}, Type: {room.type}, Price: {room.price}, Max Guests: {room.max_guests}, Availability: {availability}")
        print("-------------------------------------------------------")

def main_menu():
    print("\nOptions:")
    print("1. Login")
    print("2. Register")
    print("3. Continue as guest")
    print("4. Exit")
    return validate("Please select an option (1-4): ", "Invalid option!", int, 1, 4)

def admin_menu():
    print("\nAdmin Options:")
    print("1. Add Hotel")
    print("2. Delete Hotel")
    print("3. Update Hotel")
    print("4. List Hotels")
    print("5. Logout")
    return validate("Please select an option (1-5): ", "Invalid option!", int, 1, 5)

def user_menu():
    print("\nUser Options:")
    print("1. Search for Hotels")
    print("2. View Booking History")
    print("3. Edit Account")
    print("4. Logout")
    return validate("Please select an option (1-4): ", "Invalid option!", int, 1, 4)

def search_menu():
    print("\nSearch Options:")
    print("1. Search by availability")
    print("2. Browse hotels")
    print("3. Exit")
    return validate("Please select an option (1-3): ", "Invalid option!", int, 1, 3)

def update_menu():
    print("\nUpdate Options:")
    print("1. Update Hotel Name")
    print("2. Update Hotel Stars")
    print("3. Update Hotel Address")
    print("4. Update Room")
    print("5. Add Room to Hotel")
    print("6. Exit")
    return validate("Please select an option (1-6): ", "Invalid option!", int, 1, 6)

def update_account_menu():
    print("\nUpdate Account Options:")
    print("1. Update First Name")
    print("2. Update Last Name")
    print("3. Update Email")
    print("4. Update Street")
    print("5. Update Zip")
    print("6. Update City")
    print("7. Update Username")
    print("8. Update Password")
    print("9. Exit")
    return validate("Please select an option (1-9): ", "Invalid option!", int, 1, 9)

if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "data/hotel_reservation.db")
    user_manager = UserManager(db_path)
    hotel_manager = HotelManager(db_path)
    search_manager = SearchManager(db_path)
    reservation_manager = ReservationManager(db_path)

    while True:
        choice = main_menu()

        if choice == 1:  # Login
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = user_manager.login(username, password)
            if user:
                if user_manager.is_current_user_admin():
                    while True:
                        admin_choice = admin_menu()
                        if admin_choice == 1:  # Add Hotel
                            hotel_name = input("Enter hotel name: ")
                            hotel_stars = validate("Enter hotel stars (1-5): ", "Invalid stars!", int, 1, 5)
                            street = input("Enter street: ")
                            zip_code = input("Enter zip code: ")
                            city = input("Enter city: ")

                            rooms = []
                            while True:
                                room_number = input("Enter room number: ")
                                room_type = input("Enter room type: ")
                                room_price = validate("Enter room price: ", "Invalid price!", float)
                                room_description = input("Enter room description: ")
                                room_amenities = input("Enter room amenities: ")
                                room_max_guests = validate("Enter max guests: ", "Invalid number!", int)

                                rooms.append(Room(
                                    number=room_number,
                                    type=room_type,
                                    price=room_price,
                                    description=room_description,
                                    amenities=room_amenities,
                                    max_guests=room_max_guests
                                ))

                                another = validate("Add another room? (yes/no): ", "Invalid input!", str)
                                if another.lower() != 'yes':
                                    break

                            hotel = hotel_manager.add_hotel(hotel_name, hotel_stars, street, zip_code, city, rooms)
                            print(f"Hotel '{hotel_name}' added with ID {hotel.id}")

                        elif admin_choice == 2:  # Delete Hotel
                            hotels = hotel_manager.list_hotels()
                            show_hotels(hotels, search_manager)
                            hotel_id = validate("Enter hotel ID to delete: ", "Invalid ID!", int)
                            confirm = validate("Are you sure you want to delete this hotel? (yes/no): ", "Invalid input!", str)
                            if confirm.lower() == 'yes':
                                if hotel_manager.delete_hotel(hotel_id):
                                    print("Hotel deleted successfully.")
                                else:
                                    print("Hotel not found.")

                        elif admin_choice == 3:  # Update Hotel
                            hotels = hotel_manager.list_hotels()
                            show_hotels(hotels, search_manager)
                            hotel_id = validate("Enter hotel ID to update: ", "Invalid ID!", int)
                            hotel = hotel_manager.get_hotel(hotel_id)
                            if not hotel:
                                print("Hotel not found.")
                                continue

                            while True:
                                update_choice = update_menu()
                                if update_choice == 1:  # Update Hotel Name
                                    new_name = input("Enter new hotel name: ")
                                    if hotel_manager.update_hotel_name(hotel_id, new_name):
                                        print("Hotel name updated successfully.")
                                    else:
                                        print("Failed to update hotel name.")

                                elif update_choice == 2:  # Update Hotel Stars
                                    new_stars = validate("Enter new hotel stars (1-5): ", "Invalid stars!", int, 1, 5)
                                    if hotel_manager.update_hotel_stars(hotel_id, new_stars):
                                        print("Hotel stars updated successfully.")
                                    else:
                                        print("Failed to update hotel stars.")

                                elif update_choice == 3:  # Update Hotel Address
                                    new_street = input("Enter new street: ")
                                    new_zip = input("Enter new zip code: ")
                                    new_city = input("Enter new city: ")
                                    if hotel_manager.update_hotel_address(hotel_id, new_street, new_zip, new_city):
                                        print("Hotel address updated successfully.")
                                    else:
                                        print("Failed to update hotel address.")

                                elif update_choice == 4:  # Update Room
                                    rooms = hotel_manager.list_hotel_rooms(hotel_id)
                                    for room in rooms:
                                        print(f"Room Number: {room.number}, Type: {room.type}, Price: {room.price}, Max Guests: {room.max_guests}, Description: {room.description}, Amenities: {room.amenities}")
                                    room_number = input("Enter room number to update: ")
                                    new_type = input("Enter new room type: ")
                                    new_price = validate("Enter new room price: ", "Invalid price!", float)
                                    new_description = input("Enter new room description: ")
                                    new_amenities = input("Enter new room amenities: ")
                                    new_max_guests = validate("Enter new max guests: ", "Invalid number!", int)
                                    if hotel_manager.update_room(hotel_id, room_number, new_type, new_price, new_description, new_amenities, new_max_guests):
                                        print("Room updated successfully.")
                                    else:
                                        print("Failed to update room.")

                                elif update_choice == 5:  # Add Room to Hotel
                                    room_number = input("Enter room number: ")
                                    room_type = input("Enter room type: ")
                                    room_price = validate("Enter room price: ", "Invalid price!", float)
                                    room_description = input("Enter room description: ")
                                    room_amenities = input("Enter room amenities: ")
                                    room_max_guests = validate("Enter max guests: ", "Invalid number!", int)
                                    if hotel_manager.add_room_to_hotel(hotel_id, room_number, room_type, room_price, room_description, room_amenities, room_max_guests):
                                        print("Room added successfully.")
                                    else:
                                        print("Failed to add room.")

                                elif update_choice == 6:
                                    break

                        elif admin_choice == 4:  # List Hotels
                            hotels = hotel_manager.list_hotels()
                            show_hotels(hotels, search_manager)

                        elif admin_choice == 5:  # Logout
                            user_manager.logout()
                            break

                else:
                    while True:
                        user_choice = user_menu()
                        if user_choice == 1:  # Search for Hotels
                            while True:
                                search_choice = search_menu()
                                if search_choice == 1:  # Search by availability
                                    start_date = validate("Enter start date (YYYY-MM-DD): ", "Invalid date!", str)
                                    end_date = validate("Enter end date (YYYY-MM-DD): ", "Invalid date!", str)
                                    number_of_guests = validate("Enter number of guests: ", "Invalid number!", int)
                                    hotels = search_manager.get_hotels()
                                    filtered_hotels = []
                                    for hotel in hotels:
                                        available_rooms = search_manager.get_available_rooms(hotel.id, start_date, end_date, number_of_guests)
                                        if available_rooms:
                                            filtered_hotels.append(hotel)
                                    show_hotels(filtered_hotels, search_manager, start_date, end_date, number_of_guests)

                                    if filtered_hotels:
                                        hotel_id = validate("Enter hotel ID to book: ", "Invalid ID!", int)
                                        room_number = validate("Enter room number to book: ", "Invalid number!", str)
                                        confirm = validate("Do you want to proceed with the booking? (yes/no): ", "Invalid input!", str)
                                        if confirm.lower() == 'yes':
                                            booking = reservation_manager.book_room_guest(hotel_id, room_number, start_date, end_date, number_of_guests)
                                            print(f"Booking confirmed. Total price: {booking.total_price}")

                                elif search_choice == 2:  # Browse hotels
                                    hotels = search_manager.get_hotels()
                                    show_hotels(hotels, search_manager)
                                    hotel_id = validate("Enter hotel ID to view rooms: ", "Invalid ID!", int)
                                    start_date = validate("Enter start date (YYYY-MM-DD): ", "Invalid date!", str)
                                    end_date = validate("Enter end date (YYYY-MM-DD): ", "Invalid date!", str)
                                    number_of_guests = validate("Enter number of guests: ", "Invalid number!", int)
                                    rooms = search_manager.get_available_rooms(hotel_id, start_date, end_date, number_of_guests)
                                    for room in rooms:
                                        print(f"Room Number: {room.number}, Type: {room.type}, Price: {room.price}, Max Guests: {room.max_guests}, Description: {room.description}, Amenities: {room.amenities}")

                                elif search_choice == 3:
                                    break

                        elif user_choice == 2:
                            bookings = user_manager.get_booking_history(user_manager.get_current_user().id)
                            for booking in bookings:
                                print(f"Booking ID: {booking.id}, Hotel: {booking.room.hotel.name}, Room Number: {booking.room.number}, Start Date: {booking.start_date}, End Date: {booking.end_date}, Total Price: {booking.total_price}")

                        elif user_choice == 3:
                            while True:
                                update_account_choice = update_account_menu()
                                if update_account_choice == 1:
                                    firstname = input("Enter new first name: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, firstname=firstname)
                                    print("First name updated." if success else "Failed to update first name.")
                                elif update_account_choice == 2:
                                    lastname = input("Enter new last name: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, lastname=lastname)
                                    print("Last name updated." if success else "Failed to update last name.")
                                elif update_account_choice == 3:
                                    email = input("Enter new email: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, email=email)
                                    print("Email updated." if success else "Failed to update email.")
                                elif update_account_choice == 4:
                                    street = input("Enter new street: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, street=street)
                                    print("Street updated." if success else "Failed to update street.")
                                elif update_account_choice == 5:
                                    zip_code = input("Enter new zip code: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, zip=zip_code)
                                    print("Zip code updated." if success else "Failed to update zip code.")
                                elif update_account_choice == 6:
                                    city = input("Enter new city: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, city=city)
                                    print("City updated." if success else "Failed to update city.")
                                elif update_account_choice == 7:
                                    username = input("Enter new username: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, username=username)
                                    print("Username updated." if success else "Failed to update username.")
                                elif update_account_choice == 8:
                                    password = input("Enter new password: ")
                                    success = user_manager.update_user(user_manager.get_current_user().id, password=password)
                                    print("Password updated." if success else "Failed to update password.")
                                elif update_account_choice == 9:
                                    break

                        elif user_choice == 4:  # Logout
                            user_manager.logout()
                            break

            else:
                print("Login failed. Please check your username and password.")

        elif choice == 2:  # Register
            username = input("Enter username: ")
            password = input("Enter password: ")
            firstname = input("Enter first name: ")
            lastname = input("Enter last name: ")
            email = input("Enter email: ")
            street = input("Enter street: ")
            zip_code = input("Enter zip code: ")
            city = input("Enter city: ")

            user_id = user_manager.add_user(username, password, firstname, lastname, email, street, zip_code, city)
            print(f"User registered successfully with user ID: {user_id}")

        elif choice == 3:  # Continue as guest
            while True:
                search_choice = search_menu()
                if search_choice == 1:  # Search by availability
                    start_date = validate("Enter start date (YYYY-MM-DD): ", "Invalid date!", str)
                    end_date = validate("Enter end date (YYYY-MM-DD): ", "Invalid date!", str)
                    number_of_guests = validate("Enter number of guests: ", "Invalid number!", int)
                    hotels = search_manager.get_hotels()
                    filtered_hotels = []
                    for hotel in hotels:
                        available_rooms = search_manager.get_available_rooms(hotel.id, start_date, end_date, number_of_guests)
                        if available_rooms:
                            filtered_hotels.append(hotel)
                    show_hotels(filtered_hotels, search_manager, start_date, end_date, number_of_guests)

                    if filtered_hotels:
                        hotel_id = validate("Enter hotel ID to book: ", "Invalid ID!", int)
                        room_number = validate("Enter room number to book: ", "Invalid number!", str)
                        confirm = validate("Do you want to proceed with the booking? (yes/no): ", "Invalid input!", str)
                        if confirm.lower() == 'yes':
                            firstname = input("Enter your first name: ")
                            lastname = input("Enter your last name: ")
                            email = input("Enter your email: ")
                            street = input("Enter your street: ")
                            zip_code = input("Enter your zip code: ")
                            city = input("Enter your city: ")
                            booking = reservation_manager.book_room_guest(hotel_id, room_number, start_date, end_date, number_of_guests, firstname, lastname, email, street, zip_code, city)
                            print(f"Booking confirmed. Total price: {booking.total_price}")

                elif search_choice == 2:  # Browse hotels
                    hotels = search_manager.get_hotels()
                    show_hotels(hotels, search_manager)
                    hotel_id = validate("Enter hotel ID to view rooms: ", "Invalid ID!", int)
                    start_date = validate("Enter start date (YYYY-MM-DD): ", "Invalid date!", str)
                    end_date = validate("Enter end date (YYYY-MM-DD): ", "Invalid date!", str)
                    number_of_guests = validate("Enter number of guests: ", "Invalid number!", int)
                    rooms = search_manager.get_available_rooms(hotel_id, start_date, end_date, number_of_guests)
                    for room in rooms:
                        print(f"Room Number: {room.number}, Type: {room.type}, Price: {room.price}, Max Guests: {room.max_guests}, Description: {room.description}, Amenities: {room.amenities}")

                elif search_choice == 3:
                    break

        elif choice == 4:
            break
