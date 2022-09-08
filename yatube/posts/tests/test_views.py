from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from ..forms import PostForm
from django.core.cache import cache

User = get_user_model()


class PostsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="TestUser"
        )
        cls.random_user = User.objects.create_user(
            username="RandomUser"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="Test-slug",
            title="Тестовое название"
        )
        cls.group_2 = Group.objects.create(
            description="Тестовое описание второй группы",
            slug="test-slug-group-2",
            title="Тестовое название второй группы"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test test",
            group=cls.group
        )

        # cls.client = Client()
        # cls.client.force_login(cls.user)

    def setUp(self):
        """Не забываем перед каждым тестом чистить кэш"""
        cache.clear()
        self.client = Client()
        self.auth_client = Client()
        self.user = PostsViewsTest.user
        self.auth_client.force_login(self.user)
        self.post = PostsViewsTest.post

    def check_context_contains_page_or_post(self, context, post=False):
        """Эта функция является частью простого контекстного тестирования.
        Она создана для того, что бы не создавать повторяющиеся конструкции"""
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostsViewsTest.user)
        self.assertEqual(post.pub_date, PostsViewsTest.post.pub_date)
        self.assertEqual(post.text, PostsViewsTest.post.text)
        self.assertEqual(post.group, PostsViewsTest.post.group)

    def test_view_funcs_correct_templates(self):
        """Проверка на использование корректного шаблона"""

        names_templates = {
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ): "posts/profile.html",
        }
        for url, template in names_templates.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.auth_client.get(reverse("posts:index"))
        self.check_context_contains_page_or_post(response.context)

    def test_group_posts_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            )
        )

        self.check_context_contains_page_or_post(response.context)
        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertEqual(group.title, PostsViewsTest.group.title)
        self.assertEqual(group.description, PostsViewsTest.group.description)

    def test_post_detail_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            )
        )
        self.check_context_contains_page_or_post(response.context, post=True)
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], PostsViewsTest.user)

    def test_post_edit_correct_context(self):
        response = self.auth_client.get(reverse("posts:post_create"))
        response_1 = self.auth_client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}
            )
        )
        form_obj = response.context.get("form")
        # #Поля формы проверять не нужно
        # # form_field_types = {
        #     "group": forms.fields.ChoiceField,
        #     "text": forms.fields.CharField,
        # }
        # for field, expected_type in form_field_types.items():
        #     with self.subTest(field=field):
        #         field_type = form_obj.fields.get(field)

        # self.assertIsInstance(field_type, expected_type)
        self.assertIsInstance(form_obj, PostForm)
        is_edit_flag = response.context.get("is_edit")
        is_edit_flag_1 = response_1.context.get("is_edit")
        self.assertEqual(is_edit_flag, False)
        self.assertEqual(is_edit_flag_1, True)

    def test_profile_use_correct_context(self):
        response = self.auth_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )
        self.check_context_contains_page_or_post(response.context)

    def test_post_created_at_right_group_and_profile(self):
        """Тестовый пост создан не в той группе и профиле"""
        urls = (
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group_2.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.random_user.username}
            )
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                page_obj = response.context.get("page_obj")

                self.assertEqual(len(page_obj), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="qwerty"
        )
        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="test-slug",
            title="Тестовое название"
        )
        posts = [
            Post(
                text=f'text {num}', author=cls.user,
                group=cls.group
            ) for num in range(1, 14)
        ]
        Post.objects.bulk_create(posts)

        cls.client = Client()

    def test_templates_paginator(self):
        urls = (
            reverse(
                "posts:index"
            ),
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ),
        )
        pages = [
            (1, settings.POSTS_PER_PAGE),
            (2, Post.objects.count() - settings.POSTS_PER_PAGE),
        ]
        for url in urls:
            with self.subTest(url=url):

                for page, expected_count in pages:
                    response = self.client.get(f"{url}?page={page}")
                    page_obj = response.context.get("page_obj")

                    self.assertEqual(
                        len(page_obj),
                        expected_count
                    )

        # # Второй вариант цикла            
        # for url in urls:
        #     with self.subTest(url=url):
        #         for page in (1, 2):
        #             response = self.client.get(f"{url}?page={page}")
        #             page_obj = response.context.get("page_obj")

        #             self.assertEqual(
        #                 len(page_obj),
        #                 settings.POSTS_PER_PAGE if page == 1 else
        #                 Post.objects.count() - settings.POSTS_PER_PAGE
        #             )
