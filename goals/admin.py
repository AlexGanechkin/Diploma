from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from goals.models import GoalCategory, GoalComment, Goal


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user")
    readonly_fields = ("created", "updated")
    list_filter = ["is_deleted"]
    search_fields = ("title", "user")


class CommentsInLine(admin.StackedInline):
    model = GoalComment
    extra = 0


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author_link")
    readonly_fields = ("created", "updated")
    search_fields = ("title", "description")
    list_filter = ("status", "priority")
    inlines = [CommentsInLine]

    def author_link(self, obj: Goal) -> str:
        return format_html(
            "<a href='{url}'>{user_name}</a>",
            url=reverse('admin:core_user_change', kwargs={'object_id': obj.user_id}),
            user_name=obj.user.username
        )
    author_link.short_description = 'Автор'


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("text", "author_link")
    search_fields = ("text",)

    def author_link(self, obj: GoalComment) -> str:
        return format_html(
            "<a href='{url}'>{user_name}</a>",
            url=reverse('admin:core_user_change', kwargs={'object_id': obj.user_id}),
            user_name=obj.user.username
        )
    author_link.short_description = 'Автор'
