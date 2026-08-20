from typing import Any, Dict
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from learning.forms import EssayForm, TopicForm, VocabularyForm
from learning.models import Essay, Feedback, Topic, Vocabulary
from services.llm_analyzer import LLMAnalysisError, LLMAnalyzer


class TopicListView(ListView):
    """View to list default / AI-generated essay topics."""

    model = Topic
    template_name = "learning/topic_list.html"
    context_object_name = "topics"
    paginate_by = 10

    def get_queryset(self):
        """Return only non-custom (AI) topics."""
        return Topic.objects.filter(is_custom=False)


class UserTopicListView(ListView):
    """View to list user-created custom essay topics (UsersEssays)."""

    model = Topic
    template_name = "learning/user_topic_list.html"
    context_object_name = "topics"
    paginate_by = 10

    def get_queryset(self):
        """Return only user-created custom topics."""
        return Topic.objects.filter(is_custom=True)


class TopicCreateView(CreateView):
    """View for users to add a custom essay topic."""

    model = Topic
    form_class = TopicForm
    template_name = "learning/topic_form.html"

    def form_valid(self, form: TopicForm) -> HttpResponseRedirect:
        """Save custom topic with is_custom=True and redirect to write an essay."""
        topic: Topic = form.save(commit=False)
        topic.is_custom = True
        topic.save()
        messages.success(
            self.request,
            f"Pomyślnie dodano własny temat: '{topic.title}'. Teraz możesz napisać esej!"
        )
        return HttpResponseRedirect(
            reverse("learning:essay-create", kwargs={"topic_id": topic.pk})
        )


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


class EssayListView(ListView):
    """View to list all written essays stored in the database."""

    model = Essay
    template_name = "learning/essay_list.html"
    context_object_name = "essays"
    paginate_by = 10

    def get_queryset(self):
        """Return all written essays ordered by creation date with related topic and feedback."""
        return Essay.objects.select_related("topic", "feedback").order_by("-created_at")


class VocabularyListView(ListView):
    """View to browse C1 level Polish vocabulary items with Russian translations."""

    model = Vocabulary
    template_name = "learning/vocabulary_list.html"
    context_object_name = "vocabularies"
    paginate_by = 12

    def get_queryset(self):
        """Filter vocabulary by search query 'q' and source filter ('ai', 'custom', 'all')."""
        queryset = Vocabulary.objects.all().order_by("-created_at", "word")
        source = self.request.GET.get("source", "all")
        query = self.request.GET.get("q", "").strip()

        if source == "ai":
            queryset = queryset.filter(is_custom=False)
        elif source == "custom":
            queryset = queryset.filter(is_custom=True)

        if query:
            queryset = queryset.filter(
                Q(word__icontains=query) |
                Q(translation__icontains=query) |
                Q(example_sentence__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Inject summary statistics and active filter parameters into template context."""
        context = super().get_context_data(**kwargs)
        context["source_filter"] = self.request.GET.get("source", "all")
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["total_count"] = Vocabulary.objects.count()
        context["ai_count"] = Vocabulary.objects.filter(is_custom=False).count()
        context["custom_count"] = Vocabulary.objects.filter(is_custom=True).count()
        return context


class VocabularyCreateView(CreateView):
    """View for users to manually add a custom C1 Polish vocabulary item."""

    model = Vocabulary
    form_class = VocabularyForm
    template_name = "learning/vocabulary_form.html"
    success_url = reverse_lazy("learning:vocabulary-list")

    def form_valid(self, form: VocabularyForm) -> HttpResponseRedirect:
        """Save vocabulary item as custom (is_custom=True, level='C1')."""
        vocab: Vocabulary = form.save(commit=False)
        vocab.is_custom = True
        vocab.level = "C1"
        if self.request.user and self.request.user.is_authenticated:
            vocab.user = self.request.user
        vocab.save()
        self.object = vocab
        messages.success(
            self.request,
            f"Pomyślnie dodano własne słówko C1: '{vocab.word}' -> '{vocab.translation}'!"
        )
        return HttpResponseRedirect(self.get_success_url())


class VocabularyGenerateAIView(View):
    """View handler to trigger Gemini AI generation of new C1 Polish-Russian words."""

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        analyzer = LLMAnalyzer()
        try:
            items = analyzer.generate_c1_vocabulary(count=5)
            created_count = 0
            for item in items:
                _, created = Vocabulary.objects.get_or_create(
                    word=item["word"],
                    defaults={
                        "translation": item["translation"],
                        "example_sentence": item.get("example_sentence", ""),
                        "level": "C1",
                        "is_custom": False,
                        "user": request.user if request.user and request.user.is_authenticated else None
                    }
                )
                if created:
                    created_count += 1

            if created_count > 0:
                messages.success(
                    request,
                    f"✨ Gemini AI pomyślnie wygenerowało {created_count} nowych słówek C1 z tłumaczeniem na rosyjski!"
                )
            else:
                messages.info(
                    request,
                    "Gemini AI wygenerowało słówka, które znajdowały się już w bazie danych."
                )
        except LLMAnalysisError as exc:
            messages.error(
                request,
                f"Wystąpił błąd podczas generowania słownictwa przez AI: {str(exc)}"
            )

        return redirect("learning:vocabulary-list")


class VocabularyDeleteView(DeleteView):
    """View to delete a custom or unwanted vocabulary item."""

    model = Vocabulary
    success_url = reverse_lazy("learning:vocabulary-list")

    def form_valid(self, form: Any) -> HttpResponseRedirect:
        vocab = self.get_object()
        messages.info(self.request, f"Usunięto słówko: '{vocab.word}'.")
        return super().form_valid(form)


