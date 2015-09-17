from django.db import models


class CommentManager(models.Manager):
    def comments_count(self, content_type, object_id):
        return self.get_queryset().filter(content_type=content_type, object_id=object_id).count()
