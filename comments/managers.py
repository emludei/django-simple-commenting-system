from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class CommentManager(models.Manager):
    def comments_count(self, content_type, object_id):
        return self.get_queryset().filter(content_type=content_type, object_id=object_id).count()

    def remove_comment(self, comment_id):
        comment_to_remove = self.get_queryset().filter(pk=comment_id)

        if not comment_to_remove:
            raise ObjectDoesNotExist('Comment with such id ({0}) does not exist.'.format(comment_id))

        comment_to_remove.update(is_removed=True)

        return comment_to_remove

    def remove_comment_tree(self, parent_id):
        comments_to_remove = self.get_queryset().filter(path__contains=[parent_id])

        if not comments_to_remove:
            raise ObjectDoesNotExist('Comments with such parent_id ({0}) does not exists.'.format(parent_id))

        comments_to_remove.update(is_removed=True)

        return comments_to_remove
