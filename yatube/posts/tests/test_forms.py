from http import HTTPStatus

from posts.forms import PostForm
from posts.models import Group, Post, User

from django.test import Client, TestCase
from django.urls import reverse

POST_CREATE_URL = 'posts:post_create'
PROFILE_URL = 'posts:profile'
POST_EDIT_URL = 'posts:post_edit'

POST_TEXT_OLD = 'First check'
POST_TEXT_NEW = 'Second check'
INFO_USER = 'author'
POST_TEXT = 'Test post'
POST_TITLE = 'Test group'
POST_SLUG = 'slug1'
POST_DESCRIPTION = 'Test description'


class PostFormTests_1(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=INFO_USER)
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=POST_TITLE,
            slug=POST_SLUG,
            description=POST_DESCRIPTION,
        )
        cls.form = PostForm()

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT_OLD,
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse(POST_CREATE_URL),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                PROFILE_URL, kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, POST_TEXT_OLD)
        self.assertEqual(first_object.group.title, POST_TITLE)
        self.assertEqual(first_object.author.username, INFO_USER)

    def test_edit_post(self):
        """Валидная форма редактирует пост в Post."""
        form_data = {
            'text': POST_TEXT_NEW,
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse(POST_EDIT_URL, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        update_object = response.context['post']
        self.assertEqual(update_object.text, POST_TEXT_NEW)
        self.assertEqual(update_object.group.title, POST_TITLE)
        self.assertEqual(update_object.author.username, INFO_USER)
