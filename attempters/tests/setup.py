from attempters.models import Attempter
from tests.setup import get_user


def get_attempter_data():
    return {
        "email": "attempter@test.com",
        "phone_number": "+38005557778",
    }


def get_invalid_attempter_data():
    return {
        "email": "some@invalid@email.com",
        "phone_number": "+123some_invalid_phone_number",
    }


def get_updated_attempter_data():
    return {
        "email": "updated-attempter@test.com",
        "phone_number": "+38005557778",
    }


def get_attempter():
    attempter_data = get_attempter_data()
    attempter_data["user"] = get_user()

    return Attempter.objects.create(**attempter_data)
