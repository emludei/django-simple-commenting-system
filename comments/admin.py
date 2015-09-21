from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from comments.models import Comment


def remove_comments(modeladmin, request, queryset):
    queryset.update(is_removed=True)
remove_comments.short_description = _('To mark selected comments as removed')


class CommentTabularInline(admin.TabularInline):
    model = Comment
    extra = 0


class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['object_id', 'content_type']}),
        ('Content', {'fields': ['parent', 'user', 'comment']}),
        ('Meta', {'fields': ['is_removed']}),
    ]

    inlines = [
        CommentTabularInline,
    ]

    list_display = ('id', 'user', 'content_type', 'object_id', 'parent', 'is_removed', 'pub_date')
    list_filter = ('pub_date', 'is_removed')
    search_fields = ('comment', 'user__username', 'object_id')
    date_hierarchy = 'pub_date'
    ordering = ['-pub_date']
    raw_id_fields = ('user', 'parent')
    actions = [remove_comments]

admin.site.register(Comment, CommentAdmin)
