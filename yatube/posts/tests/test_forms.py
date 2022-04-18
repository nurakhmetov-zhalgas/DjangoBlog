import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
URL_INDEX = reverse('posts:index')
GROUP_SLUG = 'test-slug'
URL_GROUP = reverse('posts:group_posts', args=[GROUP_SLUG])
AUTHOR_USERNAME = 'pleakleeeeeeey'
URL_AUTHOR_PROFILE = reverse('posts:profile', args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse('posts:post_create')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_comment_author = User.objects.create_user(
            username='test_comment_author'
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug=GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.test_group_for_edit = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.test_post = Post.objects.create(
            author=cls.test_post_author,
            text='Тестовый пост',
            group=cls.test_group,
        )
        cls.URL_TEST_POST_DETAIL = reverse(
            'posts:post_detail',
            args=[cls.test_post.id]
        )
        cls.URL_TEST_POST_EDIT = reverse(
            'posts:post_edit',
            args=[cls.test_post.id]
        )
        cls.URL_TEST_POST_COMMENT = reverse(
            'posts:add_comment',
            args=[cls.test_post.id]
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.test_post_author)
        self.comment_author_client = Client()
        self.comment_author_client.force_login(
            PostFormTests.test_comment_author
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост из формы',
            'group': PostFormTests.test_group.pk,
            'image': uploaded,
        }
        response = self.author_client.post(
            URL_CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, URL_AUTHOR_PROFILE)
        added_post = Post.objects.latest('id')
        self.assertEqual(added_post.text, form_data['text'])
        self.assertEqual(added_post.group.pk, form_data['group'])
        self.assertEqual(
            added_post.image,
            f'posts/{form_data["image"]}'
        )

    def test_create_post_anonymous(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост из формы от анонима',
        }
        response = self.client.post(
            URL_CREATE_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response,
            f'/auth/login/?next={URL_CREATE_POST}'
        )

    def test_edit_post_author(self):
        """Редактирование записи в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст изменен',
            'group': PostFormTests.test_group_for_edit.pk
        }
        response = self.author_client.post(
            PostFormTests.URL_TEST_POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PostFormTests.URL_TEST_POST_DETAIL)
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = response.context.get('post')
        self.assertEqual(
            edited_post.author,
            PostFormTests.test_post_author
        )
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(
            edited_post.group.pk,
            form_data['group']
        )

    def test_edit_post_anonymous(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст изменен анонимно',
            'group': PostFormTests.test_group_for_edit.pk
        }
        old_post_text = PostFormTests.test_post.text
        old_post_group_pk = PostFormTests.test_post.group.pk
        response = self.client.post(
            PostFormTests.URL_TEST_POST_EDIT,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(old_post_text, PostFormTests.test_post.text)
        self.assertEqual(old_post_group_pk, PostFormTests.test_post.group.pk)
        self.assertRedirects(
            response,
            f'/auth/login/?next={PostFormTests.URL_TEST_POST_EDIT}'
        )

    def test_comment_post_anonymous(self):
        post_comments = PostFormTests.test_post.comments.count()
        form_data = {
            'text': 'Комментарий отправлен анонимно',
        }
        response = self.client.post(
            PostFormTests.URL_TEST_POST_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            PostFormTests.test_post.comments.count(),
            post_comments
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next={PostFormTests.URL_TEST_POST_COMMENT}'
        )

    def test_comment_post(self):
        post_comments = PostFormTests.test_post.comments.count()
        form_data = {
            'text': 'Тестовый комменты из формы',
        }
        response = self.comment_author_client.post(
            PostFormTests.URL_TEST_POST_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            PostFormTests.test_post.comments.count(),
            post_comments + 1
        )
        self.assertRedirects(response, PostFormTests.URL_TEST_POST_DETAIL)
        added_comment = PostFormTests.test_post.comments.latest('id')
        self.assertEqual(added_comment.text, form_data['text'])
