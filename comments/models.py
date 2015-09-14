from django.conf import settings
from django.db import models, router, transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _

from comments.sql_operations import remove_pk_from_path_tree
from comments.managers import CommentManager


COMMENTS_MAX_LENGTH = getattr('settings', 'COMMENTS_MAX_LENGTH', 6000)
COMMENTS_MAX_DEPTH = getattr('settings', 'COMMENTS_MAX_DEPTH', 10)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author', verbose_name=_('User'))
    content_type = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    object_id = models.PositiveIntegerField(verbose_name=_('Object ID'))
    obj = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField(verbose_name=_('Comment'), max_length=COMMENTS_MAX_LENGTH)
    pub_date = models.DateTimeField(verbose_name=_('Date'), auto_now_add=True)
    is_removed = models.BooleanField(verbose_name='Is removed', default=False)
    path = ArrayField(models.PositiveIntegerField(), null=True, editable=False)

    parent = models.ForeignKey(
        'self',
        verbose_name=_('Parent'),
        related_name='parent_for_comment',
        null=True,
        blank=True,
        default=None
    )

    objects = CommentManager()

    @property
    def depth(self):
        return len(self.path)

    @property
    def root_id(self):
        return self.path[0]

    @property
    def root_path(self):
        Comment.objects.filter(pk__in=self.path)

    def children(self):
        Comment.objects.filter(path__contains=self.path)

    def remove(self):
        self.is_removed = True
        self.save()

    def save(self, *args, **kwargs):
        skip_build_tree = kwargs.pop('skip_build_tree', False)
        super(Comment, self).save(*args, **kwargs)
        if skip_build_tree:
            return None

        tree_path = []

        if self.parent:
            tree_path.extend(self.parent.path)
            if len(self.parent.path) < COMMENTS_MAX_DEPTH:
                tree_path.append(self.id)
        else:
            tree_path.append(self.id)

        Comment.objects.filter(pk=self.pk).update(path=tree_path)

    def delete(self, *args, **kwargs):
        db = router.db_for_write(Comment)
        with transaction.atomic(using=db):
            if self.parent:
                Comment.objects.filter(
                    parent=self.pk,
                ).update(parent=self.parent)

            remove_pk_from_path_tree(db, self.pk, self.path)
            super(Comment, self).delete(*args, **kwargs)

    def __str__(self):
        return '<Comment: id {0}, user {1}, model {2}, object_id {3}>'.format(
            self.id,
            self.user.username,
            self.content_type,
            self.object_id
        )

    class Meta:
        ordering = ('path',)
        db_table = 'comments_comment'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
