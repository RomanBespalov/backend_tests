from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


from ..models import Group, Post

User = get_user_model()

INDEX_URL = 'posts:index'
GROUP_URL = 'posts:group_list'
PROFILE_URL = 'posts:profile'
POST_DETAIL_URL = 'posts:post_detail'
POST_CREATE_URL = 'posts:post_create'
POST_EDIT_URL = 'posts:post_edit'

INDEX_TEMPLATE = 'posts/index.html'
GROUP_TEMPLATE = 'posts/group_list.html'
PROFILE_TEMPLATE = 'posts/profile.html'
POST_DETAIL_TEMPLATE = 'posts/post_detail.html'
POST_CREATE_TEMPLATE = 'posts/create_post.html'
POST_EDIT_TEMPLATE = 'posts/create_post.html'


class PostsURLTests(TestCase):
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

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_url_templates(self):
        """Шаблоны соответствуют URL."""
        data = {
            INDEX_URL: (INDEX_TEMPLATE, {}),
            GROUP_URL: (GROUP_TEMPLATE, {'slug': self.group.slug}),
            PROFILE_URL: (PROFILE_TEMPLATE, {'username': self.author}),
            POST_DETAIL_URL: (POST_DETAIL_TEMPLATE, {'post_id': self.post.id}),
        }

        for url, params in data.items():
            template, arguments = params
            response = self.client.get(
                reverse(url, kwargs=arguments)
            )
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    response, template
                )

    def test_post_create_url_uses_correct_template(self):
        """Страница create/ использует
        шаблон posts/create_post.html.
        """
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, POST_CREATE_TEMPLATE)

    def test_post_edit_url_uses_correct_template(self):
        """Страница /posts/<int:post_id>/edit/ использует
        шаблон posts/create_post.html.
        """
        response = self.author_client.get(
            reverse(POST_EDIT_URL, kwargs={'post_id': self.post.id})
            )
        self.assertTemplateUsed(response, POST_EDIT_TEMPLATE)

    def test_url_access(self):
        """Страницы доступны всем пользователям."""
        data_access = {
            INDEX_URL: {},
            GROUP_URL: {'slug': self.group.slug},
            PROFILE_URL: {'username': self.author},
            POST_DETAIL_URL: {'post_id': self.post.id},
        }

        for url, params in data_access.items():
            response = self.client.get(
                reverse(url, kwargs=params)
            )
            with self.subTest(url=url):
                self.assertEqual(
                    response.status_code, HTTPStatus.OK
                )

    def test_unexisting_page_redirect_anonymous(self):
        """Несуществующая страница возвращает ошибку 404 всем пользователям."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_post_edit_only_for_author(self):
        """Страница /posts/<int:post_id>/edit/ доступна автору."""
        response = self.author_client.get(
            reverse(POST_EDIT_URL, kwargs={'post_id': self.post.id})
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_redirect_not_author(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет не автора."""
        response = self.authorized_client.get(
            reverse(
                POST_EDIT_URL, kwargs={'post_id': self.post.id}
            ), follow=True
        )
        self.assertRedirects(response, reverse(
            POST_DETAIL_URL, kwargs={'post_id': self.post.id}
            )
        )
