from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
            'image': 'Выберите изображение'
        }
        help_texts = {'text': 'Напишите Ваш пост'}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комметарий'}
        help_texts = {'text': 'Напишите Ваш комментарий'}
