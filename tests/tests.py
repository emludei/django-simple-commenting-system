from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.utils import six

from comments.views import ALERTS
from . import models


# get auth user model

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', None)


def get_user_model(model):
    if model is None:
        from django.contrib.auth import User

        model = User
    elif isinstance(model, six.string_types):
        try:
            app_label, model_name = model.split('.')
        except ValueError as err:
            print(err)

        model = apps.get_model(app_label, model_name)

    return model


class AddCommentVeiwTest(TestCase):
    def setUp(self):
        self.url = reverse('add_comment')
        self.client = Client()
        self.username = 'test'
        self.password = 'test'
        self.email = 'test@test.test'

        self.test_user = get_user_model(
            AUTH_USER_MODEL
        ).objects.create_user(self.username, self.email, self.password)

        login = self.client.login(username=self.username, password=self.password)
        self.assertEqual(login, True)

    def test_get_not_ajax_query(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ALERTS['alert_not_ajax'])

    def test_get_ajax_query(self):
        response = self.client.get(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ALERTS['alert_not_post'])

    def test_post_not_ajax_query(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ALERTS['alert_not_ajax'])

    def test_post_ajax_query(self):
        data = {
            'parent': 1,
            'comment': 'test',
            'object_id': 2,
            'model': models.TestCommentedObject,
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
