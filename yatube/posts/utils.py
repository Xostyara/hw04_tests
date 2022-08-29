from django.core.paginator import Paginator
from django.conf import settings


# Выносим Пагинацию отдельно
def paginate_page(request, post_list):
    """Функция пагинации постов"""
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем и возвращаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)
