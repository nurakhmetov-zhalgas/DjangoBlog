from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

URL_ABOUT_AUTHOR = reverse('about:author')
URL_ABOUT_TECH = reverse('about:tech')


class AboutURLTests(TestCase):
    def test_about_urls_exists_at_desired_locataion(self):
        """ Проверка страниц приложения about прошла успешна """
        adress_status = {
            URL_ABOUT_AUTHOR: HTTPStatus.OK,
            URL_ABOUT_TECH: HTTPStatus.OK
        }
        for address, expected_status in adress_status.items():
            with self.subTest(adress=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, expected_status)

    def test_about_urls_use_correct_template(self):
        """Проверка шаблонов приложения about прошла успешна"""
        addres_template = {
            URL_ABOUT_AUTHOR: 'about/author.html',
            URL_ABOUT_TECH: 'about/tech.html'
        }
        for adress, expected_template in addres_template.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, expected_template)
