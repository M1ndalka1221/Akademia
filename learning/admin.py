from django.contrib import admin
from learning.models import Essay, Feedback, Topic, Vocabulary


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin configuration for essay Topics."""
    list_display = ("id", "title", "is_custom", "user", "created_at")
    list_filter = ("is_custom", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(Essay)
class EssayAdmin(admin.ModelAdmin):
    """Admin configuration for written Essays."""
    list_display = ("id", "topic_title", "user", "created_at", "content_snippet")
    list_filter = ("created_at", "topic")
    search_fields = ("content", "topic__title")
    ordering = ("-created_at",)

    @admin.display(description="Temat")
    def topic_title(self, obj: Essay) -> str:
        return obj.topic.title

    @admin.display(description="Skrót treści")
    def content_snippet(self, obj: Essay) -> str:
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin configuration for AI Feedback."""
    list_display = ("id", "essay_id", "essay_topic", "created_at")
    search_fields = ("corrected_text", "essay__content", "essay__topic__title")
    ordering = ("-created_at",)

    @admin.display(description="Temat eseju")
    def essay_topic(self, obj: Feedback) -> str:
        return obj.essay.topic.title


@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    """Admin configuration for C1 Vocabulary items."""
    list_display = ("id", "word", "translation", "level", "is_custom", "user", "created_at")
    list_filter = ("level", "is_custom", "created_at")
    search_fields = ("word", "translation", "example_sentence")
    ordering = ("-created_at", "word")


