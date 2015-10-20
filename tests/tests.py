from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.utils import six
from django.contrib.contenttypes.models import ContentType

from comments.views import ALERTS
from comments.forms import CommentForm
from . import models


# get auth user model

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', None)

# user data

COMMENTS_TEST_USER = getattr(
    settings,
    'COMMENTS_TEST_USER',
    {'username': 'test', 'email': 'test@test.test', 'password': 'test'}
)

# test data

COMMENTS_TEST_DATA = getattr(settings, 'COMMENTS_TEST_DATA', ['data.json', 'user_data.json'])


def _get_user_model(model):
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


def _get_user_or_create():
    user_model = _get_user_model(AUTH_USER_MODEL)

    try:
        test_user = user_model.objects.get(pk=1)
    except user_model.DoesNotExist:
        test_user = user_model.objects.create_user(
            COMMENTS_TEST_USER['username'],
            COMMENTS_TEST_USER['email'],
            COMMENTS_TEST_USER['password']
        )

    return test_user


class RemoveCommentsMixin:
    def test_remove_not_exist_comment(self):
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error_message')


class BaseViewTest:
    commented_object_model = models.TestCommentedObject
    fixtures = COMMENTS_TEST_DATA

    @classmethod
    def setUpTestData(cls):
        cls.commented_object = cls.commented_object_model.objects.create()
        cls.test_user = _get_user_or_create()

    def setUp(self):
        self.client = Client()

        login = self.client.login(
            username=COMMENTS_TEST_USER['username'],
            password=COMMENTS_TEST_USER['password']
        )

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


class AddCommentVeiwTest(BaseViewTest, TestCase):
    def setUp(self):
        self.url = reverse('add_comment')
        super(AddCommentVeiwTest, self).setUp()

    def test_post_ajax_query_valid(self):
        data = {
            'comment': 'test',
            'object_id': self.commented_object.id,
            'model': self.commented_object_model
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, 'error_message')

    def test_post_ajax_query_empty_comment(self):
        data = {
            'comment': '',
            'object_id': self.commented_object.id,
            'model': self.commented_object_model
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error_message')


class RemoveCommentViewTest(BaseViewTest, RemoveCommentsMixin, TestCase):
    def setUp(self):
        self.url = reverse('remove_comment')
        super(RemoveCommentViewTest, self).setUp()

    def test_remove_exist_comment(self):
        data = {
            'comment_id': 1
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'error_message')


class RemoveCommentTreeViewTest(BaseViewTest, RemoveCommentsMixin, TestCase):
    def setUp(self):
        self.url = reverse('remove_comment_tree')
        super(RemoveCommentTreeViewTest, self).setUp()

    def test_remove_exist_comment_tree(self):
        data = {
            'parent_id': 1
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'error_message')


class CommentFormTest(TestCase):
    commented_object_model = models.TestCommentedObject
    fixtures = COMMENTS_TEST_DATA

    @classmethod
    def setUpTestData(cls):
        cls.commented_object = cls.commented_object_model.objects.create()
        cls.content_type = ContentType.objects.get_for_model(cls.commented_object_model)
        cls.test_user = _get_user_or_create()

    def test_valid_form(self):
        data = {
            'object_id': self.commented_object.id,
            'content_type': self.content_type.id,
            'user': self.test_user.id,
            'parent': None,
            'comment': 'test'
        }

        form = CommentForm(data=data)

        self.assertTrue(form.is_valid())

    def test_invalid_form_no_object_id(self):
        data = {
            'content_type': self.content_type.id,
            'user': self.test_user.id,
            'parent': None,
            'comment': 'test'
        }

        form = CommentForm(data=data)

        self.assertFalse(form.is_valid())

    def test_invalid_form_not_exist_parent(self):
        data = {
            'object_id': self.commented_object.id,
            'content_type': self.content_type.id,
            'user': self.test_user.id,
            'parent': -1,
            'comment': 'test'
        }

        form = CommentForm(data=data)

        self.assertFalse(form.is_valid())

    def test_invalid_form_not_exist_content_type(self):
        data = {
            'object_id': self.commented_object.id,
            'content_type': -1,
            'user': self.test_user.id,
            'parent': None,
            'comment': 'test'
        }

        form = CommentForm(data=data)

        self.assertFalse(form.is_valid())

    def test_invalid_form_not_exist_user(self):
        data = {
            'object_id': self.commented_object.id,
            'content_type': self.content_type.id,
            'user': -1,
            'parent': None,
            'comment': 'test'
        }

        form = CommentForm(data=data)

        self.assertFalse(form.is_valid())

    def test_invalid_form_empty_comment(self):
        data = {
            'object_id': self.commented_object.id,
            'content_type': self.content_type.id,
            'user': self.test_user.id,
            'parent': None,
            'comment': ''
        }

        form = CommentForm(data=data)

        self.assertFalse(form.is_valid())
