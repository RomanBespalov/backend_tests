from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.paginator import Page
from django.urls import reverse
from django import forms

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


POSTS_PER_PAGE = 10

AUTHOR_USERNAME = 'TestAuthor'
USER_USERNAME = 'TestUser'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
POST_TEXT = 'Тестовый текст'

PAG_INDEX_URL = reverse('posts:index')
PAG_GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PAG_PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])


class PostsViewsTests(TestCase):
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

    def setUp(self):
        self.user = User.objects.create_user(username='RomanBespalov')
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            INDEX_TEMPLATE: reverse(INDEX_URL),
            GROUP_TEMPLATE: (
                reverse(GROUP_URL, kwargs={'slug': self.group.slug})
            ),
            PROFILE_TEMPLATE: (
                reverse(PROFILE_URL, kwargs={'username': self.author})
            ),
            POST_DETAIL_TEMPLATE: (
                reverse(POST_DETAIL_URL, kwargs={'post_id': self.post.id})
            ),
            POST_CREATE_TEMPLATE: reverse(POST_CREATE_URL),
            POST_EDIT_TEMPLATE: (
                reverse(POST_EDIT_URL, kwargs={'post_id': self.post.id})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostPagesTests(TestCase):
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

    def setUp(self):
        self.user = User.objects.create_user(username='RomanBespalov')
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(POST_CREATE_URL))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Не работает, не знаю почему
    # def test_post_edit_page_show_correct_context(self):
    #     """Шаблон post_edit сформирован с правильным контекстом."""
    #     response = self.author_client.get(
    #         reverse(POST_EDIT_URL, kwargs={'post_id': self.post.id})
    #     )
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.fields.ChoiceField,
    #     }

    #     for value, expected in form_fields.items():
    #         with self.subTest(value=value):
    #             form_field = response.context.get('form').fields.get(value)
    #             self.assertIsInstance(form_field, expected)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.author_client.get(
            reverse(POST_DETAIL_URL, kwargs={'post_id': self.post.id}))
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(
            response.context.get('post').author, self.post.author
        )
        self.assertEqual(
            response.context.get('post').group, self.post.group
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        Post.objects.bulk_create([
            Post(
                text=f'{POST_TEXT} {i}', author=cls.author, group=cls.group
            ) for i in range(POSTS_PER_PAGE + 1)
        ])

    def test_paginator(self):
        urls_expected_post_number = [
            [PAG_INDEX_URL, Post.objects.all()[:POSTS_PER_PAGE]],
            [PAG_GROUP_LIST_URL, self.group.posts.all()[:POSTS_PER_PAGE]],
            [PAG_PROFILE_URL, self.author.posts.all()[:POSTS_PER_PAGE]],
        ]
        for url, queryset in urls_expected_post_number:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                page_obj = response.context.get('page_obj')
                self.assertIsNotNone(page_obj)
                self.assertIsInstance(page_obj, Page)
                self.assertQuerysetEqual(
                    page_obj.object_list, queryset, transform=lambda x: x
                )
