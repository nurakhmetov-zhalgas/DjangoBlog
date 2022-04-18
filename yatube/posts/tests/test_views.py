import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
URL_INDEX = reverse('posts:index')
GROUP_SLUG = 'test-slug'
URL_GROUP = reverse('posts:group_posts', args=[GROUP_SLUG])
AUTHOR_USERNAME = 'pleakleeeeeeey'
URL_AUTHOR_PROFILE = reverse('posts:profile', args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            group=cls.test_group,
            author=cls.test_post_author,
            image=uploaded
        )
        cls.URL_TEST_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.test_post.id]
        )
        cls.URL_TEST_POST_EDIT = reverse(
            'posts:post_edit',
            args=[cls.test_post.id]
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostPagesTests.test_post_author)

    def test_post_pages_show_correct_context(self):
        """Шаблоны с постами сформированы с правильным контекстом."""
        addresses = [
            URL_INDEX,
            URL_GROUP,
            URL_AUTHOR_PROFILE,
            PostPagesTests.URL_TEST_POST_DETAIL
        ]
        for address in addresses:
            response = self.author_client.get(address)
            if 'page_obj' in response.context:
                post = response.context.get('page_obj')[0]
            else:
                post = response.context.get('post')
            self.assertEqual(post.author, PostPagesTests.test_post.author)
            self.assertEqual(post.text, PostPagesTests.test_post.text)
            self.assertEqual(post.group, PostPagesTests.test_post.group)
            self.assertEqual(post.pk, PostPagesTests.test_post.pk)
            self.assertEqual(post.image, PostPagesTests.test_post.image)

    def test_group_post_page_show_correct_context(self):
        group = self.author_client.get(URL_GROUP).context.get('group')
        self.assertEqual(group.title, PostPagesTests.test_group.title)
        self.assertEqual(group.slug, PostPagesTests.test_group.slug)
        self.assertEqual(group.pk, PostPagesTests.test_group.pk)
        self.assertEqual(
            group.description,
            PostPagesTests.test_group.description
        )

    def test_profile_page_show_correct_context(self):
        author_page = self.author_client.get(URL_AUTHOR_PROFILE)
        author_page_context = author_page.context
        author = author_page_context.get('author')
        self.assertEqual(
            author.username,
            PostPagesTests.test_post_author.username
        )
        self.assertEqual(author.pk, PostPagesTests.test_post_author.pk)

    def test_create_edit_post_page_contains_expected_context(self):
        addresses = [
            URL_CREATE_POST,
            PostPagesTests.URL_TEST_POST_EDIT
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for address in addresses:
            response = self.author_client.get(address)
            for field, expected_field in form_fields.items():
                with self.subTest(field=field):
                    form_field = response.context.get('form').fields.get(field)
                    self.assertIsInstance(
                        form_field,
                        expected_field,
                        f'Неверный тип для поля {field} в {address}'
                    )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.second_author = User.objects.create_user(
            username='test_second_user'
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовая группа.Описание'
        )
        objs = [
            Post(
                author=cls.first_author,
                text=f'Тестовый пост{i}',
                group=cls.test_group
            ) for i in range(9)
        ]
        Post.objects.bulk_create(objs)
        objs = [
            Post(
                author=cls.second_author,
                text=f'Тестовый пост{i}'
            ) for i in range(4)
        ]
        Post.objects.bulk_create(objs)

    def test_index_first_page_contains_expected_number_posts(self):
        response = self.client.get(URL_INDEX)
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_PER_PAGE
        )

    def test_index_second_page_contains_expected_number_posts(self):
        response = self.client.get(URL_INDEX + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            (Post.objects.count() - settings.POSTS_PER_PAGE)
        )

    def test_group_page_contains_expected_number_posts(self):
        response = self.client.get(URL_GROUP)
        self.assertEqual(
            len(response.context['page_obj']),
            Post.objects.filter(group=PaginatorViewsTest.test_group).count()
        )

    def test_profile_page_contains_expected_number_posts(self):
        response = self.client.get(URL_AUTHOR_PROFILE)
        self.assertEqual(
            len(response.context['page_obj']),
            Post.objects.filter(author=PaginatorViewsTest.first_author).count()
        )


class CacheTest(TestCase):
    """
    при запуске теста в корневой папке проекта повляется мусор,
    который остается после тестов.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_post = Post.objects.create(
            text='Тестовый пост',
            author=cls.test_post_author
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(CacheTest.test_post_author)

    def test_cache(self):
        post_cache = Post.objects.create(
            text='Тестовый пост кэша',
            author=CacheTest.test_post_author
        )
        response_before = self.author_client.get(URL_INDEX)
        post_cache.delete()
        response_after = self.author_client.get(URL_INDEX)
        self.assertEqual(response_before.content, response_after.content)
        cache.clear()
        response_clear = self.author_client.get(URL_INDEX)
        self.assertNotEqual(response_after, response_clear)


class FollowTest(TestCase):
    # создает мусор в корневой папке. Не понимаю почему
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(FollowTest.test_post_author)

    def test_follow(self):
        user_to_follow = User.objects.create_user(
            username='user_to_follow'
        )
        before_follow = Follow.objects.count()
        self.author_client.get(
            reverse('posts:profile_follow', args=[user_to_follow, ])
        )
        self.assertEqual(Follow.objects.count(), before_follow + 1)
        new_follower = Follow.objects.first()
        self.assertEqual(new_follower.author, user_to_follow)
        self.assertEqual(new_follower.user, FollowTest.test_post_author)

    def test_unfollow(self):
        user_to_follow = User.objects.create_user(
            username='new_follower'
        )
        Follow.objects.create(
            author=user_to_follow,
            user=FollowTest.test_post_author
        )
        before_unfollow = Follow.objects.count()
        self.author_client.get(
            reverse('posts:profile_unfollow', args=[user_to_follow, ])
        )
        self.assertEqual(before_unfollow - 1, Follow.objects.count())

    def test_follow_index_show_correct_context(self):
        user_follower = User.objects.create_user(
            username='user_follower'
        )
        follower_client = Client()
        follower_client.force_login(user_follower)
        user_unfollower = User.objects.create_user(
            username='user_unfollower'
        )
        unfollower_client = Client()
        unfollower_client.force_login(user_unfollower)

        follower_client.get(
            reverse(
                'posts:profile_follow',
                args=[FollowTest.test_post_author, ]
            )
        )

        response_follow = follower_client.get(reverse('posts:follow_index'))
        response_unfollow = unfollower_client.get(
            reverse('posts:follow_index')
        )

        unfollow_count_before = len(response_unfollow.context['page_obj'])
        follow_count_before = len(response_follow.context['page_obj'])
        Post.objects.create(
            text='Текст TestFollow',
            author=FollowTest.test_post_author
        )

        response_follow = follower_client.get(reverse('posts:follow_index'))
        response_unfollow = unfollower_client.get(
            reverse('posts:follow_index')
        )

        self.assertEqual(
            follow_count_before + 1,
            len(response_follow.context['page_obj'])
        )
        self.assertEqual(
            unfollow_count_before,
            len(response_unfollow.context['page_obj'])
        )
