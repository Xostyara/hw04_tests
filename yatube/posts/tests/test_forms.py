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
            data={'text': 'Test post', 'group': TaskCreateFormTests.group.id},
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

        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Test post'
            ).exists()
        )
        # Получаем пост и проверяем все его проперти
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, TaskCreateFormTests.group) 
        
        # Подсчитаем количество записей в Post
        self.assertEqual(Post.objects.count(), 1)

        def test_auth_user_can_edit_his_post(self):
            pass
        def test_unauth_user_cant_publish_post(self):
            pass