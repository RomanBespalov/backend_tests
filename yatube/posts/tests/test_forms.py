from http import HTTPStatus
import shutil
import tempfile

from ..forms import PostForm
from ..models import Post, Group, User
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_POST_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(POST_ROOT=TEMP_POST_ROOT)
class PostFormTests_1(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Test post',
        )
        cls.group = Group.objects.create(
            title='Test group',
            slug='slug1',
            description='Test description',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_POST_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        # self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'First check',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Second check',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text='Second check',
            ).exists()
        )
