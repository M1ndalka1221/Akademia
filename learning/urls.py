"""URL configuration for the learning application."""

from django.urls import path
from learning.views import EssayCreateView, FeedbackDetailView, TopicListView

app_name = "learning"

urlpatterns = [
    path("", TopicListView.as_view(), name="topic-list"),
    path("topic/<int:topic_id>/essay/new/", EssayCreateView.as_view(), name="essay-create"),
    path("feedback/<int:pk>/", FeedbackDetailView.as_view(), name="feedback-detail"),
]
