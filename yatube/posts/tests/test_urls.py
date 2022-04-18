from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

URL_INDEX = reverse('posts:index')
GROUP_SLUG = 'test-slug'
URL_GROUP = reverse('posts:group_posts', args=[GROUP_SLUG])
AUTHOR_USERNAME = 'pleakleeeeeeey'
URL_AUTHOR_PROFILE = reverse('posts:profile', args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовая группа.Описание'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            author=cls.test_post_author
        )
        cls.URL_TEST_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.test_post.id]
        )
        cls.URL_TEST_POST_EDIT = reverse(
            'posts:post_edit',
            args=[cls.test_post.id]
        )

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.test_post_author)

    def test_posts_urls_exists_at_desired_locataion(self):
        """ Проверка страниц приложения posts прошла успешна."""
        address_status_client = [
            [URL_INDEX, HTTPStatus.OK, self.client],
            [URL_GROUP, HTTPStatus.OK, self.client],
            [URL_AUTHOR_PROFILE, HTTPStatus.OK, self.client],
            [URL_CREATE_POST, HTTPStatus.OK, self.authorized_client],
            [URL_CREATE_POST, HTTPStatus.FOUND, self.client],
            [
                PostURLTests.URL_TEST_POST_DETAIL,
                HTTPStatus.OK,
                self.client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                HTTPStatus.OK,
                self.author_client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                HTTPStatus.FOUND,
                self.client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                HTTPStatus.FOUND,
                self.authorized_client
            ],
        ]
        for url_test in address_status_client:
            adress, status, client = url_test
            self.assertEqual(
                client.get(adress).status_code,
                status, f'{adress} для {client} работает неверено'
            )

    def test_posts_urls_use_correct_template(self):
        """Проверка шаблонов приложения posts прошла успешна."""
        addres_template_guest_client = {
            URL_INDEX: 'posts/index.html',
            URL_GROUP: 'posts/group_list.html',
            URL_AUTHOR_PROFILE: 'posts/profile.html',
            PostURLTests.URL_TEST_POST_DETAIL: 'posts/post_detail.html',
            PostURLTests.URL_TEST_POST_EDIT: 'posts/create_post.html',
            URL_CREATE_POST: 'posts/create_post.html'
        }
        for adress, expected_template in addres_template_guest_client.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(
                    response,
                    expected_template,
                    f'неверный шаблон - {expected_template}'
                    f'для адресса {adress}'
                )

    def test_post_urls_redirect_correct(self):
        adress_redirect_client = [
            [
                URL_CREATE_POST,
                f'/auth/login/?next={URL_CREATE_POST}',
                self.client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                PostURLTests.URL_TEST_POST_DETAIL,
                self.authorized_client
            ],
            [
                PostURLTests.URL_TEST_POST_EDIT,
                f'/auth/login/?next={PostURLTests.URL_TEST_POST_EDIT}',
                self.client
            ]
        ]
        for redirect_test in adress_redirect_client:
            adress, expected_redirect, client = redirect_test
            response = client.get(adress, follow=True)
            self.assertRedirects(
                response,
                expected_redirect
            )
