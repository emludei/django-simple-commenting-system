from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from comments import Comment


COMMENTS_MAX_LENGTH = getattr(settings, 'COMMENTS_MAX_LENGTH', 6000)


class CommentForm(forms.ModelForm):
    comment = forms.CharField(_('Comment'), widget=forms.Textarea, max_length=COMMENTS_MAX_LENGTH)

    class Meta:
        model = Comment
        fields = ['content_type', 'object_id', 'user', 'comment', 'parent']
