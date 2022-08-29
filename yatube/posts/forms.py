# Импортируем модуль forms, из него возьмём класс ModelForm
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {"text": "Текст", "group": "Группа"}
        help_texts = {
            "text": "Текст нового поста",
            "group": "Группа, к которой будет относиться пост",
        }
