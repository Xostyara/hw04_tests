from ..forms import PostForm
from ..models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

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
        cls.post = Post.objects.create(text='Первый пост', group=cls.group,
                                       author=cls.user)

        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    def setUp(self):
        
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_task(self):
        """Валидная форма создает запись в Post."""
        # Подсчитаем количество записей в Post
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Первый пост',
            'group': TaskCreateFormTests.group.pk,
            'author': TaskCreateFormTests.user
        }
        # Отправляем POST-запрос
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': TaskCreateFormTests.user.username}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Первый пост'
            ).exists()
        )