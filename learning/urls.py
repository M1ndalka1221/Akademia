"""URL configuration for the learning application."""

from django.urls import path
from learning.views import (
    EssayCreateView,
    EssayListView,
    FeedbackDetailView,
    TopicCreateView,
    TopicListView,
    UserTopicListView,
    VocabularyCreateView,
    VocabularyDeleteView,
    VocabularyGenerateAIView,
    VocabularyListView,
)

app_name = "learning"

urlpatterns = [
    path("", TopicListView.as_view(), name="topic-list"),
    path("user-topics/", UserTopicListView.as_view(), name="user-topic-list"),
    path("essays/", EssayListView.as_view(), name="essay-list"),
    path("topic/new/", TopicCreateView.as_view(), name="topic-create"),
    path("topic/<int:topic_id>/essay/new/", EssayCreateView.as_view(), name="essay-create"),
    path("feedback/<int:pk>/", FeedbackDetailView.as_view(), name="feedback-detail"),
    path("vocabulary/", VocabularyListView.as_view(), name="vocabulary-list"),
    path("vocabulary/new/", VocabularyCreateView.as_view(), name="vocabulary-create"),
    path("vocabulary/generate/", VocabularyGenerateAIView.as_view(), name="vocabulary-generate"),
    path("vocabulary/<int:pk>/delete/", VocabularyDeleteView.as_view(), name="vocabulary-delete"),
]


