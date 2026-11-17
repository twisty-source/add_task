from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'text']
        labels = {
            'title': 'Заголовок публикации',
            'text': 'Текст публикации',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введите заголовок...'}),
            'text': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Напишите текст вашей публикации...'}),
        }
