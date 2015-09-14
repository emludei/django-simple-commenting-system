import json

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from comments.forms import CommentForm, COMMENTS_MAX_LENGTH


ALERTS = {
    'alert_not_ajax': 'Ajax requests are only supported.',
    'alert_not_post': 'Votes can only be made using POST query.',
    'content_max_length': 'Max comment length is {0}'.format(COMMENTS_MAX_LENGTH),
}


def json_error_response(error_message):
    return HttpResponse(json.dumps({'success': False, 'error_message': error_message}))


class AddComment(View):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return render(request, 'comments/alert.html', {'alert': ALERTS['alert_not_post']})
        return json_error_response(ALERTS['alert_not_post'])

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return json_error_response(ALERTS['alert_not_ajax'])

        parent = request.POST.get('parent', None)
        comment = request.POST.get('comment')
        object_id = self.kwargs.get('pk')
        model = self.kwargs.get('model')
        content_type = ContentType.objects.get_for_model(model)

        form = CommentForm(
            object_id=object_id,
            content_type=content_type,
            user=request.user,
            parent=parent,
            comment=comment
        )

        if form.is_valid():
            comment = form.save()

            response = json.dumps({
                'succes': True,
                'comment': {
                    'user': comment.user.username,
                    'pub_date': comment.pub_date,
                    'comment': comment.comment,
                    'parent': comment.parent
                }
            })

            return HttpResponse(response)

        else:
            return json_error_response(ALERTS['content_max_length'])

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        super(AddComment, self).dispatch(*args, **kwargs)
