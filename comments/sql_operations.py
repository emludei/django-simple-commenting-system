from django.db import connection


def remove_pk_from_path_tree(using, pk, path):
    with connection[using].cursor() as cursor:
        cursor.execute(
            'UPDATE comments_comment SET path=array_remove(path, %s) WHERE path @> %s',
            [pk, path]
        )