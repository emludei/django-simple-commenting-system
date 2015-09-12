from djnago.db import models


class CommentManager(models.Manager):
    def remove_tree(self, path):
        self.get_queryset().filter(path__contains=path).update(is_removed=True)

    def delete_tree(self, path):
        self.get_queryset().filter(path__contains=path).delete()