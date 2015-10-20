import json

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext

from comments.forms import CommentForm
from comments.models import Comment


RENDER_COMMENT = getattr(settings, 'RENDER_COMMENT', 'comments/render_comment.html')
ALERTS_COMMENT = getattr(settings, 'ALERTS_COMMENT', 'comments/alert.html')
REMOVED_COMMENT = getattr(settings, 'REMOVED_COMMENT', 'comments/removed_comment_data.html')
REMOVED_COMMENT_TREE = getattr(settings, 'REMOVED_COMMENT_TREE', 'comments/render_removed_comment_tree.html')

ALERTS = {
    'alert_not_ajax': _('Ajax requests are only supported.'),
    'alert_not_post': _('You can add comment only using POST query.'),
    'comment_not_exist': _('Comment with such id ({0}) does not exist.')
}


def json_error_response(error_message):
    return HttpResponse(json.dumps({'success': False, 'error_message': error_message}))


def render_comment(request, comment=None, template=REMOVED_COMMENT):
    addition = {}

    if comment is not None:
        addition['comment'] = comment

    context = RequestContext(request, addition)
    return render_to_string(template, context)


class BaseCommentView(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return render(request, ALERTS_COMMENT, {'alert': ALERTS['alert_not_ajax']})
        return json_error_response(str(ALERTS['alert_not_post']))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseCommentView, self).dispatch(request, *args, **kwargs)

    def render_alert_not_ajax(self, request):
        return render(request, ALERTS_COMMENT, {'alert': ALERTS['alert_not_ajax']})


class AddComment(BaseCommentView):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return render(request, ALERTS_COMMENT, {'alert': ALERTS['alert_not_ajax']})

        parent = request.POST.get('parent', None)
        comment = request.POST.get('comment')
        object_id = request.POST.get('object_id')
        model = self.kwargs.get('model')
        content_type = ContentType.objects.get_for_model(model)

        data = {
            'object_id': object_id,
            'content_type': content_type.pk,
            'user': request.user.pk,
            'parent': parent,
            'comment': comment
        }

        form = CommentForm(data)

        if form.is_valid():
            comment = form.save()

            # after form.save comment.path is None...
            comment = Comment.objects.get(pk=comment.id)
            rendered_comment = render_comment(request, comment, RENDER_COMMENT)

            response = json.dumps({
                'success': True,
                'parent': comment.parent.pk if comment.parent else None,
                'comment': rendered_comment
            })

            return HttpResponse(response)

        else:
            return json_error_response(form.errors)


class RemoveComment(BaseCommentView):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self.render_alert_not_ajax(request)

        comment_id = self.request.POST.get('comment_id', None)

        try:
            Comment.objects.remove_comment(comment_id)
            rendered_comment = render_comment(request)
        except (ObjectDoesNotExist, ValueError):
            return json_error_response(str(ALERTS['comment_not_exist']).format(comment_id))

        return HttpResponse(json.dumps({
            'success': True,
            'message': str(_('Comment successfully removed.')),
            'comment_id': comment_id,
            'comment': rendered_comment
        }))


class RemoveCommentTree(BaseCommentView):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return self.render_alert_not_ajax(request)

        parent_id = self.request.POST.get('parent_id', None)

        try:
            comments = Comment.objects.remove_comment_tree(parent_id)
            replace_data = render_comment(request, comments, REMOVED_COMMENT_TREE)
        except (ObjectDoesNotExist, ValueError):
            return json_error_response(str(ALERTS['comment_not_exist']).format(parent_id))

        return HttpResponse(json.dumps({
            'success': True,
            'message': str(_('Comments tree successfully removed.')),
            'parent_id': parent_id,
            'replace_data': replace_data,
            'list_id': [comment.id for comment in comments]
        }))
