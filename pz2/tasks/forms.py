from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=[
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
        ],
        label='Срок выполнения',
        help_text='Укажите плановую дату и время завершения задачи',
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'completed']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'due_date': 'Срок выполнения',
            'priority': 'Приоритет',
            'completed': 'Выполнено',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
