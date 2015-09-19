from django.db import models


class CommentManager(models.Manager):
    def comments_count(self, content_type, object_id):
        return self.get_queryset().filter(content_type=content_type, object_id=object_id).count()

    def remove_comment(self, comment_id):
        self.get_queryset().filter(pk=comment_id).update(is_removed=True)

    def remove_comment_tree(self, parent_id):
        self.get_queryset().filter(path__contains=[parent_id]).update(is_removed=True)
