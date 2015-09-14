from django import template
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from comments.utils import annotate_comment_tree


register = template.Library()


class BaseCommentNode(template.Node):
    def __init__(self, obj=None, obj_id=None, as_varname=None):
        self.obj = template.Variable(obj)
        self.as_varname = as_varname

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.split_contents()

        if len(tokens) == 5:
            if tokens[1] != 'for':
                raise template.TemplateSyntaxError('Second argument in {0} tag must be "for".'.format(tokens[0]))
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError('Fourth argument in {0} must be "as".'.format(tokens[0]))

            return cls(obj=tokens[2], as_varname=tokens[4])

        template.TemplateSyntaxError('Tag {0} takes 5 arguments.'.format(tokens[0]))

    def render(self, context):
        qs = self.get_queryset(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''

    def get_queryset(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return None

        content_type = ContentType.objects.get_for_model(obj)

        return Comment.objects.filter(content_type=content_type, object_id=obj.pk)

    def get_context_value_from_queryset(self, context):
        raise NotImplementedError


class CommentListNode(BaseCommentNode):
    """
    Insert a list of comments into the context.

    """

    def get_context_value_from_queryset(self, context, qs):
        return list(qs)


@register.tag
def get_comment_list(parser, token):
    return CommentListNode.handle_token(parser, token)


@register.filter
def annotate_tree(comments):
    return annotate_comment_tree(comments)


@register.simple_tag
def comments_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.id).count()
