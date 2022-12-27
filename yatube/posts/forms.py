from django.forms import ModelForm
from .models import Post
from .models import Comment


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = 'Группа не выбрана'

    class Meta:
        model = Post
        fields = ('group', 'image', 'text',)


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
