# Импортируем CreateView, чтобы создать ему наследника
from django.views.generic import CreateView

# Функция reverse_Lazy позволяет получить URL по параметрам функции path()
# Берем, тоже пригодится
from django.urls import reverse_lazy

# Импортируем класс формы, чтобы сослаться на нее во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
