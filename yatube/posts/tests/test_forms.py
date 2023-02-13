from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User
from posts.tests import constants as cs

POST_TEXT_OLD = 'First check'
POST_TEXT_NEW = 'Second check'
POST_USER = 'author'
POST_TEXT = 'Test post'
GROUP_TITLE = 'Test group'
GROUP_SLUG = 'slug1'
GROUP_DESCRIPTION = 'Test description'


class PostFormTests_1(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=POST_USER)
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
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
            reverse(cs.POST_CREATE_URL),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                cs.PROFILE_URL, kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, POST_TEXT_OLD)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.author, self.author)

    def test_edit_post(self):
        """Валидная форма редактирует пост в Post."""
        form_data = {
            'text': POST_TEXT_NEW,
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse(cs.POST_EDIT_URL, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        update_object = response.context['post']
        self.assertEqual(update_object.text, POST_TEXT_NEW)
        self.assertEqual(update_object.group, self.group)
        self.assertEqual(update_object.author, self.author)
