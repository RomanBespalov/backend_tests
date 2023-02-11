from http import HTTPStatus

from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests import constants as cs
from posts.forms import PostForm


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
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            cs.INDEX_TEMPLATE: reverse(cs.INDEX_URL),
            cs.GROUP_TEMPLATE: (
                reverse(cs.GROUP_URL, kwargs={'slug': self.group.slug})
            ),
            cs.PROFILE_TEMPLATE: (
                reverse(cs.PROFILE_URL, kwargs={'username': self.author})
            ),
            cs.POST_DETAIL_TEMPLATE: (
                reverse(cs.POST_DETAIL_URL, kwargs={'post_id': self.post.id})
            ),
            cs.POST_CREATE_TEMPLATE: reverse(cs.POST_CREATE_URL),
            cs.POST_EDIT_TEMPLATE: (
                reverse(cs.POST_EDIT_URL, kwargs={'post_id': self.post.id})
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
        cls.author = User.objects.create_user(username=AUTHOR_USERNAME)
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )

    def setUp(self):
        self.user = User.objects.create_user(username=USER_USERNAME)
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse(cs.POST_CREATE_URL))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.author_client.get(
            reverse(cs.POST_DETAIL_URL, kwargs={'post_id': self.post.id}))
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
                response_1 = self.client.get(url)
                response_2 = self.client.get(url, {'page': 2})
                self.assertEqual(response_1.status_code, HTTPStatus.OK)
                self.assertEqual(response_2.status_code, HTTPStatus.OK)
                page_obj_1 = response_1.context.get('page_obj')
                page_obj_2 = response_2.context.get('page_obj')
                self.assertIsNotNone(page_obj_1)
                self.assertIsNotNone(page_obj_2)
                self.assertIsInstance(page_obj_1, Page)
                self.assertIsInstance(page_obj_2, Page)
                self.assertQuerysetEqual(
                    page_obj_1.object_list, queryset, transform=lambda x: x
                )
                self.assertEqual(len(page_obj_2.object_list), 1)
