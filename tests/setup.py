from django.contrib.auth import get_user_model


def get_user():
    return get_user_model().objects.create(username="testuser-" + get_random_string())


def get_random_string(len=5):
    import random
    import string

    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(len)
    )


class UserSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = get_user()
        return cls._instance
