import os
from business.SearchManager import SearchManager


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


def show_hotels(hotels):
    if not hotels:
        print("No hotels found.")
    for hotel in hotels:
        print("-------------------------------------------------------")
        print(f"Hotel Name: {hotel.name}")
        print(f"Stars: {hotel.stars}")
        print(f"Address: {hotel.address.street}, {hotel.address.zip}, {hotel.address.city}")
        print("-------------------------------------------------------")


if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "data/hotel_reservation.db")
    if not os.environ.get('DB_FILE'):
        os.environ['DB_FILE'] = db_path

    search_manager = SearchManager()

    while True:
        print("\nSearch Options:")
        print("1. Get all hotels")
        print("2. Search hotels by name")
        print("3. Search hotels by city")
        print("4. Exit Search Manager")
        user_choice = input("Please select an option (1-4): ")

        if user_choice == 'back':
            continue

        match user_choice:
            case '1':
                all_hotels = search_manager.get_hotels()
                show_hotels(all_hotels)

            case '2':
                name = validate("Enter hotel name: ", "Invalid name!", str, allow_back=True)
                if name == 'back':
                    continue
                hotels_by_name = search_manager.get_hotels_by_name(name)
                show_hotels(hotels_by_name)

            case '3':
                city = validate("Enter city: ", "Invalid city!", str, allow_back=True)
                if city == 'back':
                    continue
                hotels_by_city = search_manager.get_hotels_by_city(city)
                show_hotels(hotels_by_city)

            case '4':
                print("Exiting the program.")
                break

            case _:
                print("Invalid option selected. Please try again.")
