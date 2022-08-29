from time import sleep
 
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
 
from ..forms import PostForm
 
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
        cls.test_post = Post.objects.create(
            author=cls.user,
            text="test test",
            group=cls.group
        )
        #cls.client = Client()
        #cls.client.force_login(cls.user)
 
    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)
 
    def check_page_obj_at_context(self, response):
        """Эта функция является частью простого контекстного тестирования.
        Она создана для того, что бы не создавать повторяющиеся конструкции"""
        first_object_post = response.context.get("page_obj")[0]
 
        self.assertEqual(first_object_post.author.username, "TestUser")
        self.assertEqual(first_object_post.text, "test test")
        self.assertEqual(first_object_post.group.title, "Тестовое название")
 
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
                kwargs={"post_id": self.test_post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.test_post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ): "posts/profile.html",
        }
        for url, template in names_templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
 
                self.assertTemplateUsed(response, template)
 
    def test_index_correct_context(self):
        response = self.client.get(reverse("posts:index"))
 
        self.check_page_obj_at_context(response)
 
    def test_post_create_correct_context(self):
        response = self.client.get(reverse("posts:post_create"))
        form_obj = response.context.get("form")
        form_field_types = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
        }
        for field, expected_type in form_field_types.items():
            with self.subTest(field=field):
                field_type = form_obj.fields.get(field)
 
                self.assertIsInstance(field_type, expected_type)
        self.assertIsInstance(form_obj, PostForm)
 
    def test_group_posts_correct_context(self):
        response = self.client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            )
        )
        group_obj = response.context.get("group")
 
        self.assertEqual(group_obj, Group.objects.get(id=1))
        self.check_page_obj_at_context(response)
 
    def test_post_detail_correct_context(self):
        response = self.client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.test_post.id}
            )
        )
        post_obj = response.context.get("post")
        self.assertEqual(post_obj, self.test_post)
        
 
    def test_post_edit_correct_context(self):
        response = self.client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.test_post.id}
            )
        )
        post_obj = response.context.get("post")
        is_edit_flag = response.context.get("is_edit")
        form_obj = response.context.get("form")
 
        form_group = form_obj["group"].__getitem__(1).choice_label
        form_text = form_obj["text"].value()
        expected_fields = {
            "group": "Тестовое название",
            "text": "test test",
        }
 
        self.assertEqual(post_obj, self.test_post)
        self.assertEqual(is_edit_flag, True)
 
        self.assertIsInstance(form_obj, PostForm)
        self.assertEqual(form_group, expected_fields.get("group"))
        self.assertEqual(form_text, expected_fields.get("text"))
 
    def test_profile_use_correct_context(self):
        response = self.client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )
        #user_obj = response.context.get("username")
 
        #self.assertEqual(user_obj, self.user)
        self.check_page_obj_at_context(response)
 
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
                response = self.client.get(url)
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
        for i in range(15, 0, -1):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f"тестовый пост № {i}"
            )
            # задержка при создании
            sleep(1E-6)
 
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
        for url in urls:
            with self.subTest(url=url):
                for page in (1, 2):
                    response = self.client.get(f"{url}?page={page}")
                    page_obj = response.context.get("page_obj")
 
                    self.assertEqual(
                        len(page_obj),
                        settings.POSTS_PER_PAGE if page == 1 else
                        Post.objects.count() - settings.POSTS_PER_PAGE
                    )