from django.conf import settings
from django import template
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.template import RequestContext

from comments.models import Comment
from comments.utils import annotate_comment_tree
from comments.models import COMMENTS_MAX_DEPTH


register = template.Library()


RENDER_COMMENT_TREE = getattr(settings, 'RENDER_COMMENT_TREE', 'comments/render_comment_tree.html')


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
        context[self.as_varname] = self.get_context_value_from_queryset(qs)
        return ''

    def get_queryset(self, context):
        ctype, object_id = self.get_ctype_and_pk(context)
        if object_id:
            return Comment.objects.filter(content_type=ctype, object_id=object_id)

        return Comment.objects.none()

    def get_ctype_and_pk(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return None, None

        return ContentType.objects.get_for_model(obj), obj.pk

    def get_context_value_from_queryset(self):
        raise NotImplementedError


class CommentListNode(BaseCommentNode):
    """
    Insert a list of comments into the context.

    """

    def get_context_value_from_queryset(self, qs):
        return list(qs)


class RenderCommentListNode(CommentListNode):
    """
    Render comment list for object.
    Usage: {% render_comment_list for <object> %}

    """

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.split_contents()

        if len(tokens) == 3:
            if tokens[1] != 'for':
                template.TemplateSyntaxError('Secont argument in {0} tag must be "for".'.format(tokens[0]))

            return cls(obj=tokens[2])

        template.TemplateSyntaxError('Tag {0} takes 3 arguments.'.format(tokens[0]))

    def render(self, context):
        ctype, object_id = self.get_ctype_and_pk(context)
        if object_id:
            qs = self.get_queryset(context)
            context['comment_list'] = self.get_context_value_from_queryset(qs)

            rendered_comment_list = render_to_string(
                RENDER_COMMENT_TREE,
                context
            )

            return rendered_comment_list
        else:
            return ''


@register.tag
def get_comment_list(parser, token):
    return CommentListNode.handle_token(parser, token)


@register.tag
def render_comment_list(parser, token):
    return RenderCommentListNode.handle_token(parser, token)


@register.simple_tag
def comments_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.id).count()


@register.simple_tag
def comment_max_depth():
    return COMMENTS_MAX_DEPTH


@register.filter
def annotate_tree(comments):
    return annotate_comment_tree(comments)
