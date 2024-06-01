from sqlalchemy.orm import joinedload
from sqlalchemy import select
from data_models.models import Login, RegisteredGuest, Guest, Address, Booking, Room
from business.BaseManager import BaseManager
import sys

class UserManager(BaseManager):
    def __init__(self, db_file):
        super(UserManager, self).__init__(db_file)
        self._attempts = 0
        self._current_user = None

    def login(self, username, password):
        query = select(Login).where(Login.username == username, Login.password == password)
        result = self._session.execute(query).scalar_one_or_none()
        self._attempts += 1
        self._current_user = result
        return result

    def has_more_attempts(self):
        return self._attempts < 3

    def logout(self):
        self._current_user = None
        self._attempts = 0

    def get_current_user(self) -> Login:
        return self._current_user

    def get_reg_guest_of(self, login) -> RegisteredGuest:
        query = select(RegisteredGuest).where(RegisteredGuest.login_id == login.id)
        result = self._session.execute(query).scalar_one_or_none()
        return result

    def is_current_user_admin(self):
        return self._current_user and self._current_user.role.access_level == sys.maxsize

    def add_user(self, username, password, firstname, lastname, email, street, zip, city):
        address = Address(street=street, zip=zip, city=city)
        self._session.add(address)
        self._session.commit()

        guest = RegisteredGuest(
            login=Login(username=username, password=password, role_id=2),  # role_id 2 for regular users
            firstname=firstname,
            lastname=lastname,
            email=email,
            address_id=address.id,
            address=address
        )
        self._session.add(guest)
        self._session.commit()
        return guest.id

    def update_user(self, user_id, **kwargs):
        user = self._session.query(RegisteredGuest).filter(RegisteredGuest.id == user_id).first()
        if not user:
            return False

        if 'street' in kwargs or 'zip' in kwargs or 'city' in kwargs:
            if not user.address:
                user.address = Address()
            user.address.street = kwargs.get('street', user.address.street)
            user.address.zip = kwargs.get('zip', user.address.zip)
            user.address.city = kwargs.get('city', user.address.city)

        for attr, value in kwargs.items():
            if hasattr(user, attr):
                setattr(user, attr, value)
            elif hasattr(user.login, attr):
                setattr(user.login, attr, value)

        self._session.commit()
        return True

    def get_booking_history(self, user_id):
        query = select(Booking).where(Booking.guest_id == user_id)
        return self._session.execute(query).scalars().all()

    def update_booking(self, booking_id, start_date, end_date, number_of_guests):
        booking = self._session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False

        # Check room availability excluding the current booking
        available_rooms = self._session.query(Room).join(Booking).filter(
            Booking.room_hotel_id == booking.room_hotel_id,
            Booking.start_date <= end_date,
            Booking.end_date >= start_date,
            Booking.id != booking.id  # Exclude the current booking
        ).all()

        if booking.room_number in [room.number for room in available_rooms]:
            return False

        booking.start_date = start_date
        booking.end_date = end_date
        booking.number_of_guests = number_of_guests
        self._session.commit()
        return True

    def delete_booking(self, booking_id):
        booking = self._session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False

        self._session.delete(booking)
        self._session.commit()
        return True
