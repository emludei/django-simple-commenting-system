from django.conf.urls import url

from .models import TestCommentedObject

from comments import views as comment_views


urlpatterns = [
    url(r'^addcomment/$', comment_views.AddComment.as_view(), {'model': TestCommentedObject}, name='add_comment'),
    url(r'^removecomment/$', comment_views.RemoveComment.as_view(), name='remove_comment'),
    url(r'^removecomment_tree/$', comment_views.RemoveCommentTree.as_view(), name='remove_comment_tree'),
]
