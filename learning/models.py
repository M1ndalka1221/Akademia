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
    """Represents saved Polish vocabulary words with translations and usage examples."""

    word: models.CharField = models.CharField(
        max_length=255,
        help_text="The Polish word or phrase."
    )
    translation: models.CharField = models.CharField(
        max_length=255,
        help_text="Translation of the word."
    )
    example_sentence: models.TextField = models.TextField(
        blank=True,
        help_text="Example sentence illustrating usage."
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["word"]
        verbose_name = "Vocabulary"
        verbose_name_plural = "Vocabularies"

    def __str__(self) -> str:
        return f"{self.word} - {self.translation}"
