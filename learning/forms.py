"""Forms for the learning application."""

from typing import Any
from django import forms
from learning.models import Essay, Topic


class EssayForm(forms.ModelForm):
    """Form for writing and submitting Polish essays."""

    class Meta:
        model = Essay
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": (
                        "w-full p-4 border border-slate-300 dark:border-slate-700 rounded-xl "
                        "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                        "bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 "
                        "font-sans shadow-sm transition-all duration-200"
                    ),
                    "rows": 12,
                    "placeholder": "Napisz swój esej po polsku tutaj...",
                }
            ),
        }
        labels = {
            "content": "Treść Eseju (Essay Content)",
        }


class TopicForm(forms.ModelForm):
    """Form for creating user-defined custom essay topics."""

    class Meta:
        model = Topic
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": (
                        "w-full p-4 border border-slate-700 rounded-xl "
                        "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                        "bg-slate-900 text-slate-100 font-sans shadow-sm "
                        "placeholder-slate-500 transition-all duration-200"
                    ),
                    "placeholder": "Tytuł tematu (np. Rozwój technologii w XXI wieku)",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": (
                        "w-full p-4 border border-slate-700 rounded-xl "
                        "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                        "bg-slate-900 text-slate-100 font-sans shadow-sm "
                        "placeholder-slate-500 transition-all duration-200"
                    ),
                    "rows": 4,
                    "placeholder": "Opis tematu lub dodatkowe instrukcje (opcjonalnie)...",
                }
            ),
        }
        labels = {
            "title": "Tytuł Tematu (Topic Title)",
            "description": "Opis / Wskazówki (Topic Description)",
        }

