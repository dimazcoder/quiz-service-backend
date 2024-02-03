from attempters.models import Attempter
from attempters.tests.setup import get_attempter_data
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from phonenumber_field.phonenumber import PhoneNumber
from tests.setup import get_user


class AttempterModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user()
        self.attempter_data = get_attempter_data()
        self.attempter_data["user"] = self.user
        self.attempter = Attempter.objects.create(**self.attempter_data)

    def test_create_attempter(self):
        # attempter = Attempter.objects.create(**self.attempter_data, user=self.user)
        self.assertEqual(self.attempter.email, self.attempter_data["email"])
        self.assertEqual(
            self.attempter.phone_number,
            PhoneNumber.from_string(self.attempter_data["phone_number"]),
        )
        self.assertEqual(self.attempter.user, self.user)

    def test_attempter_str_method(self):
        # attempter = Attempter.objects.create(**self.attempter_data)
        self.assertEqual(str(self.attempter), f"Участник {self.attempter.pk}")

    def test_attempter_created_modified(self):
        # attempter = Attempter.objects.create(**self.attempter_data)
        self.assertIsNotNone(self.attempter.created_at)
        self.assertIsNotNone(self.attempter.modified_at)
        self.assertGreater(self.attempter.modified_at, self.attempter.created_at)

    def test_invalid_phone_number(self):
        with self.assertRaises(ValidationError):
            self.attempter.phone_number = "invalid_phone_number"
            self.attempter.full_clean()
            self.attempter.save()

            # Attempter.objects.create(
            #     email="invalid@example.com", phone_number="12345", user=None
            # )

    def test_unique_user_constraint(self):
        with self.assertRaises(IntegrityError):
            Attempter.objects.create(
                email="another@example.com",
                phone_number="+9876543210",
                user=self.attempter.user,
            )
