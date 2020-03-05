from django.test import TestCase


class PagesTests(TestCase):

    def test_home_page(self):
        request = self.client.get('/')
        self.assertEqual(request.status_code, 200)
