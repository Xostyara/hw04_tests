# Каждый логический набор тестов — это класс,
# который наследуется от базового класса TestCase
from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание записи в тестовой БД для проверки
        cls.user = User.objects.create_user(username='TestUserNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.auth_user = User.objects.create_user(username='TestUser')
        cls.authorized_client.force_login(cls.user)
        cls.post_author = User.objects.create_user(username='Post_author')
        cls.post_author_client = Client()
        cls.post_author_client.force_login(cls.post_author)

    def setUp(self) -> None:
        # Объявляем гостевой клиент
        self.guest_client = PostsURLTests.guest_client

        # Объявляем пользователя
        self.auth_user = PostsURLTests.user
        # Авторизуем пользователя
        self.authorized_client = PostsURLTests.authorized_client

        # Авторизуем автора поста
        self.post_author_client = PostsURLTests.post_author

    def test_urls_status_code(self):
        """Проверка общедоступных страниц"""
        url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        ]
        for urls in url_names:
            with self.subTest(urls):
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_avaliable_to_authorized(self):
        """Проверка доступности страниц авторизованным пользователям"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_code_404_aut(self):
        """Проверка, что несуществующая страница вернет ошибку 404"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template_guest_user(self):
        """URL-адрес использует соответствующий
        шаблон для всех пользователей."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_edit_posts_author_user(self):
        """Проверка редактирования поста автором"""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
