from ..forms import PostForm
from ..models import Post, Group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего slug
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test_slug',
                                         description='Тестовое описание')
        # в этом методе создаем только группу
        # cls.post = Post.objects.create(text='Первый пост', group=cls.group,
        #                                author=cls.user)

        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = TaskCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        # Создаем первый пост и проверяем статус запроса
        response = self.authorized_client.post(
            reverse('posts:profile',
                    kwargs={
                        'username': TaskCreateFormTests.user.username
                    }),
            data={
                'text': 'Test post',
                'group': TaskCreateFormTests.group.id
            },
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form_data = {
            'text': 'Test post',
            'group': TaskCreateFormTests.group.id,
            'author': TaskCreateFormTests.user
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={
                    'username': TaskCreateFormTests.user.username
                }
            )
        )

        # Получаем пост и проверяем все его проперти
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, TaskCreateFormTests.group)
        self.assertEqual(Post.objects.count(), 1)

        # def test_auth_user_can_edit_his_post(self):
        # pass

    def test_authorized_user_edit_post(self):
        # проверка редактирования записи авторизованным пользователем
        post = Post.objects.create(
            text='post_text',
            author=self.user
        )
        form_data = {
            'text': 'post_text_edit',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])

    def test_nonauthorized_user_create_post(self):
        # проверка создания записи не авторизованным пользователем
        form_data = {
            'text': 'non_auth_edit_text',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            ('/auth/login/?next=/create/')
        )
        self.assertEqual(Post.objects.count(), 0)
