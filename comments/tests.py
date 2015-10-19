from django.db.models.loading import get_model
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.utils import six

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

        model = get_model(app_label, model_name)

    return model


class AddCommentVeiwTest(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('add_comment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ajax requests are only supported.')
