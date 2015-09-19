from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _


from comments.managers import CommentManager


COMMENTS_MAX_DEPTH = getattr(settings, 'COMMENTS_MAX_DEPTH', 10)

# maximum length of "path" array (in database)...
MAX_LENGTH_OF_COMMENT_TREE = getattr(settings, 'MAX_LENGTH_OF_COMMENT_TREE', None)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='author', verbose_name=_('User'))
    content_type = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    object_id = models.PositiveIntegerField(verbose_name=_('Object ID'))
    obj = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField(verbose_name=_('Comment'))
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
        return min(len(self.path), COMMENTS_MAX_DEPTH)

    @property
    def root_id(self):
        return self.path[0]

    def save(self, *args, **kwargs):
        skip_build_tree = kwargs.pop('skip_build_tree', False)
        super(Comment, self).save(*args, **kwargs)
        if skip_build_tree:
            return None

        tree_path = []

        if self.parent:
            tree_path.extend(self.parent.path)

        if MAX_LENGTH_OF_COMMENT_TREE is None:
            tree_path.append(self.id)
        else:
            if len(tree_path) < MAX_LENGTH_OF_COMMENT_TREE:
                tree_path.append(self.id)
            else:
                tree_path[-1] = self.id

        Comment.objects.filter(pk=self.pk).update(path=tree_path)

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
