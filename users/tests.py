import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagerTest(TestCase):
    email = "user@email.com"

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email=self.email, password="123")
        self.assertEqual(user.email, self.email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertEqual(len(user.id), len(uuid.uuid4()))
        with self.assertRaises(AttributeError):  # no username field should be defined
            self.assertIsNone(user.username)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):  # password missing
            User.objects.create_user(email="asd")
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="123")
        with self.assertRaises(ValueError):  # email must be unique
            User.objects.create_user(email=self.email, password="123")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email=self.email, password="123")
        self.assertEqual(admin_user.email, self.email)
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="admin@email.com", password="123", is_superuser=False)