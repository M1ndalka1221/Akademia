"""
Models for the Learning domain of Akademia.

Includes essay topics, user essays, AI feedback, and vocabulary items.
"""

from typing import Any
from django.conf import settings
from django.db import models


class Topic(models.Model):
    """Represents an essay prompt or topic for Polish language practice."""

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="topics",
        help_text="User who created this topic (null for AI/system default topics)."
    )
    title: models.CharField = models.CharField(max_length=255)
    description: models.TextField = models.TextField(blank=True)
    is_custom: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Designates whether this topic was created by a user."
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self) -> str:
        return self.title


class Essay(models.Model):
    """Represents an essay written by a user in Polish."""

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="essays",
        help_text="User who wrote this essay (null for anonymous/guest submissions)."
    )
    topic: models.ForeignKey = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="essays"
    )
    content: models.TextField = models.TextField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Essay"
        verbose_name_plural = "Essays"

    def __str__(self) -> str:
        snippet: str = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"Essay on '{self.topic.title}': {snippet}"


class Feedback(models.Model):
    """Represents AI feedback generated for a user's essay."""

    essay: models.OneToOneField = models.OneToOneField(
        Essay,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    corrected_text: models.TextField = models.TextField()
    feedback_json: models.JSONField = models.JSONField(
        default=dict,
        help_text="Stores structured feedback including list of errors and suggested advanced synonyms."
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self) -> str:
        return f"Feedback for Essay #{self.essay_id}"


class Vocabulary(models.Model):
    """Represents saved Polish vocabulary words (C1 level) with Russian translations and usage examples."""

    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vocabularies",
        help_text="User who saved this vocabulary item (null for AI/system defaults)."
    )
    word: models.CharField = models.CharField(
        max_length=255,
        help_text="The Polish C1 word or phrase."
    )
    translation: models.CharField = models.CharField(
        max_length=255,
        help_text="Russian translation of the word."
    )
    example_sentence: models.TextField = models.TextField(
        blank=True,
        help_text="Example sentence illustrating usage in Polish."
    )
    level: models.CharField = models.CharField(
        max_length=10,
        default="C1",
        help_text="CEFR proficiency level (e.g., C1)."
    )
    is_custom: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Designates whether this word was created manually by a user."
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "word"]
        verbose_name = "Vocabulary"
        verbose_name_plural = "Vocabularies"

    def __str__(self) -> str:
        return f"{self.word} - {self.translation}"


def calculate_learning_streak(user: Any = None) -> int:
    """
    Calculate consecutive calendar days of learning activity (essays written, custom topics or vocabulary added).
    Returns integer number of days in current streak.
    """
    from datetime import date, timedelta
    from django.utils import timezone

    essay_qs = Essay.objects.all()
    vocab_qs = Vocabulary.objects.all()
    topic_qs = Topic.objects.filter(is_custom=True)

    if user and getattr(user, "is_authenticated", False):
        essay_qs = essay_qs.filter(user=user)
        vocab_qs = vocab_qs.filter(user=user)
        topic_qs = topic_qs.filter(user=user)

    essay_dates = set(essay_qs.values_list("created_at__date", flat=True))
    vocab_dates = set(vocab_qs.values_list("created_at__date", flat=True))
    topic_dates = set(topic_qs.values_list("created_at__date", flat=True))

    active_dates = essay_dates.union(vocab_dates).union(topic_dates)
    if not active_dates:
        return 0

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    if today in active_dates:
        current_date = today
    elif yesterday in active_dates:
        current_date = yesterday
    else:
        return 0

    streak = 0
    while current_date in active_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak

