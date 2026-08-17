"""
Views for the Learning application.

Implements Class-Based Views for Topic list, Essay submission, and AI Feedback view.
"""

from typing import Any, Dict
from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from learning.forms import EssayForm
from learning.models import Essay, Feedback, Topic
from services.llm_analyzer import LLMAnalysisError, LLMAnalyzer


class TopicListView(ListView):
    """View to list all available essay topics."""

    model = Topic
    template_name = "learning/topic_list.html"
    context_object_name = "topics"
    paginate_by = 10


class EssayCreateView(CreateView):
    """View to write and submit an essay for a specific topic."""

    model = Essay
    form_class = EssayForm
    template_name = "learning/essay_form.html"

    def get_topic(self) -> Topic:
        """Retrieve topic from URL parameter topic_id."""
        return get_object_or_404(Topic, pk=self.kwargs["topic_id"])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Inject topic object into template context."""
        context = super().get_context_data(**kwargs)
        context["topic"] = self.get_topic()
        return context

    def form_valid(self, form: EssayForm) -> HttpResponseRedirect:
        """
        Process valid form submission:
        1. Save Essay model with associated topic.
        2. Evaluate essay content using LLMAnalyzer service.
        3. Create Feedback model instance.
        4. Redirect to FeedbackDetailView.
        """
        topic: Topic = self.get_topic()
        essay: Essay = form.save(commit=False)
        essay.topic = topic
        essay.save()

        analyzer = LLMAnalyzer()

        try:
            analysis_results: Dict[str, Any] = analyzer.analyze_essay(essay.content)
            
            feedback = Feedback.objects.create(
                essay=essay,
                corrected_text=analysis_results.get("corrected_text", essay.content),
                feedback_json=analysis_results
            )
            messages.success(self.request, "Esej został pomyślnie przeanalizowany przez AI!")

        except LLMAnalysisError as exc:
            messages.error(
                self.request,
                f"Wystąpił błąd podczas analizy AI: {str(exc)}. Esej został zapisany."
            )
            # Create a fallback Feedback instance so user can view saved essay
            feedback = Feedback.objects.create(
                essay=essay,
                corrected_text=essay.content,
                feedback_json={
                    "corrected_text": essay.content,
                    "errors": [f"Błąd usługi analizy: {str(exc)}"],
                    "advanced_synonyms": []
                }
            )

        return HttpResponseRedirect(
            reverse("learning:feedback-detail", kwargs={"pk": feedback.pk})
        )


class FeedbackDetailView(DetailView):
    """View to display AI evaluation feedback for a specific essay."""

    model = Feedback
    template_name = "learning/feedback_detail.html"
    context_object_name = "feedback"
