# backend_community_homework

[![CI](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw03_forms/actions/workflows/python-app.yml)
# yatube_project
Социальная сеть блогеров

### Описание
Благодаря этому проекту я буду учиться разработке на Django! и мы создадим социальную сеть для блогеров
### Технологии
Python 3.7
Django 2.2.19
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение из папки с проектом
python -m venv venv
```
source venv/Scripts/Activate
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt

дополнительно необходимо обновить pytest!
pip install pytest==6.2.5
``` 
инструмент для проверки покрытия тестами
pip3 install coverage 
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
```



# Указание настроек для работы программного клиента (для тестирования) в файле settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    'testserver',
]
Локальный сервер:
127.0.0.1:8000/index
### Авторы
Xostyara