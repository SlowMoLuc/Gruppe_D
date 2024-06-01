import os
from business.ReservationManager import ReservationManager

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
    manager = ReservationManager(db_path)

    while True:
        print("\nOptions:")
        print("1. Book a room as a guest")
        print("2. Generate reservation text file")
        print("3. Book a room as a registered user")
        print("4. Cancel a reservation")
        print("5. Exit Reservation Manager")
        user_choice = input("Please select an option (1-5): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                firstname = validate("Enter firstname: ", "Invalid firstname!", str, allow_back=True)
                if firstname == 'back':
                    continue

                lastname = validate("Enter lastname: ", "Invalid lastname!", str, allow_back=True)
                if lastname == 'back':
                    continue

                email = validate("Enter email: ", "Invalid email!", str, allow_back=True)
                if email == 'back':
                    continue

                room_id = validate("Enter Room ID: ", "Invalid Room ID!", str, allow_back=True)
                if room_id == 'back':
                    continue

                hotel_id = validate("Enter Hotel ID: ", "Invalid Hotel ID!", int, allow_back=True)
                if hotel_id == 'back':
                    continue

                start_date = validate("Enter check-in date (YYYY-MM-DD): ", "Invalid date!", str, allow_back=True)
                if start_date == 'back':
                    continue

                end_date = validate("Enter check-out date (YYYY-MM-DD): ", "Invalid date!", str, allow_back=True)
                if end_date == 'back':
                    continue

                try:
                    booking = manager.book_room(firstname, lastname, email, room_id, hotel_id, start_date, end_date)
                    print(f"Room booked successfully with Booking ID: {booking.id}")
                except ValueError as e:
                    print(e)

            case '2':
                booking_id = validate("Enter Booking ID: ", "Invalid Booking ID!", int, allow_back=True)
                if booking_id == 'back':
                    continue

                try:
                    text_path = manager.generate_reservation_text(booking_id)
                    print(f"Reservation text file generated: {text_path}")
                except ValueError as e:
                    print(e)

            case '3':
                user_id = validate("Enter User ID: ", "Invalid User ID!", int, allow_back=True)
                if user_id == 'back':
                    continue

                room_id = validate("Enter Room ID: ", "Invalid Room ID!", int, allow_back=True)
                if room_id == 'back':
                    continue

                try:
                    result = manager.book_room_user(user_id, room_id)
                    print(result)
                except ValueError as e:
                    print(e)

            case '4':
                booking_id = validate("Enter Booking ID: ", "Invalid Booking ID!", int, allow_back=True)
                if booking_id == 'back':
                    continue

                try:
                    result = manager.cancel_reservation(booking_id)
                    print(result)
                except ValueError as e:
                    print(e)

            case '5':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")
