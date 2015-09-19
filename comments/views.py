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

from comments.forms import CommentForm


RENDER_COMMENT = getattr(settings, 'RENDER_COMMENT', 'comments/render_comment.html')
ALERTS_COMMENT = getattr(settings, 'ALERTS_COMMENT', 'comments/alert.html')

ALERTS = {
    'alert_not_ajax': _('Ajax requests are only supported.'),
    'alert_not_post': _('You can add comment only using POST query.')
}


def json_error_response(error_message):
    return HttpResponse(json.dumps({'success': False, 'error_message': error_message}))


class AddComment(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return render(request, ALERTS_COMMENT, {'alert': ALERTS['alert_not_post']})
        return json_error_response(ALERTS['alert_not_post'])

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return render(request, ALERTS_COMMENT, {'alert': ALERTS['alert_not_post']})

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
            rendered_comment = render_to_string(RENDER_COMMENT, {'comment': comment})

            response = json.dumps({
                'success': True,
                'parent': comment.parent.pk if comment.parent else None,
                'comment': rendered_comment
            })

            return HttpResponse(response)

        else:
            return json_error_response(form.errors)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AddComment, self).dispatch(request, *args, **kwargs)
